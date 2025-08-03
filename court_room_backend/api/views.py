from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
import asyncio
import requests
import logging

from .models import Court, CaseType, CaseQuery, CaseDetail, CaseDocument
from .serializers import (
    CourtSerializer, CaseTypeSerializer, CaseQuerySerializer, 
    CaseSearchSerializer, CaseDetailSerializer
)
from court_room_backend.scrapers.ecourts_scraper import ECourtsScraper

logger = logging.getLogger(__name__)

class CourtListView(generics.ListAPIView):
    """List all available courts"""
    queryset = Court.objects.filter(is_active=True)
    serializer_class = CourtSerializer

class CaseTypeListView(generics.ListAPIView):
    """List case types for a specific court"""
    serializer_class = CaseTypeSerializer
    
    def get_queryset(self):
        court_id = self.request.query_params.get('court_id')
        if court_id:
            return CaseType.objects.filter(court_id=court_id)
        return CaseType.objects.all()

class CaseHistoryView(generics.ListAPIView):
    """View search history with pagination"""
    serializer_class = CaseQuerySerializer
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        queryset = CaseQuery.objects.all()
        
        # Filter by success status
        success = self.request.query_params.get('success')
        if success is not None:
            queryset = queryset.filter(success=success.lower() == 'true')
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(queried_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(queried_at__date__lte=date_to)
            
        return queryset

@api_view(['POST'])
def search_case(request):
    """
    Search for case details
    """
    serializer = CaseSearchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid input data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = serializer.validated_data
    court = get_object_or_404(Court, id=data['court_id'])
    case_type = get_object_or_404(CaseType, id=data['case_type_id'])
    
    # Get client IP
    client_ip = get_client_ip(request)
    
    # Create query record
    query = CaseQuery.objects.create(
        court=court,
        case_type=case_type,
        case_number=data['case_number'],
        filing_year=data['filing_year'],
        user_ip=client_ip
    )
    
    try:
        # Perform scraping
        scraper = ECourtsScraper()
        
        # Run async scraper in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                scraper.search_case(
                    court.id,
                    case_type.code,
                    data['case_number'],
                    data['filing_year']
                )
            )
        finally:
            loop.close()
        
        # Update query with results
        query.success = result['success']
        query.raw_response = result
        
        if not result['success']:
            query.error_message = result.get('error', 'Unknown error')
            query.save()
            
            return Response({
                'success': False,
                'error': result.get('error', 'Search failed'),
                'query_id': str(query.id)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Save case details if successful
        with transaction.atomic():
            case_data = result['data']['case_details']
            
            case_detail = CaseDetail.objects.create(
                query=query,
                cnr_number=case_data.get('cnr_number', ''),
                petitioner_name=case_data.get('petitioner_name', ''),
                respondent_name=case_data.get('respondent_name', ''),
                filing_date=case_data.get('filing_date'),
                next_hearing_date=case_data.get('next_hearing_date'),
                case_status=case_data.get('case_status', ''),
                court_hall=case_data.get('court_hall', ''),
                judge_name=case_data.get('judge_name', '')
            )
            
            # Save documents
            for doc_data in result['data']['documents']:
                CaseDocument.objects.create(
                    case_detail=case_detail,
                    document_type=doc_data.get('document_type', 'Document'),
                    document_date=doc_data.get('document_date'),
                    pdf_url=doc_data['pdf_url'],
                    file_name=doc_data.get('file_name', 'Document')
                )
        
        query.save()
        
        # Return formatted response
        response_serializer = CaseQuerySerializer(query)
        return Response({
            'success': True,
            'data': response_serializer.data,
            'query_id': str(query.id)
        })
        
    except Exception as e:
        logger.error(f"Error in case search: {str(e)}")
        query.success = False
        query.error_message = str(e)
        query.save()
        
        return Response({
            'success': False,
            'error': 'Internal server error',
            'query_id': str(query.id)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def download_pdf(request, document_id):
    """
    Download PDF document
    """
    try:
        document = get_object_or_404(CaseDocument, id=document_id)
        
        # If file is already downloaded locally, serve it
        if document.local_file_path and os.path.exists(document.local_file_path):
            with open(document.local_file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{document.file_name}.pdf"'
                return response
        
        # Otherwise, download from court server
        pdf_response = requests.get(document.pdf_url, timeout=30)
        
        if pdf_response.status_code == 200:
            # Save locally for future use
            import os
            from django.conf import settings
            
            media_dir = os.path.join(settings.MEDIA_ROOT, 'court_documents')
            os.makedirs(media_dir, exist_ok=True)
            
            filename = f"{document.id}_{document.file_name}.pdf"
            filepath = os.path.join(media_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(pdf_response.content)
            
            document.local_file_path = filepath
            document.downloaded = True
            document.save()
            
            response = HttpResponse(pdf_response.content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{document.file_name}.pdf"'
            return response
        else:
            return Response({
                'error': 'PDF not available from court server'
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        logger.error(f"Error downloading PDF: {str(e)}")
        return Response({
            'error': 'Error downloading PDF'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def case_detail(request, query_id):
    """
    Get detailed case information by query ID
    """
    try:
        query = get_object_or_404(CaseQuery, id=query_id)
        serializer = CaseQuerySerializer(query)
        return Response(serializer.data)
    except Exception as e:
        return Response({
            'error': 'Case not found'
        }, status=status.HTTP_404_NOT_FOUND)

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

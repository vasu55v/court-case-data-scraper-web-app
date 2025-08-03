from rest_framework import serializers
from .models import Court, CaseType, CaseQuery, CaseDetail, CaseDocument

class CourtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = ['id', 'name', 'location', 'is_active']

class CaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseType
        fields = ['id', 'name', 'code']

class CaseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseDocument
        fields = ['id', 'document_type', 'document_date', 'pdf_url', 'file_name']

class CaseDetailSerializer(serializers.ModelSerializer):
    documents = CaseDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = CaseDetail
        fields = [
            'cnr_number', 'petitioner_name', 'respondent_name',
            'filing_date', 'next_hearing_date', 'case_status',
            'court_hall', 'judge_name', 'documents'
        ]

class CaseQuerySerializer(serializers.ModelSerializer):
    case_detail = CaseDetailSerializer(read_only=True)
    court_name = serializers.CharField(source='court.name', read_only=True)
    case_type_name = serializers.CharField(source='case_type.name', read_only=True)
    
    class Meta:
        model = CaseQuery
        fields = [
            'id', 'court_name', 'case_type_name', 'case_number',
            'filing_year', 'queried_at', 'success', 'error_message',
            'case_detail'
        ]

class CaseSearchSerializer(serializers.Serializer):
    court_id = serializers.IntegerField()
    case_type_id = serializers.IntegerField()
    case_number = serializers.CharField(max_length=50)
    filing_year = serializers.CharField(max_length=4)
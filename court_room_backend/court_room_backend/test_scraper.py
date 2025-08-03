#!/usr/bin/env python
"""
Test script for eCourts scraper
Run: python manage.py shell < test_scraper.py
"""

import asyncio
import json
from api.models import Court, CaseType
from court_room_backend.scrapers.ecourts_scraper import ECourtsScraper

async def test_scraper():
    """Test the scraper with real court data"""
    
    print("=== TESTING ECOURTS SCRAPER ===\n")
    
    # Initialize scraper
    scraper = ECourtsScraper()
    
    # Test cases with real court data
    test_cases = [
        {
            'court_id': 6,  # Gujarat High Court
            'case_type': 'WP',  # Writ Petition
            'case_number': '12345',
            'filing_year': '2023',
            'description': 'Gujarat High Court - Writ Petition'
        },
        {
            'court_id': 5,  # Delhi High Court
            'case_type': 'CRL',  # Criminal
            'case_number': '6789',
            'filing_year': '2023',
            'description': 'Delhi High Court - Criminal Case'
        },
        {
            'court_id': 201,  # District Court Surat
            'case_type': 'CS',  # Civil Suit
            'case_number': '1001',
            'filing_year': '2024',
            'description': 'District Court Surat - Civil Suit'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['description']}")
        print(f"Court ID: {test_case['court_id']}")
        print(f"Case Type: {test_case['case_type']}")
        print(f"Case Number: {test_case['case_number']}")
        print(f"Filing Year: {test_case['filing_year']}")
        print("-" * 50)
        
        try:
            # Test the scraper
            result = await scraper.search_case(
                court_id=test_case['court_id'],
                case_type=test_case['case_type'],
                case_number=test_case['case_number'],
                filing_year=test_case['filing_year']
            )
            
            print("Result:")
            print(f"Success: {result.get('success', False)}")
            
            if result.get('success'):
                print("Case Data Found:")
                case_data = result.get('data', {}).get('case_details', {})
                for key, value in case_data.items():
                    print(f"  {key}: {value}")
                
                documents = result.get('data', {}).get('documents', [])
                if documents:
                    print(f"Documents Found: {len(documents)}")
                    for doc in documents[:2]:  # Show first 2 documents
                        print(f"  - {doc.get('document_type', 'Document')}: {doc.get('file_name', 'N/A')}")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
        
        print("\n" + "="*60 + "\n")
        
        # Add delay between tests
        await asyncio.sleep(2)

def test_database_setup():
    """Test if database is properly set up"""
    print("=== TESTING DATABASE SETUP ===\n")
    
    courts = Court.objects.all()
    print(f"Total Courts: {courts.count()}")
    
    if courts.exists():
        print("\nSample Courts:")
        for court in courts[:5]:
            case_types = CaseType.objects.filter(court=court)
            print(f"  {court.name} (ID: {court.id}) - {case_types.count()} case types")
            
            # Show some case types
            sample_types = case_types[:3]
            for ct in sample_types:
                print(f"    - {ct.name} ({ct.code})")
    
    print(f"\nTotal Case Types: {CaseType.objects.count()}")
    
    # Check specific courts that are important for testing
    important_courts = [5, 6, 201]  # Delhi HC, Gujarat HC, Surat District
    print("\nImportant Courts for Testing:")
    for court_id in important_courts:
        try:
            court = Court.objects.get(id=court_id)
            case_types = CaseType.objects.filter(court=court).count()
            print(f"  ✓ {court.name} (ID: {court_id}) - {case_types} case types")
        except Court.DoesNotExist:
            print(f"  ✗ Court ID {court_id} not found!")

def run_api_test():
    """Test the API endpoint"""
    print("=== TESTING API ENDPOINT ===\n")
    
    import requests
    import json
    
    # Test data
    test_data = {
        'court_id': 6,  # Gujarat High Court
        'case_type_id': None,  # Will be set below
        'case_number': '12345',
        'filing_year': '2023'
    }
    
    try:
        # Get a case type ID
        court = Court.objects.get(id=6)
        case_type = CaseType.objects.filter(court=court, code='WP').first()
        
        if case_type:
            test_data['case_type_id'] = case_type.id
            
            print(f"Testing API with data: {test_data}")
            
            # Make API request (assuming server is running on 8000)
            try:
                response = requests.post(
                    'http://127.0.0.1:8000/api/search-case/',
                    json=test_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"API Response Status: {response.status_code}")
                print(f"API Response: {response.json()}")
                
            except requests.exceptions.ConnectionError:
                print("API server not running. Start with: python manage.py runserver")
                
        else:
            print("No Writ Petition case type found for Gujarat High Court")
            
    except Court.DoesNotExist:
        print("Gujarat High Court not found in database")

    # Test database setup first
    test_database_setup()
    
    # Test scraper functionality
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(test_scraper())
    finally:
        loop.close()
    
    # Test API
    run_api_test()
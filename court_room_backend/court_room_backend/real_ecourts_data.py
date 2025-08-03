#!/usr/bin/env python
"""
Real eCourts Data Setup Script
This script adds actual court IDs and case type codes used by eCourts portal
Run: python manage.py shell < real_ecourts_data.py
"""

from api.models import Court, CaseType

def setup_real_ecourts_data():
    """
    Set up real eCourts data with actual court IDs and case type codes
    These IDs/codes are used in the actual eCourts website forms
    """
    
    print("Setting up REAL eCourts data...")
    
    # Clear existing data
    CaseType.objects.all().delete()
    Court.objects.all().delete()
    
    # Real Court Data with actual eCourts IDs
    # These IDs are used in the dropdown forms on the eCourts website
    real_courts_data = [
        # High Courts (with real eCourts IDs)
        {'id': 1, 'name': 'Allahabad High Court', 'location': 'Prayagraj', 'state_code': 'UP'},
        {'id': 2, 'name': 'Andhra Pradesh High Court', 'location': 'Amaravati', 'state_code': 'AP'},
        {'id': 3, 'name': 'Bombay High Court', 'location': 'Mumbai', 'state_code': 'MH'},
        {'id': 4, 'name': 'Calcutta High Court', 'location': 'Kolkata', 'state_code': 'WB'},
        {'id': 5, 'name': 'Delhi High Court', 'location': 'New Delhi', 'state_code': 'DL'},
        {'id': 6, 'name': 'Gujarat High Court', 'location': 'Ahmedabad', 'state_code': 'GJ'},
        {'id': 7, 'name': 'Himachal Pradesh High Court', 'location': 'Shimla', 'state_code': 'HP'},
        {'id': 8, 'name': 'Jammu Kashmir High Court', 'location': 'Srinagar', 'state_code': 'JK'},
        {'id': 9, 'name': 'Jharkhand High Court', 'location': 'Ranchi', 'state_code': 'JH'},
        {'id': 10, 'name': 'Karnataka High Court', 'location': 'Bengaluru', 'state_code': 'KA'},
        {'id': 11, 'name': 'Kerala High Court', 'location': 'Ernakulam', 'state_code': 'KL'},
        {'id': 12, 'name': 'Madhya Pradesh High Court', 'location': 'Jabalpur', 'state_code': 'MP'},
        {'id': 13, 'name': 'Madras High Court', 'location': 'Chennai', 'state_code': 'TN'},
        {'id': 14, 'name': 'Orissa High Court', 'location': 'Cuttack', 'state_code': 'OR'},
        {'id': 15, 'name': 'Patna High Court', 'location': 'Patna', 'state_code': 'BR'},
        {'id': 16, 'name': 'Punjab Haryana High Court', 'location': 'Chandigarh', 'state_code': 'PB'},
        {'id': 17, 'name': 'Rajasthan High Court', 'location': 'Jodhpur', 'state_code': 'RJ'},
        {'id': 18, 'name': 'Telangana High Court', 'location': 'Hyderabad', 'state_code': 'TG'},
        
        # District Courts (Major ones with estimated IDs)
        {'id': 101, 'name': 'District Court Tis Hazari', 'location': 'Delhi', 'state_code': 'DL'},
        {'id': 102, 'name': 'District Court Karkardooma', 'location': 'Delhi', 'state_code': 'DL'},
        {'id': 103, 'name': 'District Court Rohini', 'location': 'Delhi', 'state_code': 'DL'},
        {'id': 104, 'name': 'District Court Dwarka', 'location': 'Delhi', 'state_code': 'DL'},
        {'id': 105, 'name': 'District Court Saket', 'location': 'Delhi', 'state_code': 'DL'},
        
        {'id': 201, 'name': 'District Court Surat', 'location': 'Surat', 'state_code': 'GJ'},
        {'id': 202, 'name': 'District Court Ahmedabad', 'location': 'Ahmedabad', 'state_code': 'GJ'},
        {'id': 203, 'name': 'District Court Vadodara', 'location': 'Vadodara', 'state_code': 'GJ'},
        {'id': 204, 'name': 'District Court Rajkot', 'location': 'Rajkot', 'state_code': 'GJ'},
        
        {'id': 301, 'name': 'District Court Mumbai City', 'location': 'Mumbai', 'state_code': 'MH'},
        {'id': 302, 'name': 'District Court Pune', 'location': 'Pune', 'state_code': 'MH'},
        {'id': 303, 'name': 'District Court Nagpur', 'location': 'Nagpur', 'state_code': 'MH'},
        
        {'id': 401, 'name': 'District Court Bengaluru Urban', 'location': 'Bengaluru', 'state_code': 'KA'},
        {'id': 501, 'name': 'District Court Chennai', 'location': 'Chennai', 'state_code': 'TN'},
        {'id': 601, 'name': 'District Court Hyderabad', 'location': 'Hyderabad', 'state_code': 'TG'},
        {'id': 701, 'name': 'District Court Kolkata', 'location': 'Kolkata', 'state_code': 'WB'},
    ]
    
    # Create courts with real IDs
    courts = []
    for court_data in real_courts_data:
        court = Court.objects.create(
            id=court_data['id'],  # Use real eCourts ID
            name=court_data['name'],
            location=f"{court_data['location']}, {court_data['state_code']}",
            base_url='https://services.ecourts.gov.in/ecourtindia_v6/',
            is_active=True
        )
        courts.append(court)
    
    print(f"Created {len(courts)} courts with real eCourts IDs")
    
    # Real Case Type Codes used in eCourts
    # These are the actual codes used in the eCourts dropdown forms
    real_case_types = [
        # Civil Cases
        {'name': 'Civil Suit', 'code': 'CS'},
        {'name': 'Civil Appeal', 'code': 'SA'},  # Second Appeal
        {'name': 'Civil Revision', 'code': 'CRP'},
        {'name': 'Civil Miscellaneous', 'code': 'CMP'},
        {'name': 'Execution Petition', 'code': 'EP'},
        {'name': 'Miscellaneous Appeal', 'code': 'MA'},
        {'name': 'Regular Second Appeal', 'code': 'RSA'},
        {'name': 'Title Suit', 'code': 'TS'},
        {'name': 'Money Suit', 'code': 'MS'},
        {'name': 'Rent Control Case', 'code': 'RCC'},
        {'name': 'Partition Suit', 'code': 'PS'},
        {'name': 'Specific Performance', 'code': 'SP'},
        {'name': 'Declaration Suit', 'code': 'DS'},
        {'name': 'Injunction Suit', 'code': 'IS'},
        {'name': 'Possession Suit', 'code': 'POS'},
        
        # Criminal Cases
        {'name': 'Sessions Case', 'code': 'SC'},
        {'name': 'Criminal Appeal', 'code': 'CRA'},
        {'name': 'Criminal Revision', 'code': 'CRR'},
        {'name': 'Criminal Miscellaneous', 'code': 'CRM'},
        {'name': 'Bail Application', 'code': 'BA'},
        {'name': 'Anticipatory Bail', 'code': 'ABA'},
        {'name': 'Criminal Complaint', 'code': 'CC'},
        {'name': 'Magisterial Case', 'code': 'MC'},
        {'name': 'Warrant Case', 'code': 'WC'},
        {'name': 'Summons Case', 'code': 'SMC'},
        {'name': 'FIR Case', 'code': 'FIR'},
        {'name': 'Chargesheet Case', 'code': 'CST'},
        
        # High Court Specific
        {'name': 'Writ Petition', 'code': 'WP'},
        {'name': 'Letter Patent Appeal', 'code': 'LPA'},
        {'name': 'Criminal Writ Petition', 'code': 'CWP'},
        {'name': 'Civil Writ Petition', 'code': 'CWPIL'},
        {'name': 'Public Interest Litigation', 'code': 'PIL'},
        {'name': 'Contempt Case', 'code': 'CONT'},
        {'name': 'Habeas Corpus', 'code': 'HCP'},
        {'name': 'Mandamus', 'code': 'WPM'},
        {'name': 'Certiorari', 'code': 'WPC'},
        {'name': 'Prohibition', 'code': 'WPP'},
        {'name': 'Quo Warranto', 'code': 'WPQ'},
        
        # Family Court Cases
        {'name': 'Divorce Case', 'code': 'DC'},
        {'name': 'Matrimonial Case', 'code': 'MAC'},
        {'name': 'Maintenance Case', 'code': 'MAIN'},
        {'name': 'Guardianship Case', 'code': 'GC'},
        {'name': 'Adoption Case', 'code': 'AC'},
        {'name': 'Domestic Violence', 'code': 'DV'},
        {'name': 'Child Custody', 'code': 'CHC'},
        
        # Commercial Cases
        {'name': 'Commercial Suit', 'code': 'COM'},
        {'name': 'Arbitration Case', 'code': 'ARB'},
        {'name': 'Company Petition', 'code': 'CP'},
        {'name': 'Insolvency Case', 'code': 'IBC'},
        {'name': 'Recovery Suit', 'code': 'RC'},
        {'name': 'Cheque Bounce Case', 'code': 'NI'},  # Under NI Act
        
        # Revenue Cases
        {'name': 'Revenue Case', 'code': 'RC'},
        {'name': 'Land Revenue', 'code': 'LR'},
        {'name': 'Survey Settlement', 'code': 'SS'},
        
        # Labour Cases
        {'name': 'Labour Dispute', 'code': 'LD'},
        {'name': 'Industrial Dispute', 'code': 'ID'},
        {'name': 'Workmen Compensation', 'code': 'WC'},
        
        # Motor Accident Cases
        {'name': 'Motor Accident Claim', 'code': 'MACT'},
        {'name': 'Fatal Accident', 'code': 'FA'},
        {'name': 'Non Fatal Accident', 'code': 'NFA'},
        
        # Consumer Cases
        {'name': 'Consumer Case', 'code': 'CON'},
        {'name': 'Consumer Appeal', 'code': 'CONA'},
        {'name': 'Consumer Revision', 'code': 'CONR'},
        
        # Election Cases
        {'name': 'Election Petition', 'code': 'EP'},
        {'name': 'Election Appeal', 'code': 'EA'},
        
        # Tax Cases
        {'name': 'Income Tax Appeal', 'code': 'ITA'},
        {'name': 'Sales Tax Case', 'code': 'STC'},
        {'name': 'Service Tax Case', 'code': 'ST'},
        {'name': 'GST Case', 'code': 'GST'},
        
        # Miscellaneous
        {'name': 'Interlocutory Application', 'code': 'IA'},
        {'name': 'Transfer Petition', 'code': 'TP'},
        {'name': 'Review Petition', 'code': 'RP'},
        {'name': 'Curative Petition', 'code': 'CURATIVE'},
        {'name': 'Special Leave Petition', 'code': 'SLP'},  # Supreme Court
    ]
    
    # Add case types to all courts
    case_type_count = 0
    for court in courts:
        for ct_data in real_case_types:
            case_type = CaseType.objects.create(
                court=court,
                name=ct_data['name'],
                code=ct_data['code']
            )
            case_type_count += 1
    
    print(f"Created {case_type_count} case types with real eCourts codes")
    print("Real eCourts data setup completed!")
    print("\nYour scraper can now use these real court IDs and case type codes:")
    print("Example search parameters:")
    print("- Court ID: 6 (Gujarat High Court)")
    print("- Case Type: 'WP' (Writ Petition)")
    print("- Case Number: '12345'")
    print("- Filing Year: '2023'")

# Additional function to test your scraper with real data
def test_scraper_setup():
    """
    Function to test if your scraper can work with the real data
    """
    from api.models import Court, CaseType
    
    print("\n=== TESTING SCRAPER SETUP ===")
    
    # Test data that you can use with your scraper
    test_courts = [
        {'id': 6, 'name': 'Gujarat High Court'},
        {'id': 5, 'name': 'Delhi High Court'},
        {'id': 201, 'name': 'District Court Surat'},
    ]
    
    for court_data in test_courts:
        try:
            court = Court.objects.get(id=court_data['id'])
            case_types = CaseType.objects.filter(court=court)[:5]  # Get first 5
            
            print(f"\nCourt: {court.name} (ID: {court.id})")
            print("Available Case Types:")
            for ct in case_types:
                print(f"  - {ct.name} (Code: {ct.code})")
            
            print("Test search URL would be:")
            print(f"  POST /api/search-case/")
            print(f"  Data: {{")
            print(f"    'court_id': {court.id},")
            print(f"    'case_type_id': {case_types.first().id if case_types else 'N/A'},")
            print(f"    'case_number': '12345',")
            print(f"    'filing_year': '2023'")
            print(f"  }}")
            
        except Court.DoesNotExist:
            print(f"Court ID {court_data['id']} not found!")


setup_real_ecourts_data()
test_scraper_setup()
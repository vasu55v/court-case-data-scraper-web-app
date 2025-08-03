import asyncio
import random
import time
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from django.conf import settings
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ECourtsScraper:
    def __init__(self):
        self.base_url = "https://services.ecourts.gov.in/ecourtindia_v6/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    async def search_case(self, court_id: int, case_type: str, case_number: str, filing_year: str) -> Dict:
        """
        Search for case details using eCourts portal
        """
        try:
            # First try with requests for speed
            result = await self._search_with_requests(court_id, case_type, case_number, filing_year)
            if result.get('success'):
                return result
                
            # Fallback to Playwright for JavaScript-heavy pages
            result = await self._search_with_playwright(court_id, case_type, case_number, filing_year)
            return result
            
        except Exception as e:
            logger.error(f"Error searching case: {str(e)}")
            return {
                'success': False,
                'error': f"Search failed: {str(e)}",
                'data': None
            }
    
    async def _search_with_requests(self, court_id: int, case_type: str, case_number: str, filing_year: str) -> Dict:
        """
        Attempt search using requests library
        """
        try:
            # Simulate human behavior with delays
            await asyncio.sleep(random.uniform(
                settings.REQUEST_DELAY_MIN, 
                settings.REQUEST_DELAY_MAX
            ))
            
            # Build search URL
            search_url = f"{self.base_url}?p=casestatus/caseno"
            
            # Get initial page to capture viewstate and other tokens
            response = self.session.get(search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract form tokens
            viewstate = self._extract_viewstate(soup)
            if not viewstate:
                return {'success': False, 'error': 'Could not extract viewstate'}
            
            # Prepare search data
            form_data = {
                '__VIEWSTATE': viewstate,
                'ctl00$ContentPlaceHolder1$DropDownList1': court_id,
                'ctl00$ContentPlaceHolder1$DropDownList2': case_type,
                'ctl00$ContentPlaceHolder1$TextBox1': case_number,
                'ctl00$ContentPlaceHolder1$TextBox2': filing_year,
                'ctl00$ContentPlaceHolder1$Button1': 'Go'
            }
            
            # Submit search
            response = self.session.post(search_url, data=form_data)
            
            if response.status_code == 200:
                return self._parse_case_details(response.text)
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _search_with_playwright(self, court_id: int, case_type: str, case_number: str, filing_year: str) -> Dict:
        """
        Search using Playwright for JavaScript-heavy interactions
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=settings.PLAYWRIGHT_HEADLESS)
            page = await browser.new_page()
            
            try:
                # Navigate to search page
                await page.goto(f"{self.base_url}?p=casestatus/caseno")
                
                # Wait for page to load
                await page.wait_for_selector('select[name*="DropDownList1"]', timeout=10000)
                
                # Fill form
                await page.select_option('select[name*="DropDownList1"]', str(court_id))
                await page.select_option('select[name*="DropDownList2"]', case_type)
                await page.fill('input[name*="TextBox1"]', case_number)
                await page.fill('input[name*="TextBox2"]', filing_year)
                
                # Handle CAPTCHA if present
                captcha_element = await page.query_selector('img[src*="captcha"]')
                if captcha_element:
                    captcha_solution = await self._solve_captcha(page, captcha_element)
                    if captcha_solution:
                        await page.fill('input[name*="captcha"]', captcha_solution)
                
                # Submit form
                await page.click('input[value="Go"]')
                
                # Wait for results
                await page.wait_for_timeout(3000)
                
                # Get page content
                content = await page.content()
                result = self._parse_case_details(content)
                
                return result
                
            except Exception as e:
                return {'success': False, 'error': str(e)}
            finally:
                await browser.close()
    
    def _extract_viewstate(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract ASP.NET ViewState from page"""
        viewstate_input = soup.find('input', {'name': '__VIEWSTATE'})
        return viewstate_input['value'] if viewstate_input else None
    
    async def _solve_captcha(self, page, captcha_element) -> Optional[str]:
        """
        Solve CAPTCHA using various methods
        """
        if not settings.CAPTCHA_ENABLED:
            return None
            
        try:
            # Method 1: Use 2captcha service
            if settings.CAPTCHA_API_KEY:
                captcha_img = await captcha_element.screenshot()
                # Implementation for 2captcha API would go here
                pass
            
            # Method 2: Simple OCR for basic CAPTCHAs
            # This would require additional libraries like pytesseract
            
            # Method 3: Return None to trigger manual input
            return None
            
        except Exception as e:
            logger.error(f"CAPTCHA solving failed: {str(e)}")
            return None
    
    def _parse_case_details(self, html_content: str) -> Dict:
        """
        Parse case details from HTML response
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            # Check for error messages
            error_div = soup.find('div', class_='error') or soup.find('span', {'color': 'red'})
            if error_div and 'not found' in error_div.get_text().lower():
                return {
                    'success': False,
                    'error': 'Case not found',
                    'data': None
                }
            
            # Extract case details from table
            details_table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_GridView1'})
            if not details_table:
                return {
                    'success': False,
                    'error': 'No case details table found',
                    'data': None
                }
            
            case_data = self._extract_case_data(details_table)
            
            # Extract documents/orders
            documents = self._extract_documents(soup)
            
            return {
                'success': True,
                'error': None,
                'data': {
                    'case_details': case_data,
                    'documents': documents
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Parse error: {str(e)}',
                'data': None
            }
    
    def _extract_case_data(self, table) -> Dict:
        """Extract case details from HTML table"""
        data = {}
        rows = table.find_all('tr')
        
        for row in rows[1:]:  # Skip header
            cells = row.find_all('td')
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)
                
                if 'cnr' in key:
                    data['cnr_number'] = value
                elif 'petitioner' in key or 'complainant' in key:
                    data['petitioner_name'] = value
                elif 'respondent' in key or 'accused' in key:
                    data['respondent_name'] = value
                elif 'filing' in key and 'date' in key:
                    data['filing_date'] = self._parse_date(value)
                elif 'next' in key and 'hearing' in key:
                    data['next_hearing_date'] = self._parse_date(value)
                elif 'status' in key:
                    data['case_status'] = value
                elif 'court' in key or 'hall' in key:
                    data['court_hall'] = value
                elif 'judge' in key:
                    data['judge_name'] = value
        
        return data
    
    def _extract_documents(self, soup) -> List[Dict]:
        """Extract document/order links"""
        documents = []
        
        # Look for PDF links
        pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
        
        for link in pdf_links:
            href = link.get('href')
            text = link.get_text(strip=True)
            
            if href:
                documents.append({
                    'document_type': self._classify_document(text),
                    'pdf_url': self._resolve_url(href),
                    'file_name': text or 'Document',
                    'document_date': self._extract_date_from_text(text)
                })
        
        return documents
    
    def _classify_document(self, text: str) -> str:
        """Classify document type from text"""
        text_lower = text.lower()
        if 'order' in text_lower:
            return 'Order'
        elif 'judgment' in text_lower:
            return 'Judgment'
        elif 'notice' in text_lower:
            return 'Notice'
        else:
            return 'Document'
    
    def _resolve_url(self, url: str) -> str:
        """Resolve relative URLs to absolute"""
        if url.startswith('http'):
            return url
        return f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to YYYY-MM-DD format"""
        import re
        from datetime import datetime
        
        if not date_str or date_str.strip() == '-':
            return None
            
        # Try different date formats
        formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str.strip(), fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def _extract_date_from_text(self, text: str) -> Optional[str]:
        """Extract date from document text"""
        import re
        
        # Look for date patterns in text
        date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b'
        match = re.search(date_pattern, text)
        
        if match:
            return self._parse_date(match.group(1))
        
        return None
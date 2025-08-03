from django.db import models
from django.contrib.auth.models import User
import uuid

class Court(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    base_url = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name}, {self.location}"

class CaseType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    court = models.ForeignKey(Court, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class CaseQuery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    court = models.ForeignKey(Court, on_delete=models.CASCADE)
    case_type = models.ForeignKey(CaseType, on_delete=models.CASCADE)
    case_number = models.CharField(max_length=50)
    filing_year = models.CharField(max_length=4)
    user_ip = models.GenericIPAddressField()
    queried_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    raw_response = models.JSONField(blank=True, null=True)
    
    class Meta:
        ordering = ['-queried_at']

class CaseDetail(models.Model):
    query = models.OneToOneField(CaseQuery, on_delete=models.CASCADE)
    cnr_number = models.CharField(max_length=50, blank=True)
    petitioner_name = models.CharField(max_length=200, blank=True)
    respondent_name = models.CharField(max_length=200, blank=True)
    filing_date = models.DateField(null=True, blank=True)
    next_hearing_date = models.DateField(null=True, blank=True)
    case_status = models.CharField(max_length=100, blank=True)
    court_hall = models.CharField(max_length=50, blank=True)
    judge_name = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Case {self.query.case_number}/{self.query.filing_year}"

class CaseDocument(models.Model):
    case_detail = models.ForeignKey(CaseDetail, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50)  # Order, Judgment, etc.
    document_date = models.DateField(null=True, blank=True)
    pdf_url = models.URLField()
    file_name = models.CharField(max_length=200, blank=True)
    downloaded = models.BooleanField(default=False)
    local_file_path = models.CharField(max_length=500, blank=True)
    
    class Meta:
        ordering = ['-document_date']

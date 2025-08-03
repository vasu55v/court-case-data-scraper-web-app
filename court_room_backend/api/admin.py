from django.contrib import admin
from .models import Court, CaseType, CaseQuery, CaseDetail, CaseDocument

@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_active', 'created_at')
    list_filter = ('is_active', 'location')
    search_fields = ('name', 'location')

@admin.register(CaseType)
class CaseTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'court')
    list_filter = ('court',)
    search_fields = ('name', 'code')

@admin.register(CaseQuery)
class CaseQueryAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'filing_year', 'court', 'success', 'queried_at')
    list_filter = ('success', 'court', 'queried_at')
    search_fields = ('case_number', 'user_ip')
    readonly_fields = ('id', 'queried_at', 'raw_response')

@admin.register(CaseDetail)
class CaseDetailAdmin(admin.ModelAdmin):
    list_display = ('query', 'cnr_number', 'petitioner_name', 'case_status')
    search_fields = ('cnr_number', 'petitioner_name', 'respondent_name')

@admin.register(CaseDocument)
class CaseDocumentAdmin(admin.ModelAdmin):
    list_display = ('case_detail', 'document_type', 'document_date', 'downloaded')
    list_filter = ('document_type', 'downloaded')
    search_fields = ('file_name',)
from django.urls import path
from . import views

urlpatterns = [
    path('courts/', views.CourtListView.as_view(), name='court-list'),
    path('case-types/', views.CaseTypeListView.as_view(), name='case-type-list'),
    path('case-search/', views.search_case, name='case-search'),
    path('case-history/', views.CaseHistoryView.as_view(), name='case-history'),
    path('case-detail/<uuid:query_id>/', views.case_detail, name='case-detail'),
    path('download-pdf/<int:document_id>/', views.download_pdf, name='download-pdf'),
]
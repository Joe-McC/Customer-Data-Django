# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'organizations', views.OrganizationViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'data-categories', views.DataCategoryViewSet)
router.register(r'data-storages', views.DataStorageViewSet)
router.register(r'data-mappings', views.DataMappingViewSet)
router.register(r'data-subject-requests', views.DataSubjectRequestViewSet)
router.register(r'documents', views.DocumentViewSet)
router.register(r'compliance-actions', views.ComplianceActionViewSet)

# Add new API endpoints for GDPR automation
router.register(r'data-subjects', views.DataSubjectViewSet)
router.register(r'workflow-templates', views.WorkflowTemplateViewSet)
router.register(r'workflow-step-templates', views.WorkflowStepTemplateViewSet)
router.register(r'workflow-instances', views.WorkflowInstanceViewSet)
router.register(r'workflow-steps', views.WorkflowStepViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # Custom endpoints
    path('dashboard/summary/', views.DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('data-map/', views.DataMapView.as_view(), name='data-map'),
    path('document-templates/', views.DocumentTemplateListView.as_view(), name='document-templates'),
    path('generate-document/<uuid:template_id>/', views.GenerateDocumentView.as_view(), name='generate-document'),
    path('export-data-inventory/', views.ExportDataInventoryView.as_view(), name='export-data-inventory'),
    
    # New GDPR automation endpoints
    path('dashboard/enhanced/', views.EnhancedDashboardView.as_view(), name='enhanced-dashboard'),
    path('automated-workflows/process/', views.AutomatedWorkflowView.as_view(), name='process-automated-workflows'),
]


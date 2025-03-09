from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'crm'

# API Router
router = DefaultRouter()
router.register(r'accounts', views.AccountViewSet)
router.register(r'contacts', views.ContactViewSet)
router.register(r'leads', views.LeadViewSet)
router.register(r'opportunities', views.OpportunityViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'custom-fields', views.CustomFieldViewSet)
router.register(r'custom-field-values', views.CustomFieldValueViewSet)
router.register(r'reports', views.ReportViewSet)
router.register(r'dashboards', views.DashboardViewSet)
router.register(r'dashboard-components', views.DashboardComponentViewSet)
router.register(r'email-templates', views.EmailTemplateViewSet)
router.register(r'workflow-rules', views.WorkflowRuleViewSet)
router.register(r'workflow-actions', views.WorkflowActionViewSet)
router.register(r'approval-processes', views.ApprovalProcessViewSet)
router.register(r'approval-steps', views.ApprovalStepViewSet)
router.register(r'approval-requests', views.ApprovalRequestViewSet)

# Template-based URLs
urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Accounts
    path('accounts/', views.account_list, name='account_list'),
    path('accounts/new/', views.account_create, name='account_create'),
    path('accounts/<int:pk>/', views.account_detail, name='account_detail'),
    path('accounts/<int:pk>/edit/', views.account_edit, name='account_edit'),
    path('accounts/<int:pk>/delete/', views.account_delete, name='account_delete'),
    
    # Contacts
    path('contacts/new/', views.contact_create, name='contact_create'),
    path('contacts/<int:pk>/', views.contact_detail, name='contact_detail'),
    
    # Opportunities
    path('opportunities/intake/', views.opportunity_intake, name='opportunity_intake'),
    
    # API endpoints
    path('api/', include(router.urls)),
] 
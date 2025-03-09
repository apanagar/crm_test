from django.urls import path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
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

urlpatterns = router.urls 
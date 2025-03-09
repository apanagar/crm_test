from django.contrib import admin
from .models import (
    Account, Contact, Lead, Opportunity, Task,
    CustomField, CustomFieldValue, Report, Dashboard, DashboardComponent,
    EmailTemplate, WorkflowRule, WorkflowAction, ApprovalProcess,
    ApprovalStep, ApprovalRequest
)

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_owner', 'industry', 'created_date')
    list_filter = ('industry', 'created_date')
    search_fields = ('name', 'website')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'account', 'owner')
    list_filter = ('account', 'created_date')
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'company', 'status', 'owner')
    list_filter = ('status', 'source', 'created_date')
    search_fields = ('first_name', 'last_name', 'company')

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'account', 'amount', 'stage', 'close_date', 'probability')
    list_filter = ('stage', 'close_date')
    search_fields = ('name', 'account__name')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('subject', 'due_date', 'status', 'priority', 'owner')
    list_filter = ('status', 'priority', 'due_date')
    search_fields = ('subject', 'description')

@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'label', 'field_type', 'model_name', 'required', 'created_by')
    list_filter = ('field_type', 'model_name', 'required')
    search_fields = ('name', 'label')

@admin.register(CustomFieldValue)
class CustomFieldValueAdmin(admin.ModelAdmin):
    list_display = ('custom_field', 'record_id', 'value')
    list_filter = ('custom_field',)
    search_fields = ('value',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'model_name', 'owner', 'is_public')
    list_filter = ('report_type', 'model_name', 'is_public')
    search_fields = ('name', 'description')

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_public', 'created_date')
    list_filter = ('is_public', 'created_date')
    search_fields = ('name', 'description')

@admin.register(DashboardComponent)
class DashboardComponentAdmin(admin.ModelAdmin):
    list_display = ('title', 'dashboard', 'chart_type', 'position')
    list_filter = ('chart_type', 'dashboard')
    search_fields = ('title',)
    ordering = ('dashboard', 'position')

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'model_name', 'owner', 'created_date')
    list_filter = ('model_name', 'is_html')
    search_fields = ('name', 'subject', 'body')

@admin.register(WorkflowRule)
class WorkflowRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_name', 'active', 'evaluation_criteria', 'owner')
    list_filter = ('model_name', 'active', 'evaluation_criteria')
    search_fields = ('name', 'description')

@admin.register(WorkflowAction)
class WorkflowActionAdmin(admin.ModelAdmin):
    list_display = ('name', 'workflow_rule', 'action_type', 'order')
    list_filter = ('workflow_rule', 'action_type')
    search_fields = ('name',)
    ordering = ('workflow_rule', 'order')

@admin.register(ApprovalProcess)
class ApprovalProcessAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_name', 'active', 'owner')
    list_filter = ('model_name', 'active')
    search_fields = ('name', 'description')

@admin.register(ApprovalStep)
class ApprovalStepAdmin(admin.ModelAdmin):
    list_display = ('name', 'approval_process', 'step_number', 'approval_type')
    list_filter = ('approval_process', 'approval_type')
    search_fields = ('name',)
    ordering = ('approval_process', 'step_number')

@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ('approval_process', 'current_step', 'status', 'submitter', 'created_date')
    list_filter = ('approval_process', 'status', 'current_step')
    search_fields = ('comments',)
    ordering = ('-created_date',)

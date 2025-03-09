from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Account, Contact, Lead, Opportunity, Task,
    CustomField, CustomFieldValue, Report, Dashboard, DashboardComponent,
    EmailTemplate, WorkflowRule, WorkflowAction, ApprovalProcess,
    ApprovalStep, ApprovalRequest
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class AccountSerializer(serializers.ModelSerializer):
    account_owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Account
        fields = '__all__'

class ContactSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Contact
        fields = '__all__'

class LeadSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Lead
        fields = '__all__'

class OpportunitySerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Opportunity
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = '__all__'

class CustomFieldSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = CustomField
        fields = '__all__'

class CustomFieldValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomFieldValue
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Report
        fields = '__all__'

class DashboardComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardComponent
        fields = '__all__'

class DashboardSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    components = DashboardComponentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Dashboard
        fields = '__all__'

class EmailTemplateSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = EmailTemplate
        fields = '__all__'

class WorkflowActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowAction
        fields = '__all__'

class WorkflowRuleSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    actions = WorkflowActionSerializer(many=True, read_only=True)
    
    class Meta:
        model = WorkflowRule
        fields = '__all__'

class ApprovalStepSerializer(serializers.ModelSerializer):
    approvers = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = ApprovalStep
        fields = '__all__'

class ApprovalProcessSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    steps = ApprovalStepSerializer(many=True, read_only=True)
    
    class Meta:
        model = ApprovalProcess
        fields = '__all__'

class ApprovalRequestSerializer(serializers.ModelSerializer):
    submitter = UserSerializer(read_only=True)
    
    class Meta:
        model = ApprovalRequest
        fields = '__all__' 
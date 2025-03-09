from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
import json
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from .models import (
    Account, Contact, Lead, Opportunity, Task,
    CustomField, CustomFieldValue, Report, Dashboard, DashboardComponent,
    EmailTemplate, WorkflowRule, WorkflowAction, ApprovalProcess,
    ApprovalStep, ApprovalRequest, EmailCommunication
)
from .serializers import (
    AccountSerializer, ContactSerializer, LeadSerializer,
    OpportunitySerializer, TaskSerializer, CustomFieldSerializer,
    CustomFieldValueSerializer, ReportSerializer, DashboardSerializer,
    DashboardComponentSerializer, EmailTemplateSerializer,
    WorkflowRuleSerializer, WorkflowActionSerializer,
    ApprovalProcessSerializer, ApprovalStepSerializer,
    ApprovalRequestSerializer
)
from .forms import AccountForm, ContactForm  # We'll create these form classes next

# Template-based views
@login_required
def dashboard(request):
    # Get the first day of current month
    today = timezone.now()
    first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Account metrics
    total_accounts = Account.objects.count()
    new_accounts_count = Account.objects.filter(created_date__gte=first_day_of_month).count()

    # Opportunity metrics
    open_opportunities = Opportunity.objects.exclude(stage__in=['closed_won', 'closed_lost'])
    open_opportunities_count = open_opportunities.count()
    total_opportunity_value = open_opportunities.aggregate(total=Sum('amount'))['total'] or 0

    # Lead metrics
    active_leads_count = Lead.objects.exclude(status='converted').count()
    converted_leads_count = Lead.objects.filter(status='converted', modified_date__gte=first_day_of_month).count()

    # Task metrics
    tasks_due_count = Task.objects.filter(due_date__date=today.date()).count()
    overdue_tasks_count = Task.objects.filter(due_date__lt=today, status__in=['not_started', 'in_progress']).count()

    # Pipeline data for funnel
    stage_display = dict(Opportunity.STAGE_CHOICES)
    funnel_data = Opportunity.objects.values('stage').annotate(
        count=Count('id'),
        value=Sum('amount')
    ).order_by('-count')

    # Prepare funnel data in the correct order
    stage_order = ['prospecting', 'qualification', 'needs_analysis', 'value_proposition', 'negotiation', 'closed_won']
    funnel_stages = []
    funnel_counts = []
    funnel_values = []
    
    for stage in stage_order:
        stage_data = next((item for item in funnel_data if item['stage'] == stage), None)
        if stage_data:
            funnel_stages.append(stage_display[stage])
            funnel_counts.append(stage_data['count'])
            funnel_values.append(float(stage_data['value']) if stage_data['value'] else 0)

    # Recent activity
    recent_activities = []
    
    # Recent accounts
    for account in Account.objects.order_by('-created_date')[:5]:
        recent_activities.append({
            'title': f'New Account Created: {account.name}',
            'description': f'Industry: {account.industry}' if account.industry else '',
            'timestamp': account.created_date
        })
    
    # Recent opportunities
    for opp in Opportunity.objects.order_by('-modified_date')[:5]:
        recent_activities.append({
            'title': f'Opportunity Updated: {opp.name}',
            'description': f'Stage: {opp.get_stage_display()} - ${opp.amount:,.2f}',
            'timestamp': opp.modified_date
        })
    
    # Sort activities by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = recent_activities[:5]  # Keep only 5 most recent

    context = {
        'total_accounts': total_accounts,
        'new_accounts_count': new_accounts_count,
        'open_opportunities_count': open_opportunities_count,
        'total_opportunity_value': total_opportunity_value,
        'active_leads_count': active_leads_count,
        'converted_leads_count': converted_leads_count,
        'tasks_due_count': tasks_due_count,
        'overdue_tasks_count': overdue_tasks_count,
        'funnel_stages': json.dumps(funnel_stages),
        'funnel_counts': json.dumps(funnel_counts),
        'funnel_values': json.dumps(funnel_values),
        'recent_activities': recent_activities,
    }

    return render(request, 'crm/dashboard.html', context)

@login_required
def account_list(request):
    accounts = Account.objects.all().select_related('account_owner')
    return render(request, 'crm/accounts/list.html', {'accounts': accounts})

@login_required
def account_detail(request, pk):
    account = get_object_or_404(Account, pk=pk)
    
    # Get email communications
    communications = account.communications.select_related('contact', 'owner').all()
    
    # Get pending follow-ups
    pending_follow_ups = communications.filter(
        requires_follow_up=True,
        follow_up_completed=False
    ).order_by('follow_up_date')

    # Mark follow-up as complete
    if request.method == 'POST' and request.POST.get('action') == 'complete_follow_up':
        comm_id = request.POST.get('communication_id')
        if comm_id:
            comm = get_object_or_404(EmailCommunication, id=comm_id, account=account)
            comm.follow_up_completed = True
            comm.save()
            messages.success(request, 'Follow-up marked as completed.')
            return redirect('crm:account_detail', pk=account.pk)

    context = {
        'account': account,
        'communications': communications,
        'pending_follow_ups': pending_follow_ups,
    }
    return render(request, 'crm/accounts/detail.html', context)

@login_required
def account_create(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.account_owner = request.user
            account.save()
            messages.success(request, 'Account created successfully.')
            return redirect('crm:account_detail', pk=account.pk)
    else:
        form = AccountForm()
    
    return render(request, 'crm/accounts/form.html', {
        'form': form,
        'form_title': 'New Account'
    })

@login_required
def account_edit(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account updated successfully.')
            return redirect('crm:account_detail', pk=account.pk)
    else:
        form = AccountForm(instance=account)
    
    return render(request, 'crm/accounts/form.html', {
        'form': form,
        'form_title': f'Edit Account: {account.name}'
    })

@login_required
@require_http_methods(['POST'])
def account_delete(request, pk):
    account = get_object_or_404(Account, pk=pk)
    account.delete()
    messages.success(request, 'Account deleted successfully.')
    return redirect('crm:account_list')

@login_required
def contact_create(request):
    account = None
    if request.GET.get('account'):
        account = get_object_or_404(Account, pk=request.GET['account'])
    
    if request.method == 'POST':
        form = ContactForm(request.POST, account=account)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.owner = request.user
            contact.save()
            messages.success(request, 'Contact created successfully.')
            return redirect('crm:account_detail', pk=contact.account.pk)
    else:
        form = ContactForm(account=account)
    
    context = {
        'form': form,
        'form_title': 'New Contact',
        'account': account,
        'accounts': Account.objects.all() if not account else None
    }
    return render(request, 'crm/contacts/form.html', context)

@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    return render(request, 'crm/contacts/detail.html', {'contact': contact})

@login_required
def opportunity_intake(request):
    if request.method == 'POST':
        # Create or get the account based on company name
        account, created = Account.objects.get_or_create(
            name=request.POST['company'],
            defaults={
                'industry': request.POST.get('industry'),
                'account_owner': request.user
            }
        )
        
        # Create or get the contact
        contact, created = Contact.objects.get_or_create(
            email=request.POST['contact_email'],
            defaults={
                'first_name': request.POST['contact_name'].split()[0],
                'last_name': ' '.join(request.POST['contact_name'].split()[1:]),
                'title': request.POST.get('contact_title'),
                'phone': request.POST.get('contact_phone'),
                'account': account,
                'owner': request.user
            }
        )
        
        # Create the opportunity
        opportunity = Opportunity.objects.create(
            name=request.POST['opportunity_name'],
            amount=request.POST['amount'],
            stage=request.POST['stage'],
            probability=request.POST['probability'],
            close_date=request.POST['close_date'],
            source=request.POST.get('source'),
            description=request.POST.get('description'),
            next_steps=request.POST.get('next_steps'),
            account=account,
            primary_contact=contact,
            owner=request.user
        )
        
        # Handle products/services
        products = request.POST.getlist('products')
        if products:
            # You might want to create a many-to-many relationship with products here
            opportunity.description += f"\n\nInterested in: {', '.join(products)}"
            opportunity.save()
        
        messages.success(request, 'Opportunity created successfully.')
        return redirect('crm:opportunity_detail', pk=opportunity.pk)
    
    return render(request, 'crm/opportunities/intake.html')

# API ViewSets
class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'industry', 'website']
    ordering_fields = ['name', 'created_date', 'modified_date']
    filterset_fields = ['industry']

    def perform_create(self, serializer):
        serializer.save(account_owner=self.request.user)

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['last_name', 'created_date']
    filterset_fields = ['account']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['first_name', 'last_name', 'company']
    ordering_fields = ['created_date', 'status']
    filterset_fields = ['status', 'source']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class OpportunityViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'account__name']
    ordering_fields = ['amount', 'close_date', 'probability']
    filterset_fields = ['stage', 'account']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['subject', 'description']
    ordering_fields = ['due_date', 'priority', 'status']
    filterset_fields = ['status', 'priority']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class CustomFieldViewSet(viewsets.ModelViewSet):
    queryset = CustomField.objects.all()
    serializer_class = CustomFieldSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'label']
    ordering_fields = ['name', 'created_date']
    filterset_fields = ['model_name', 'field_type']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class CustomFieldValueViewSet(viewsets.ModelViewSet):
    queryset = CustomFieldValue.objects.all()
    serializer_class = CustomFieldValueSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['custom_field', 'record_id']

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_date', 'modified_date']
    filterset_fields = ['report_type', 'model_name', 'is_public']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return Report.objects.filter(
            models.Q(owner=self.request.user) | models.Q(is_public=True)
        )

class DashboardViewSet(viewsets.ModelViewSet):
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_date', 'modified_date']
    filterset_fields = ['is_public']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return Dashboard.objects.filter(
            models.Q(owner=self.request.user) | models.Q(is_public=True)
        )

class DashboardComponentViewSet(viewsets.ModelViewSet):
    queryset = DashboardComponent.objects.all()
    serializer_class = DashboardComponentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['position']
    filterset_fields = ['dashboard', 'chart_type']

class EmailTemplateViewSet(viewsets.ModelViewSet):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'subject']
    ordering_fields = ['name', 'created_date']
    filterset_fields = ['model_name']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class WorkflowRuleViewSet(viewsets.ModelViewSet):
    queryset = WorkflowRule.objects.all()
    serializer_class = WorkflowRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_date']
    filterset_fields = ['model_name', 'active']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class WorkflowActionViewSet(viewsets.ModelViewSet):
    queryset = WorkflowAction.objects.all()
    serializer_class = WorkflowActionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['order']
    filterset_fields = ['workflow_rule', 'action_type']

class ApprovalProcessViewSet(viewsets.ModelViewSet):
    queryset = ApprovalProcess.objects.all()
    serializer_class = ApprovalProcessSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_date']
    filterset_fields = ['model_name', 'active']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ApprovalStepViewSet(viewsets.ModelViewSet):
    queryset = ApprovalStep.objects.all()
    serializer_class = ApprovalStepSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['step_number']
    filterset_fields = ['approval_process', 'approval_type']

class ApprovalRequestViewSet(viewsets.ModelViewSet):
    queryset = ApprovalRequest.objects.all()
    serializer_class = ApprovalRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['comments']
    ordering_fields = ['created_date', 'modified_date']
    filterset_fields = ['approval_process', 'status', 'current_step']

    def perform_create(self, serializer):
        serializer.save(submitter=self.request.user)

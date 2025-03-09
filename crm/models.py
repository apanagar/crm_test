from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class Account(models.Model):
    name = models.CharField(max_length=200)
    account_owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    shipping_address = models.TextField(blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Contact(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='contacts')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    mailing_address = models.TextField(blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Lead(models.Model):
    LEAD_STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('unqualified', 'Unqualified'),
        ('converted', 'Converted'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    company = models.CharField(max_length=200)
    title = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=LEAD_STATUS_CHOICES, default='new')
    source = models.CharField(max_length=100, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company}"

class Opportunity(models.Model):
    STAGE_CHOICES = [
        ('prospecting', 'Prospecting'),
        ('qualification', 'Qualification'),
        ('needs_analysis', 'Needs Analysis'),
        ('value_proposition', 'Value Proposition'),
        ('negotiation', 'Negotiation'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    ]

    name = models.CharField(max_length=200)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='opportunities')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    close_date = models.DateField()
    probability = models.IntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('deferred', 'Deferred'),
    ]

    subject = models.CharField(max_length=200)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    related_to_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    related_to_contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True)
    related_to_opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

class CustomField(models.Model):
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('datetime', 'DateTime'),
        ('picklist', 'Picklist'),
        ('boolean', 'Boolean'),
        ('url', 'URL'),
        ('email', 'Email'),
        ('phone', 'Phone'),
    ]

    MODEL_CHOICES = [
        ('Account', 'Account'),
        ('Contact', 'Contact'),
        ('Lead', 'Lead'),
        ('Opportunity', 'Opportunity'),
        ('Task', 'Task'),
    ]

    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    model_name = models.CharField(max_length=20, choices=MODEL_CHOICES)
    required = models.BooleanField(default=False)
    picklist_values = models.TextField(blank=True, help_text='JSON array of picklist values')
    default_value = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.label} ({self.model_name})"

    def get_picklist_values(self):
        if self.field_type == 'picklist' and self.picklist_values:
            return json.loads(self.picklist_values)
        return []

class CustomFieldValue(models.Model):
    custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE)
    record_id = models.IntegerField()
    value = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('custom_field', 'record_id')

class Report(models.Model):
    REPORT_TYPES = [
        ('tabular', 'Tabular'),
        ('summary', 'Summary'),
        ('matrix', 'Matrix'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    model_name = models.CharField(max_length=20, choices=CustomField.MODEL_CHOICES)
    fields = models.TextField(help_text='JSON array of field names to include')
    filters = models.TextField(blank=True, help_text='JSON object of filter conditions')
    grouping_fields = models.TextField(blank=True, help_text='JSON array of grouping fields')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_fields(self):
        return json.loads(self.fields)

    def get_filters(self):
        return json.loads(self.filters) if self.filters else {}

    def get_grouping_fields(self):
        return json.loads(self.grouping_fields) if self.grouping_fields else []

class Dashboard(models.Model):
    CHART_TYPES = [
        ('bar', 'Bar Chart'),
        ('line', 'Line Chart'),
        ('pie', 'Pie Chart'),
        ('table', 'Table'),
        ('funnel', 'Funnel'),
        ('metric', 'Metric'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class DashboardComponent(models.Model):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='components')
    title = models.CharField(max_length=200)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    chart_type = models.CharField(max_length=20, choices=Dashboard.CHART_TYPES)
    width = models.IntegerField(default=6, help_text='Width in grid units (1-12)')
    height = models.IntegerField(default=4, help_text='Height in grid units')
    position = models.IntegerField(default=0, help_text='Order of appearance')
    chart_config = models.TextField(blank=True, help_text='JSON object of chart configuration')

    def __str__(self):
        return f"{self.title} - {self.dashboard.name}"

    def get_chart_config(self):
        return json.loads(self.chart_config) if self.chart_config else {}

class EmailTemplate(models.Model):
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    model_name = models.CharField(max_length=20, choices=CustomField.MODEL_CHOICES)
    is_html = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)
    available_merge_fields = models.TextField(help_text='JSON array of available merge fields')

    def __str__(self):
        return self.name

    def get_merge_fields(self):
        return json.loads(self.available_merge_fields) if self.available_merge_fields else []

class WorkflowRule(models.Model):
    EVALUATION_CRITERIA = [
        ('created', 'When record is created'),
        ('created_edited', 'When record is created, and every time it is edited'),
        ('edited', 'Every time record is edited'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    model_name = models.CharField(max_length=20, choices=CustomField.MODEL_CHOICES)
    active = models.BooleanField(default=False)
    evaluation_criteria = models.CharField(max_length=20, choices=EVALUATION_CRITERIA)
    conditions = models.TextField(help_text='JSON object of filter conditions')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_conditions(self):
        return json.loads(self.conditions) if self.conditions else {}

class WorkflowAction(models.Model):
    ACTION_TYPES = [
        ('field_update', 'Field Update'),
        ('email_alert', 'Email Alert'),
        ('task_creation', 'Task Creation'),
        ('outbound_message', 'Outbound Message'),
    ]

    workflow_rule = models.ForeignKey(WorkflowRule, on_delete=models.CASCADE, related_name='actions')
    name = models.CharField(max_length=200)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    action_config = models.TextField(help_text='JSON object of action configuration')
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.get_action_type_display()})"

    def get_action_config(self):
        return json.loads(self.action_config) if self.action_config else {}

class ApprovalProcess(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    model_name = models.CharField(max_length=20, choices=CustomField.MODEL_CHOICES)
    active = models.BooleanField(default=False)
    entry_criteria = models.TextField(help_text='JSON object of entry criteria')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_entry_criteria(self):
        return json.loads(self.entry_criteria) if self.entry_criteria else {}

class ApprovalStep(models.Model):
    APPROVAL_TYPE = [
        ('unanimous', 'Unanimous'),
        ('first_response', 'First Response'),
    ]

    approval_process = models.ForeignKey(ApprovalProcess, on_delete=models.CASCADE, related_name='steps')
    name = models.CharField(max_length=200)
    step_number = models.IntegerField()
    approval_type = models.CharField(max_length=20, choices=APPROVAL_TYPE)
    approvers = models.ManyToManyField(User, related_name='approval_steps')
    reject_behavior = models.TextField(help_text='JSON object of rejection behavior')
    approval_actions = models.TextField(help_text='JSON object of approval actions')
    rejection_actions = models.TextField(help_text='JSON object of rejection actions')

    class Meta:
        ordering = ['step_number']

    def __str__(self):
        return f"{self.name} - Step {self.step_number}"

    def get_reject_behavior(self):
        return json.loads(self.reject_behavior) if self.reject_behavior else {}

    def get_approval_actions(self):
        return json.loads(self.approval_actions) if self.approval_actions else {}

    def get_rejection_actions(self):
        return json.loads(self.rejection_actions) if self.rejection_actions else {}

class ApprovalRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('recalled', 'Recalled'),
    ]

    approval_process = models.ForeignKey(ApprovalProcess, on_delete=models.CASCADE)
    current_step = models.ForeignKey(ApprovalStep, on_delete=models.CASCADE)
    record_id = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='submitted_approvals')
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"Approval Request for {self.approval_process.name} - {self.get_status_display()}"

class EmailCommunication(models.Model):
    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]

    account = models.ForeignKey('Account', on_delete=models.CASCADE, related_name='communications')
    contact = models.ForeignKey('Contact', on_delete=models.SET_NULL, null=True, blank=True, related_name='communications')
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    sent_date = models.DateTimeField()
    sender = models.EmailField()
    recipients = models.TextField(help_text='Comma-separated list of email addresses')
    requires_follow_up = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    follow_up_completed = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-sent_date']

    def __str__(self):
        return f"{self.subject} ({self.sent_date.strftime('%Y-%m-%d %H:%M')})"

    def get_recipients_list(self):
        return [email.strip() for email in self.recipients.split(',')]

    @property
    def is_follow_up_overdue(self):
        if self.requires_follow_up and not self.follow_up_completed:
            return self.follow_up_date and self.follow_up_date < timezone.now().date()
        return False

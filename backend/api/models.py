# models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class Organization(models.Model):
    """Organization/company using the system"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, choices=[
        ('legal', 'Legal Services'),
        ('accounting', 'Accounting'),
        ('consulting', 'Consulting'),
        ('financial_advisory', 'Financial Advisory'),
        ('other', 'Other Professional Services')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class User(AbstractUser):
    """Extended user model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='users')
    job_title = models.CharField(max_length=100, blank=True)
    is_admin = models.BooleanField(default=False)
    is_data_processor = models.BooleanField(default=False)
    
    # Add these lines to fix the conflict
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='api_user_groups',  # This is the key change
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='api_user_permissions',  # This is the key change
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    def __str__(self):
        return f"{self.username} ({self.organization.name})"

class DataCategory(models.Model):
    """Categories of personal data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='data_categories')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_sensitive = models.BooleanField(default=False)
    retention_period_days = models.IntegerField(default=365)
    legal_basis = models.CharField(max_length=100, choices=[
        ('consent', 'Consent'),
        ('contract', 'Contract Performance'),
        ('legal_obligation', 'Legal Obligation'),
        ('vital_interests', 'Vital Interests'),
        ('public_interest', 'Public Interest'),
        ('legitimate_interests', 'Legitimate Interests')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"
    
    class Meta:
        verbose_name_plural = 'Data Categories'


class DataStorage(models.Model):
    """Locations where data is stored"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='data_storages')
    name = models.CharField(max_length=255)
    storage_type = models.CharField(max_length=100, choices=[
        ('internal_db', 'Internal Database'),
        ('cloud', 'Cloud Storage'),
        ('saas', 'SaaS Application'),
        ('paper', 'Paper Records'),
        ('other', 'Other')
    ])
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    is_outside_eea = models.BooleanField(default=False)
    security_measures = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"
    
    class Meta:
        verbose_name_plural = 'Data Storages'


class DataMapping(models.Model):
    """Maps relationships between data categories and storage locations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='data_mappings')
    data_category = models.ForeignKey(DataCategory, on_delete=models.CASCADE, related_name='mappings')
    storage = models.ForeignKey(DataStorage, on_delete=models.CASCADE, related_name='mappings')
    purpose = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.data_category.name} in {self.storage.name}"


class DataSubjectRequest(models.Model):
    """Tracks GDPR data subject requests (DSR)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='subject_requests')
    request_type = models.CharField(max_length=100, choices=[
        ('access', 'Right to Access'),
        ('rectification', 'Right to Rectification'),
        ('erasure', 'Right to Erasure'),
        ('restriction', 'Right to Restrict Processing'),
        ('portability', 'Right to Data Portability'),
        ('objection', 'Right to Object'),
        ('not_automated', 'Right Not to be Subject to Automated Decision-Making')
    ])
    data_subject_name = models.CharField(max_length=255)
    data_subject_email = models.EmailField()
    request_details = models.TextField()
    date_received = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=100, choices=[
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('denied', 'Denied')
    ], default='new')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_requests')
    due_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.request_type} request from {self.data_subject_name}"
    
    def save(self, *args, **kwargs):
        # Set due date to 30 days after request if not set
        if not self.due_date:
            self.due_date = self.date_received + timezone.timedelta(days=30)
        super().save(*args, **kwargs)


class Document(models.Model):
    """Compliance documents and templates"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=100, choices=[
        ('privacy_policy', 'Privacy Policy'),
        ('consent_form', 'Consent Form'),
        ('dpa', 'Data Processing Agreement'),
        ('dpia', 'Data Protection Impact Assessment'),
        ('record_processing', 'Record of Processing Activities'),
        ('breach_notification', 'Breach Notification Template'),
        ('other', 'Other Document')
    ])
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='documents/', blank=True)
    version = models.CharField(max_length=50, default='1.0')
    status = models.CharField(max_length=100, choices=[
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived')
    ], default='draft')
    review_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_documents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} (v{self.version})"


class ComplianceAction(models.Model):
    """Tracks compliance tasks and actions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='compliance_actions')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=50, choices=[
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ], default='medium')
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue')
    ], default='pending')
    due_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_actions')
    completed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
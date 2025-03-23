# api/serializers.py
from rest_framework import serializers
from .models import (
    Organization, User, DataCategory, DataStorage, DataMapping,
    DataSubjectRequest, Document, ComplianceAction, DataSubject,
    ConsentActivity, WorkflowTemplate, WorkflowStepTemplate,
    WorkflowInstance, WorkflowStep
)

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'address', 'registration_number', 'industry', 'created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'organization', 'job_title', 'is_admin', 'is_data_processor']
        read_only_fields = ['id']

class DataCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DataCategory
        fields = ['id', 'name', 'description', 'is_sensitive', 'retention_period_days', 'legal_basis', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class DataStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataStorage
        fields = ['id', 'name', 'storage_type', 'description', 'location', 'is_outside_eea', 'security_measures', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class DataMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataMapping
        fields = ['id', 'data_category', 'storage', 'purpose', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class DataSubjectRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSubjectRequest
        fields = ['id', 'request_type', 'data_subject_name', 'data_subject_email', 'request_details', 
                 'date_received', 'status', 'assigned_to', 'due_date', 'completed_date', 'notes', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class DataSubjectSerializer(serializers.ModelSerializer):
    """Serializer for data subjects (individuals whose data is processed)"""
    class Meta:
        model = DataSubject
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'marketing_consent', 'marketing_consent_date',
            'data_processing_consent', 'data_processing_consent_date',
            'cookie_consent', 'cookie_consent_date',
            'data_expiry_date', 'privacy_notice_version',
            'privacy_notice_accepted_date', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 
                           'marketing_consent_date', 'data_processing_consent_date',
                           'cookie_consent_date', 'data_expiry_date']

class ConsentActivitySerializer(serializers.ModelSerializer):
    """Serializer for consent activity logs"""
    class Meta:
        model = ConsentActivity
        fields = [
            'id', 'data_subject', 'activity_type', 'consent_type',
            'timestamp', 'ip_address', 'user_agent', 'notes'
        ]
        read_only_fields = ['id', 'timestamp']

class DocumentSerializer(serializers.ModelSerializer):
    data_subject_detail = DataSubjectSerializer(source='data_subject', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'document_type', 'is_template', 'content',
            'template_variables', 'file', 'version', 'status', 
            'review_date', 'created_by', 'data_subject',
            'data_subject_detail', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

class WorkflowStepTemplateSerializer(serializers.ModelSerializer):
    """Serializer for workflow step templates"""
    class Meta:
        model = WorkflowStepTemplate
        fields = [
            'id', 'workflow_template', 'name', 'description',
            'step_type', 'order', 'is_automated', 'automation_script',
            'document_template', 'estimated_duration_hours',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class WorkflowTemplateSerializer(serializers.ModelSerializer):
    """Serializer for workflow templates"""
    step_templates = WorkflowStepTemplateSerializer(many=True, read_only=True)
    
    class Meta:
        model = WorkflowTemplate
        fields = [
            'id', 'name', 'description', 'workflow_type',
            'estimated_completion_days', 'is_active',
            'step_templates', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class WorkflowStepSerializer(serializers.ModelSerializer):
    """Serializer for individual workflow steps"""
    document_template_detail = DocumentSerializer(source='document_template', read_only=True)
    generated_document_detail = DocumentSerializer(source='generated_document', read_only=True)
    
    class Meta:
        model = WorkflowStep
        fields = [
            'id', 'workflow', 'name', 'description', 'step_type',
            'order', 'is_automated', 'document_template', 'document_template_detail',
            'status', 'assigned_to', 'start_date', 'due_date',
            'completed_date', 'result_notes', 'generated_document',
            'generated_document_detail', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 
                           'generated_document', 'generated_document_detail']

class WorkflowInstanceSerializer(serializers.ModelSerializer):
    """Serializer for workflow instances"""
    steps = WorkflowStepSerializer(many=True, read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    template_detail = WorkflowTemplateSerializer(source='template', read_only=True)
    
    class Meta:
        model = WorkflowInstance
        fields = [
            'id', 'organization', 'template', 'template_detail', 'name',
            'status', 'data_subject', 'related_request', 'assigned_to',
            'start_date', 'due_date', 'completed_date', 'current_step',
            'steps', 'progress_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'progress_percentage']
    
    def get_progress_percentage(self, obj):
        return obj.get_progress_percentage()

class ComplianceActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceAction
        fields = ['id', 'title', 'description', 'priority', 'status', 'due_date', 
                 'assigned_to', 'completed_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
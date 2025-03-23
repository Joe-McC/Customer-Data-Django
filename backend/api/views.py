# viewsets.py

from rest_framework import viewsets, permissions, views, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import (
    Organization, User, DataCategory, DataStorage, DataMapping,
    DataSubjectRequest, Document, ComplianceAction, DataSubject, ConsentActivity,
    WorkflowTemplate, WorkflowInstance, WorkflowStepTemplate, WorkflowStep
)
from .serializers import (
    OrganizationSerializer, UserSerializer, DataCategorySerializer,
    DataStorageSerializer, DataMappingSerializer, DataSubjectRequestSerializer,
    DocumentSerializer, ComplianceActionSerializer, DataSubjectSerializer,
    ConsentActivitySerializer, WorkflowTemplateSerializer, WorkflowInstanceSerializer,
    WorkflowStepTemplateSerializer, WorkflowStepSerializer
)
from .permissions import IsOrganizationAdmin, IsOrganizationMember


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for organizations
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]
    
    def get_queryset(self):
        """
        Filter organizations to only show the user's organization
        """
        user = self.request.user
        return Organization.objects.filter(id=user.organization.id)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]
    
    def get_queryset(self):
        """
        Filter users to only show users in the same organization
        """
        user = self.request.user
        return User.objects.filter(organization=user.organization)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Return the current user's details"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class DataCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for data categories
    """
    queryset = DataCategory.objects.all()
    serializer_class = DataCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        """
        Filter data categories to only show those in the user's organization
        """
        user = self.request.user
        return DataCategory.objects.filter(organization=user.organization)
    
    def perform_create(self, serializer):
        """
        Set the organization when creating a new data category
        """
        serializer.save(organization=self.request.user.organization)


class DataStorageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for data storage locations
    """
    queryset = DataStorage.objects.all()
    serializer_class = DataStorageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        """
        Filter data storage locations to only show those in the user's organization
        """
        user = self.request.user
        return DataStorage.objects.filter(organization=user.organization)
    
    def perform_create(self, serializer):
        """
        Set the organization when creating a new data storage location
        """
        serializer.save(organization=self.request.user.organization)


class DataMappingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for data mappings
    """
    queryset = DataMapping.objects.all()
    serializer_class = DataMappingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        """
        Filter data mappings to only show those in the user's organization
        """
        user = self.request.user
        return DataMapping.objects.filter(organization=user.organization)
    
    def perform_create(self, serializer):
        """
        Set the organization when creating a new data mapping
        """
        serializer.save(organization=self.request.user.organization)


class DataSubjectRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for data subject requests
    """
    queryset = DataSubjectRequest.objects.all()
    serializer_class = DataSubjectRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        """
        Filter requests to only show those in the user's organization
        """
        user = self.request.user
        return DataSubjectRequest.objects.filter(organization=user.organization)
    
    def perform_create(self, serializer):
        """
        Set the organization when creating a new data subject request
        """
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Assign a request to a user
        """
        dsr = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id, organization=request.user.organization)
            dsr.assigned_to = user
            dsr.save()
            return Response({'status': 'request assigned'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update the status of a request
        """
        dsr = self.get_object()
        status_value = request.data.get('status')
        
        if status_value not in dict(DataSubjectRequest._meta.get_field('status').choices).keys():
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        dsr.status = status_value
        if status_value == 'completed':
            dsr.completed_date = timezone.now()
        dsr.save()
        
        return Response({'status': 'request status updated'})


class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for documents
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        """
        Filter documents to only show those in the user's organization
        """
        user = self.request.user
        return Document.objects.filter(organization=user.organization)
    
    def perform_create(self, serializer):
        """
        Set the organization and created_by when creating a new document
        """
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def version(self, request, pk=None):
        """
        Create a new version of an existing document
        """
        doc = self.get_object()
        
        # Create new version with incremented version number
        current_version = float(doc.version)
        new_version = str(current_version + 0.1)
        
        new_doc = Document.objects.create(
            organization=doc.organization,
            title=doc.title,
            document_type=doc.document_type,
            content=doc.content,
            version=new_version,
            status='draft',
            created_by=request.user
        )
        
        serializer = self.get_serializer(new_doc)
        return Response(serializer.data)


class ComplianceActionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for compliance actions
    """
    queryset = ComplianceAction.objects.all()
    serializer_class = ComplianceActionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        """
        Filter compliance actions to only show those in the user's organization
        """
        user = self.request.user
        return ComplianceAction.objects.filter(organization=user.organization)
    
    def perform_create(self, serializer):
        """
        Set the organization when creating a new compliance action
        """
        serializer.save(organization=self.request.user.organization)


# Custom API views

class DashboardSummaryView(views.APIView):
    """
    API endpoint for dashboard summary data
    """
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get(self, request):
        """
        Get summary data for the dashboard
        """
        org = request.user.organization
        
        # Count data subject requests by status
        dsr_counts = {}
        for status_choice, _ in DataSubjectRequest._meta.get_field('status').choices:
            dsr_counts[status_choice] = DataSubjectRequest.objects.filter(
                organization=org, status=status_choice
            ).count()
        
        # Count overdue requests
        overdue_requests = DataSubjectRequest.objects.filter(
            organization=org,
            status__in=['new', 'in_progress'],
            due_date__lt=timezone.now()
        ).count()
        
        # Count compliance actions by priority and status
        actions_by_priority = {}
        for priority, _ in ComplianceAction._meta.get_field('priority').choices:
            actions_by_priority[priority] = ComplianceAction.objects.filter(
                organization=org, priority=priority
            ).count()
        
        actions_by_status = {}
        for status_choice, _ in ComplianceAction._meta.get_field('status').choices:
            actions_by_status[status_choice] = ComplianceAction.objects.filter(
                organization=org, status=status_choice
            ).count()
        
        # Calculate retention compliance
        total_data_categories = DataCategory.objects.filter(organization=org).count()
        categories_with_retention = DataCategory.objects.filter(
            organization=org, 
            retention_period_days__gt=0
        ).count()
        
        retention_compliance = 0
        if total_data_categories > 0:
            retention_compliance = int((categories_with_retention / total_data_categories) * 100)
        
        # Count data storages by type
        storage_counts = {}
        for storage_type, _ in DataStorage._meta.get_field('storage_type').choices:
            storage_counts[storage_type] = DataStorage.objects.filter(
                organization=org, storage_type=storage_type
            ).count()
        
        return Response({
            'data_subject_requests': {
                'counts_by_status': dsr_counts,
                'overdue': overdue_requests,
                'total': sum(dsr_counts.values())
            },
            'compliance_actions': {
                'by_priority': actions_by_priority,
                'by_status': actions_by_status,
                'total': sum(actions_by_status.values())
            },
            'data_inventory': {
                'categories': total_data_categories,
                'storage_locations': sum(storage_counts.values()),
                'retention_compliance': retention_compliance,
                'storage_by_type': storage_counts
            }
        })


class DataMapView(views.APIView):
    """
    API endpoint for data mapping visualization
    """
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get(self, request):
        """
        Get data mapping in a format suitable for visualization
        """
        org = request.user.organization
        
        # Get all data categories and storage locations
        categories = DataCategory.objects.filter(organization=org)
        storages = DataStorage.objects.filter(organization=org)
        mappings = DataMapping.objects.filter(organization=org)
        
        # Format for visualization (nodes and links)
        nodes = []
        links = []
        
        # Add category nodes
        for cat in categories:
            nodes.append({
                'id': str(cat.id),
                'name': cat.name,
                'type': 'category',
                'sensitive': cat.is_sensitive
            })
        
        # Add storage nodes
        for storage in storages:
            nodes.append({
                'id': str(storage.id),
                'name': storage.name,
                'type': 'storage',
                'storage_type': storage.storage_type,
                'outside_eea': storage.is_outside_eea
            })
        
        # Add links between categories and storages
        for mapping in mappings:
            links.append({
                'source': str(mapping.data_category.id),
                'target': str(mapping.storage.id),
                'purpose': mapping.purpose
            })
        
        return Response({
            'nodes': nodes,
            'links': links
        })


class DocumentTemplateListView(views.APIView):
    """
    API endpoint for document templates
    """
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get(self, request):
        """
        Get list of available document templates
        """
        # In MVP, these would be hardcoded templates
        templates = [
            {
                'id': '1',
                'name': 'Privacy Policy',
                'description': 'Generic GDPR-compliant privacy policy for professional services',
                'document_type': 'privacy_policy'
            },
            {
                'id': '2',
                'name': 'Client Consent Form',
                'description': 'Template for obtaining client consent for data processing',
                'document_type': 'consent_form'
            },
            {
                'id': '3',
                'name': 'Data Processing Agreement',
                'description': 'Template for agreements with third-party data processors',
                'document_type': 'dpa'
            },
            {
                'id': '4',
                'name': 'Engagement Letter GDPR Clauses',
                'description': 'GDPR clauses to include in client engagement letters',
                'document_type': 'other'
            },
            {
                'id': '5',
                'name': 'Data Breach Notification Template',
                'description': 'Template for notifying ICO of a data breach',
                'document_type': 'breach_notification'
            }
        ]
        
        return Response(templates)


class GenerateDocumentView(views.APIView):
    """
    API endpoint for generating documents from templates
    """
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def post(self, request, template_id):
        """
        Generate a document from a template with custom fields
        """
        # Get template content based on template_id
        # In MVP, these would be hardcoded template contents
        template_content = "This is the template content with {{ORGANIZATION_NAME}} placeholders"
        
        # Get custom fields from request
        fields = request.data.get('fields', {})
        
        # Replace placeholders in template with custom fields
        content = template_content
        for key, value in fields.items():
            content = content.replace('{{' + key + '}}', value)
        
        # Create new document
        doc = Document.objects.create(
            organization=request.user.organization,
            title=request.data.get('title', 'Generated Document'),
            document_type=request.data.get('document_type', 'other'),
            content=content,
            created_by=request.user
        )
        
        serializer = DocumentSerializer(doc)
        return Response(serializer.data)


class ExportDataInventoryView(views.APIView):
    """
    API endpoint for exporting data inventory
    """
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get(self, request):
        """
        Export data inventory as CSV or JSON
        """
        format_type = request.query_params.get('format', 'json')
        org = request.user.organization
        
        # Get all data categories and their mappings
        categories = DataCategory.objects.filter(organization=org)
        
        # Format data for export
        data = []
        for category in categories:
            category_data = {
                'category_name': category.name,
                'is_sensitive': category.is_sensitive,
                'legal_basis': category.legal_basis,
                'retention_period_days': category.retention_period_days,
                'storages': []
            }
            
            # Add storage locations for this category
            for mapping in category.mappings.all():
                storage = mapping.storage
                category_data['storages'].append({
                    'storage_name': storage.name,
                    'storage_type': storage.storage_type,
                    'outside_eea': storage.is_outside_eea,
                    'purpose': mapping.purpose
                })
            
            data.append(category_data)
        
        # Return data in requested format
        if format_type == 'csv':
            # In a real implementation, convert to CSV
            return Response({'status': 'CSV export not implemented in MVP'})
        else:
            return Response(data)


class DataSubjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for data subjects (individuals whose data is processed)
    """
    queryset = DataSubject.objects.all()
    serializer_class = DataSubjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        """
        Filter data subjects to only show those in the user's organization
        """
        user = self.request.user
        return DataSubject.objects.filter(organization=user.organization)
    
    def perform_create(self, serializer):
        """
        Set the organization when creating a new data subject
        """
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['get'])
    def consent_activities(self, request, pk=None):
        """
        Get consent activities for a specific data subject
        """
        data_subject = self.get_object()
        activities = ConsentActivity.objects.filter(data_subject=data_subject)
        serializer = ConsentActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def record_consent(self, request, pk=None):
        """
        Record a consent activity for a specific data subject
        """
        data_subject = self.get_object()
        serializer = ConsentActivitySerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(
                data_subject=data_subject,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkflowTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for workflow templates
    """
    queryset = WorkflowTemplate.objects.all()
    serializer_class = WorkflowTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        """
        Filter workflow templates to only show those in the user's organization
        """
        user = self.request.user
        return WorkflowTemplate.objects.filter(organization=user.organization)
    
    def perform_create(self, serializer):
        """
        Set the organization when creating a new workflow template
        """
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def create_workflow(self, request, pk=None):
        """
        Create a new workflow instance from this template
        """
        template = self.get_object()
        data_subject_id = request.data.get('data_subject_id')
        data_subject = None
        
        if data_subject_id:
            try:
                data_subject = DataSubject.objects.get(
                    id=data_subject_id, 
                    organization=request.user.organization
                )
            except DataSubject.DoesNotExist:
                return Response(
                    {'error': 'Data subject not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        request_id = request.data.get('request_id')
        data_request = None
        
        if request_id:
            try:
                data_request = DataSubjectRequest.objects.get(
                    id=request_id, 
                    organization=request.user.organization
                )
            except DataSubjectRequest.DoesNotExist:
                return Response(
                    {'error': 'Data subject request not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Create the workflow instance
        workflow = template.create_workflow_instance(
            data_subject=data_subject,
            request=data_request
        )
        
        serializer = WorkflowInstanceSerializer(workflow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WorkflowStepTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for workflow step templates
    """
    queryset = WorkflowStepTemplate.objects.all()
    serializer_class = WorkflowStepTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        """
        Filter workflow step templates to only show those in the user's organization's workflows
        """
        user = self.request.user
        return WorkflowStepTemplate.objects.filter(
            workflow_template__organization=user.organization
        )


class WorkflowInstanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for workflow instances
    """
    queryset = WorkflowInstance.objects.all()
    serializer_class = WorkflowInstanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        """
        Filter workflow instances to only show those in the user's organization
        """
        user = self.request.user
        return WorkflowInstance.objects.filter(organization=user.organization)
    
    @action(detail=True, methods=['post'])
    def advance(self, request, pk=None):
        """
        Advance the workflow to the next step
        """
        workflow = self.get_object()
        next_step = workflow.advance_to_next_step()
        
        if next_step:
            return Response({
                'status': 'advanced',
                'current_step': WorkflowStepSerializer(next_step).data
            })
        else:
            return Response({
                'status': 'completed',
                'message': 'Workflow has been completed'
            })
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Assign a workflow to a user
        """
        workflow = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id, organization=request.user.organization)
            workflow.assigned_to = user
            workflow.save()
            return Response({'status': 'workflow assigned'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class WorkflowStepViewSet(viewsets.ModelViewSet):
    """
    API endpoint for workflow steps
    """
    queryset = WorkflowStep.objects.all()
    serializer_class = WorkflowStepSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        """
        Filter workflow steps to only show those in the user's organization's workflows
        """
        user = self.request.user
        return WorkflowStep.objects.filter(workflow__organization=user.organization)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark a workflow step as completed
        """
        step = self.get_object()
        notes = request.data.get('notes', '')
        
        if step.status != 'in_progress':
            return Response(
                {'error': 'Can only complete steps that are in progress'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        step.status = 'completed'
        step.completed_date = timezone.now()
        step.result_notes = notes
        step.save()
        
        # Advance the workflow to the next step
        step.workflow.advance_to_next_step()
        
        return Response({'status': 'step completed'})


class AutomatedWorkflowView(views.APIView):
    """
    API endpoint for automated processing of workflows
    """
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]
    
    def post(self, request):
        """
        Process all pending automated steps in workflows
        """
        user = request.user
        org = user.organization
        
        # Find all in-progress workflows with automated current steps
        workflows = WorkflowInstance.objects.filter(
            organization=org,
            status='in_progress',
            current_step__is_automated=True
        )
        
        results = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for workflow in workflows:
            current_step = workflow.current_step
            if not current_step:
                continue
                
            results['processed'] += 1
            step_result = current_step.execute_automation()
            
            if step_result:
                results['successful'] += 1
            else:
                results['failed'] += 1
                
            results['details'].append({
                'workflow_id': str(workflow.id),
                'workflow_name': workflow.name,
                'step_id': str(current_step.id),
                'step_name': current_step.name,
                'success': step_result,
                'notes': current_step.result_notes
            })
        
        return Response(results)


class EnhancedDashboardView(views.APIView):
    """
    API endpoint for enhanced dashboard with GDPR compliance metrics
    """
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get(self, request):
        """
        Get enhanced dashboard data including GDPR-specific metrics
        """
        user = request.user
        org = user.organization
        
        # Basic counts
        data_subjects_count = DataSubject.objects.filter(organization=org).count()
        expiring_soon_count = DataSubject.objects.filter(
            organization=org,
            data_expiry_date__lte=timezone.now() + timezone.timedelta(days=30),
            data_expiry_date__gt=timezone.now()
        ).count()
        
        # Data subject requests
        dsr_counts = {
            'total': DataSubjectRequest.objects.filter(organization=org).count(),
            'pending': DataSubjectRequest.objects.filter(organization=org, status='new').count(),
            'in_progress': DataSubjectRequest.objects.filter(organization=org, status='in_progress').count(),
            'completed': DataSubjectRequest.objects.filter(organization=org, status='completed').count(),
            'overdue': DataSubjectRequest.objects.filter(
                organization=org, 
                status__in=['new', 'in_progress'],
                due_date__lt=timezone.now()
            ).count(),
        }
        
        # Workflows
        workflow_counts = {
            'total': WorkflowInstance.objects.filter(organization=org).count(),
            'pending': WorkflowInstance.objects.filter(organization=org, status='pending').count(),
            'in_progress': WorkflowInstance.objects.filter(organization=org, status='in_progress').count(),
            'completed': WorkflowInstance.objects.filter(organization=org, status='completed').count(),
            'active_templates': WorkflowTemplate.objects.filter(organization=org, is_active=True).count(),
        }
        
        # Document metrics
        document_counts = {
            'total': Document.objects.filter(organization=org).count(),
            'templates': Document.objects.filter(organization=org, is_template=True).count(),
            'active': Document.objects.filter(organization=org, status='active').count(),
            'needs_review': Document.objects.filter(
                organization=org,
                status='active',
                review_date__lte=timezone.now()
            ).count(),
        }
        
        # Consent metrics
        consent_metrics = {
            'marketing_consent': DataSubject.objects.filter(organization=org, marketing_consent=True).count(),
            'data_processing_consent': DataSubject.objects.filter(organization=org, data_processing_consent=True).count(),
            'cookie_consent': DataSubject.objects.filter(organization=org, cookie_consent=True).count(),
            'total_data_subjects': data_subjects_count,
        }
        
        # Recent activities
        recent_consent_activities = ConsentActivity.objects.filter(
            data_subject__organization=org
        ).order_by('-timestamp')[:10]
        
        recent_consent = []
        for activity in recent_consent_activities:
            recent_consent.append({
                'id': str(activity.id),
                'data_subject': f"{activity.data_subject.first_name} {activity.data_subject.last_name}",
                'data_subject_id': str(activity.data_subject.id),
                'activity_type': activity.get_activity_type_display(),
                'consent_type': activity.get_consent_type_display() if activity.consent_type else None,
                'timestamp': activity.timestamp.isoformat(),
            })
        
        return Response({
            'data_subjects': {
                'count': data_subjects_count,
                'expiring_soon': expiring_soon_count,
            },
            'data_subject_requests': dsr_counts,
            'workflows': workflow_counts,
            'documents': document_counts,
            'consent': consent_metrics,
            'recent_consent_activities': recent_consent,
        })
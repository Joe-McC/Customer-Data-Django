from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from api.models import DataSubject, ConsentActivity, Document, WorkflowTemplate, Organization
import logging
import csv
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process data retention policy, anonymize expired data, and generate retention reports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Run in dry run mode - no data will be changed',
        )
        parser.add_argument(
            '--generate-report',
            action='store_true',
            dest='generate_report',
            help='Generate a data retention report',
        )
        parser.add_argument(
            '--notify-expiring',
            action='store_true',
            dest='notify_expiring',
            help='Create notification workflow for subjects with data expiring soon',
        )
        parser.add_argument(
            '--days-before-expiry',
            type=int,
            dest='days_before_expiry',
            default=30,
            help='Number of days before expiry to notify (default: 30)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        generate_report = options['generate_report']
        notify_expiring = options['notify_expiring']
        days_before_expiry = options['days_before_expiry']
        
        now = timezone.now()
        
        # Get expired data subjects
        expired_subjects = DataSubject.objects.filter(
            data_expiry_date__lt=now
        )
        
        # Get subjects expiring soon
        expiring_soon_subjects = DataSubject.objects.filter(
            data_expiry_date__gt=now,
            data_expiry_date__lte=now + timezone.timedelta(days=days_before_expiry)
        )
        
        self.stdout.write(f"Found {expired_subjects.count()} expired data subjects")
        self.stdout.write(f"Found {expiring_soon_subjects.count()} data subjects expiring in the next {days_before_expiry} days")
        
        # Process expired subjects
        if not dry_run:
            self._process_expired_subjects(expired_subjects)
        else:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No data has been modified"))
        
        # Notify about soon-to-expire subjects
        if notify_expiring and not dry_run:
            self._notify_expiring_subjects(expiring_soon_subjects)
        
        # Generate report if requested
        if generate_report:
            self._generate_retention_report(expired_subjects, expiring_soon_subjects, days_before_expiry)
    
    def _process_expired_subjects(self, expired_subjects):
        """Anonymize expired data subjects"""
        counter = 0
        
        for subject in expired_subjects:
            try:
                # Record the anonymization activity
                ConsentActivity.objects.create(
                    data_subject=subject,
                    activity_type='data_deleted',
                    notes='Automated anonymization due to expiry date'
                )
                
                # Anonymize personal data
                subject.first_name = f"Anonymized-{subject.id}"
                subject.last_name = "User"
                subject.email = f"anonymized-{subject.id}@example.com"
                subject.phone = ""
                subject.notes = "This data subject has been anonymized due to data retention policy."
                
                # Remove all consent
                subject.marketing_consent = False
                subject.data_processing_consent = False
                subject.cookie_consent = False
                
                # Set expiry date to None (no longer applicable)
                subject.data_expiry_date = None
                
                subject.save()
                
                # Record anonymization in documents
                for doc in Document.objects.filter(data_subject=subject):
                    doc.content += f"\n\nNOTE: This document relates to a data subject that has been anonymized on {timezone.now().strftime('%Y-%m-%d')} due to data retention policy."
                    doc.save()
                
                counter += 1
                self.stdout.write(f"Anonymized subject: {subject.id}")
            
            except Exception as e:
                logger.error(f"Error processing expired subject {subject.id}: {str(e)}")
                self.stdout.write(self.style.ERROR(f"Error processing subject {subject.id}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f"Successfully anonymized {counter} expired data subjects"))
    
    def _notify_expiring_subjects(self, expiring_subjects):
        """Create workflows to notify subjects with data expiring soon"""
        counter = 0
        
        # Find retention notification workflow template
        try:
            organizations = Organization.objects.all()
            
            for org in organizations:
                workflow_template = WorkflowTemplate.objects.filter(
                    organization=org,
                    workflow_type='retention_notification',
                    is_active=True
                ).first()
                
                if not workflow_template:
                    self.stdout.write(self.style.WARNING(
                        f"No active retention notification workflow template found for organization {org.name}. Skipping notifications."
                    ))
                    continue
                
                # Create workflow for each expiring subject in this organization
                org_subjects = expiring_subjects.filter(organization=org)
                
                for subject in org_subjects:
                    # Create a workflow instance
                    workflow = workflow_template.create_workflow_instance(data_subject=subject)
                    
                    # Start the workflow
                    workflow.status = 'in_progress'
                    workflow.save()
                    workflow.advance_to_next_step()
                    
                    counter += 1
                    self.stdout.write(f"Created notification workflow for subject: {subject.id}")
            
            self.stdout.write(self.style.SUCCESS(f"Successfully created {counter} notification workflows"))
            
        except Exception as e:
            logger.error(f"Error creating notification workflows: {str(e)}")
            self.stdout.write(self.style.ERROR(f"Error creating notification workflows: {str(e)}"))
    
    def _generate_retention_report(self, expired_subjects, expiring_soon_subjects, days_before_expiry):
        """Generate a CSV report of expired and soon-to-expire data subjects"""
        try:
            # Create reports directory if it doesn't exist
            reports_dir = os.path.join(os.getcwd(), 'reports')
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            # Generate filename based on current date
            report_filename = os.path.join(
                reports_dir, 
                f"data_retention_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            with open(report_filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    'Subject ID', 'Organization', 'Name', 'Email', 'Status', 
                    'Expiry Date', 'Data Processing Consent', 'Marketing Consent',
                    'Cookie Consent', 'Created Date'
                ])
                
                # Add expired subjects
                for subject in expired_subjects:
                    writer.writerow([
                        subject.id,
                        subject.organization.name,
                        f"{subject.first_name} {subject.last_name}",
                        subject.email,
                        'EXPIRED',
                        subject.data_expiry_date.strftime('%Y-%m-%d') if subject.data_expiry_date else 'N/A',
                        subject.data_processing_consent,
                        subject.marketing_consent,
                        subject.cookie_consent,
                        subject.created_at.strftime('%Y-%m-%d')
                    ])
                
                # Add soon-to-expire subjects
                for subject in expiring_soon_subjects:
                    writer.writerow([
                        subject.id,
                        subject.organization.name,
                        f"{subject.first_name} {subject.last_name}",
                        subject.email,
                        f'EXPIRING IN <{days_before_expiry} DAYS',
                        subject.data_expiry_date.strftime('%Y-%m-%d') if subject.data_expiry_date else 'N/A',
                        subject.data_processing_consent,
                        subject.marketing_consent,
                        subject.cookie_consent,
                        subject.created_at.strftime('%Y-%m-%d')
                    ])
            
            self.stdout.write(self.style.SUCCESS(f"Generated retention report: {report_filename}"))
            
        except Exception as e:
            logger.error(f"Error generating retention report: {str(e)}")
            self.stdout.write(self.style.ERROR(f"Error generating retention report: {str(e)}")) 
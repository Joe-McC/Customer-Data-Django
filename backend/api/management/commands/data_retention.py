from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from api.models import DataSubject, DataSubjectRequest, ConsentActivity

class Command(BaseCommand):
    help = 'Execute data retention policies based on retention periods'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making any changes',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry-run', False)
        self.stdout.write(self.style.SUCCESS('===== Data Retention Command ====='))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Running in dry-run mode - no changes will be made'))
        
        self.stdout.write('Executing data retention policies...')
        
        processed_expired_consent = self.process_expired_consent(dry_run)
        processed_deletion_requests = self.process_deletion_requests(dry_run)
        processed_retention_limits = self.process_retention_limits(dry_run)
        
        total_processed = processed_expired_consent + processed_deletion_requests + processed_retention_limits
        
        if total_processed == 0:
            self.stdout.write(self.style.SUCCESS('No records found that need processing'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Processed {total_processed} records'))
            
        self.stdout.write(self.style.SUCCESS('Data retention process completed'))
    
    def process_expired_consent(self, dry_run):
        """Process expired consent records"""
        self.stdout.write('Checking for expired consent records...')
        expired_count = 0
        
        try:
            # Get data subjects with expired marketing consent
            expired_marketing = DataSubject.objects.filter(
                marketing_consent=True,
                marketing_consent_date__isnull=False,
                marketing_consent_date__lt=timezone.now() - timedelta(days=730)  # 2 years
            )
            
            if expired_marketing.exists():
                self.stdout.write(f'Found {expired_marketing.count()} expired marketing consent records')
                self.stdout.write(f'Emails: {", ".join([s.email for s in expired_marketing])}')
                
                if not dry_run:
                    with transaction.atomic():
                        for subject in expired_marketing:
                            subject.marketing_consent = False
                            subject.save()
                            
                            # Log the activity
                            ConsentActivity.objects.create(
                                data_subject=subject,
                                activity_type='revoke',
                                consent_type='marketing',
                                notes='Automatically expired by data retention process'
                            )
                            expired_count += 1
                else:
                    expired_count += expired_marketing.count()
                    self.stdout.write(self.style.WARNING(f'Would revoke marketing consent for {expired_marketing.count()} records'))
            else:
                self.stdout.write('No expired marketing consent records found')
                
            return expired_count
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing expired consent: {str(e)}'))
            return 0
    
    def process_deletion_requests(self, dry_run):
        """Process pending deletion requests"""
        self.stdout.write('Checking for pending deletion requests...')
        processed_count = 0
        
        try:
            # Get pending deletion requests that are older than 30 days
            pending_requests = DataSubjectRequest.objects.filter(
                request_type='deletion',
                status='pending',
                date_received__lt=timezone.now() - timedelta(days=30)
            )
            
            if pending_requests.exists():
                self.stdout.write(f'Found {pending_requests.count()} pending deletion requests')
                
                if not dry_run:
                    with transaction.atomic():
                        for request in pending_requests:
                            # Get the data subject
                            try:
                                data_subject = DataSubject.objects.get(email=request.data_subject_email)
                                
                                # Process deletion - in a real application, this would anonymize the data
                                data_subject.first_name = '[DELETED]'
                                data_subject.last_name = '[DELETED]'
                                data_subject.phone = '[DELETED]'
                                data_subject.marketing_consent = False
                                data_subject.data_processing_consent = False
                                data_subject.cookie_consent = False
                                data_subject.notes = 'Data deleted per user request'
                                data_subject.save()
                                
                                # Update the request status
                                request.status = 'completed'
                                request.completed_date = timezone.now()
                                request.notes = f'{request.notes}\nAutomatically processed by data retention job'
                                request.save()
                                
                                processed_count += 1
                            except DataSubject.DoesNotExist:
                                self.stdout.write(self.style.WARNING(f'No data subject found for email {request.data_subject_email}'))
                                request.status = 'rejected'
                                request.notes = f'{request.notes}\nNo matching data subject found'
                                request.save()
                else:
                    processed_count += pending_requests.count()
                    self.stdout.write(self.style.WARNING(f'Would process {pending_requests.count()} deletion requests'))
            else:
                self.stdout.write('No pending deletion requests found')
                
            return processed_count
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing deletion requests: {str(e)}'))
            return 0
    
    def process_retention_limits(self, dry_run):
        """Process data beyond retention period"""
        self.stdout.write('Checking for data beyond retention period...')
        processed_count = 0
        
        try:
            # Find data subjects with expired data_expiry_date
            expired_data = DataSubject.objects.filter(
                data_expiry_date__lt=timezone.now(),
                data_expiry_date__isnull=False
            )
            
            if expired_data.exists():
                self.stdout.write(f'Found {expired_data.count()} records beyond retention period')
                
                if not dry_run:
                    with transaction.atomic():
                        for subject in expired_data:
                            # Process deletion - in a real application, this would anonymize the data
                            subject.first_name = '[EXPIRED]'
                            subject.last_name = '[EXPIRED]'
                            subject.phone = '[EXPIRED]'
                            subject.email = f'expired-{subject.id}@example.com'  # Anonymize email but keep a reference
                            subject.marketing_consent = False
                            subject.data_processing_consent = False
                            subject.cookie_consent = False
                            subject.notes = 'Data expired due to retention policy'
                            subject.save()
                            
                            processed_count += 1
                else:
                    processed_count += expired_data.count()
                    self.stdout.write(self.style.WARNING(f'Would anonymize {expired_data.count()} expired records'))
            else:
                self.stdout.write('No records found beyond retention period')
                
            return processed_count
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing retention limits: {str(e)}'))
            return 0 
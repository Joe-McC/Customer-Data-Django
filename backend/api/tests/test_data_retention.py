import pytest
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta
from io import StringIO
from api.models import ConsentRecord, DataSubject, ProcessingActivity
from api.management.commands.data_retention import Command

@pytest.mark.django_db
class TestDataRetention:
    def test_expired_consent_records(self):
        """Test that expired consent records are properly processed"""
        # Create test data
        now = timezone.now()
        
        # Create an active consent record that's expired
        ConsentRecord.objects.create(
            data_subject_id="test-subject-1",
            purpose="Marketing",
            expiration_date=now - timedelta(days=1),
            is_active=True
        )
        
        # Create an active consent record that's not expired
        ConsentRecord.objects.create(
            data_subject_id="test-subject-2",
            purpose="Marketing",
            expiration_date=now + timedelta(days=30),
            is_active=True
        )
        
        # Run the command
        out = StringIO()
        call_command('data_retention', stdout=out)
        
        # Check the results
        output = out.getvalue()
        assert 'Found 1 expired consent records' in output
        assert 'Marked 1 consent records as expired' in output
        
        # Verify database state
        assert ConsentRecord.objects.filter(is_active=False).count() == 1
        assert ConsentRecord.objects.filter(is_active=True).count() == 1
    
    def test_deletion_requests(self):
        """Test that deletion requests are properly processed"""
        # Create a data subject with deletion requested
        data_subject = DataSubject.objects.create(
            email="test@example.com",
            name="Test User",
            phone_number="123-456-7890",
            address="123 Test St",
            deletion_requested=True,
            deletion_processed=False
        )
        
        # Run the command
        out = StringIO()
        call_command('data_retention', stdout=out)
        
        # Check the results
        output = out.getvalue()
        assert 'Found 1 data subjects pending deletion' in output
        assert 'Processed 1 deletion requests' in output
        
        # Verify database state
        data_subject.refresh_from_db()
        assert data_subject.deletion_processed is True
        assert data_subject.name == f"Deleted User {data_subject.id}"
        assert data_subject.email == f"deleted-{data_subject.id}@anonymous.com"
        assert data_subject.phone_number == ""
        assert data_subject.address == ""
    
    def test_retention_limits(self, settings):
        """Test that old data is archived based on retention limits"""
        # Set a short retention period for testing
        settings.DATA_RETENTION_PERIOD_DAYS = 30
        
        # Create an old processing activity
        ProcessingActivity.objects.create(
            purpose="Test Activity",
            description="A test processing activity",
            created_at=timezone.now() - timedelta(days=60),
            archived=False
        )
        
        # Create a recent processing activity
        ProcessingActivity.objects.create(
            purpose="Recent Activity",
            description="A recent processing activity",
            created_at=timezone.now() - timedelta(days=10),
            archived=False
        )
        
        # Run the command
        out = StringIO()
        call_command('data_retention', stdout=out)
        
        # Check the results
        output = out.getvalue()
        assert 'Found 1 processing activities older than 30 days' in output
        assert 'Archived 1 old processing activities' in output
        
        # Verify database state
        assert ProcessingActivity.objects.filter(archived=True).count() == 1
        assert ProcessingActivity.objects.filter(archived=False).count() == 1
    
    def test_dry_run_mode(self):
        """Test that dry run mode doesn't modify data"""
        # Create test data
        now = timezone.now()
        
        # Create an expired consent record
        ConsentRecord.objects.create(
            data_subject_id="test-subject-1",
            purpose="Marketing",
            expiration_date=now - timedelta(days=1),
            is_active=True
        )
        
        # Run the command in dry run mode
        out = StringIO()
        call_command('data_retention', '--dry-run', stdout=out)
        
        # Check the results
        output = out.getvalue()
        assert 'Running in dry-run mode - no changes will be made' in output
        assert 'Found 1 expired consent records' in output
        
        # Verify database state (should be unchanged)
        assert ConsentRecord.objects.filter(is_active=True).count() == 1
        assert ConsentRecord.objects.filter(is_active=False).count() == 0 
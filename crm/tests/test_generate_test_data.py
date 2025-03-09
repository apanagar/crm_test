from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User
from django.utils import timezone
from crm.models import Account, Opportunity, EmailCommunication
from crm.management.commands.generate_test_data import Command
from io import StringIO
from datetime import timedelta
import decimal

class GenerateTestDataCommandTest(TestCase):
    """Test cases for the generate_test_data management command."""

    def setUp(self):
        """Set up test environment."""
        self.command = Command()
        self.stdout = StringIO()
        self.command.stdout = self.stdout

    def test_create_test_user(self):
        """Test creation of test user."""
        # Test user creation
        user = self.command.create_test_user()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

        # Test idempotency (should not create duplicate user)
        user_count = User.objects.count()
        self.command.create_test_user()
        self.assertEqual(User.objects.count(), user_count)

    def test_create_accounts(self):
        """Test account creation with predefined company data."""
        user = self.command.create_test_user()
        accounts = self.command.create_accounts(user)

        # Test number of accounts created
        self.assertEqual(len(accounts), len(self.command.COMPANIES))

        # Test account properties
        for account, (company_name, industry) in zip(accounts, self.command.COMPANIES):
            self.assertEqual(account.name, company_name)
            self.assertEqual(account.industry, industry)
            self.assertEqual(account.account_owner, user)
            self.assertIsInstance(float(account.annual_revenue), float)
            self.assertGreaterEqual(account.annual_revenue, 1000000)
            self.assertLessEqual(account.annual_revenue, 10000000)

    def test_create_opportunities(self):
        """Test opportunity creation with realistic distribution."""
        user = self.command.create_test_user()
        accounts = self.command.create_accounts(user)
        total_opps = 100
        
        # Create opportunities
        self.command.create_opportunities(accounts, user, total_opps)
        
        # Test total number of opportunities
        self.assertEqual(Opportunity.objects.count(), total_opps)

        # Test stage distribution
        for stage, probability, _ in self.command.OPPORTUNITY_STAGES:
            expected_count = int(total_opps * probability)
            actual_count = Opportunity.objects.filter(stage=stage).count()
            # Allow for small variance due to random selection
            self.assertAlmostEqual(actual_count, expected_count, delta=2)

        # Test opportunity properties
        for opp in Opportunity.objects.all():
            self.assertIn(opp.account, accounts)
            self.assertEqual(opp.owner, user)
            self.assertIsInstance(opp.amount, decimal.Decimal)
            self.assertGreater(opp.probability, 0)
            self.assertLessEqual(opp.probability, 90)
            self.assertGreater(opp.close_date, timezone.now().date())

    def test_create_email_communications(self):
        """Test email communication creation."""
        user = self.command.create_test_user()
        accounts = self.command.create_accounts(user)
        
        # Create email communications
        self.command.create_email_communications(accounts, user)
        
        # Test email count (5-10 per account)
        min_expected = len(accounts) * 5
        max_expected = len(accounts) * 10
        total_emails = EmailCommunication.objects.count()
        self.assertGreaterEqual(total_emails, min_expected)
        self.assertLessEqual(total_emails, max_expected)

        # Test email properties
        for email in EmailCommunication.objects.all():
            # Test basic properties
            self.assertIn(email.account, accounts)
            self.assertEqual(email.owner, user)
            self.assertIn(email.direction, ['inbound', 'outbound'])
            self.assertIn(email.subject, self.command.EMAIL_SUBJECTS)
            
            # Test email addresses
            if email.direction == 'outbound':
                self.assertEqual(email.sender, 'sales@ourcompany.com')
                self.assertTrue(email.recipients.startswith('contact@'))
            else:
                self.assertTrue(email.sender.startswith('contact@'))
                self.assertEqual(email.recipients, 'sales@ourcompany.com')

            # Test dates
            self.assertLess(email.sent_date, timezone.now())
            self.assertGreater(
                email.sent_date,
                timezone.now() - timedelta(days=31)
            )

            # Test follow-up data
            if email.requires_follow_up:
                self.assertIsNotNone(email.follow_up_date)
                self.assertIn(email.follow_up_notes, self.command.FOLLOW_UP_NOTES)
                self.assertFalse(email.follow_up_completed)
            else:
                self.assertIsNone(email.follow_up_date)
                self.assertEqual(email.follow_up_notes, '')

    def test_full_command_execution(self):
        """Test full command execution through call_command."""
        # Execute command
        call_command('generate_test_data', stdout=self.stdout)

        # Verify data was created
        self.assertGreater(User.objects.count(), 0)
        self.assertGreater(Account.objects.count(), 0)
        self.assertGreater(Opportunity.objects.count(), 0)
        self.assertGreater(EmailCommunication.objects.count(), 0)

        # Check for success message
        self.assertIn('Successfully generated test data', self.stdout.getvalue())

    def test_email_generation_helpers(self):
        """Test helper methods for email generation."""
        user = self.command.create_test_user()
        account = Account.objects.create(
            name='Test Corp',
            account_owner=user
        )

        # Test sender email generation
        sender_outbound = self.command._get_sender_email('outbound', account)
        self.assertEqual(sender_outbound, 'sales@ourcompany.com')
        
        sender_inbound = self.command._get_sender_email('inbound', account)
        self.assertEqual(sender_inbound, 'contact@testcorp.com')

        # Test recipient email generation
        recipient_outbound = self.command._get_recipient_email('outbound', account)
        self.assertEqual(recipient_outbound, 'contact@testcorp.com')
        
        recipient_inbound = self.command._get_recipient_email('inbound', account)
        self.assertEqual(recipient_inbound, 'sales@ourcompany.com')

        # Test follow-up data generation
        sent_date = timezone.now()
        follow_up_data = self.command._generate_follow_up_data(sent_date)
        
        if follow_up_data['requires_follow_up']:
            self.assertIsNotNone(follow_up_data['follow_up_date'])
            self.assertIn(follow_up_data['follow_up_notes'], self.command.FOLLOW_UP_NOTES)
        else:
            self.assertIsNone(follow_up_data['follow_up_date'])
            self.assertEqual(follow_up_data['follow_up_notes'], '') 
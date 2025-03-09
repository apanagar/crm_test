from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from crm.models import Account, Contact, Opportunity, EmailCommunication
from django.utils import timezone
from datetime import timedelta
import random
import decimal
from typing import List, Tuple, Dict, Any

class Command(BaseCommand):
    """Management command to generate test data for the CRM system."""

    help = 'Generates test data for the CRM including accounts, opportunities, and email communications'

    # Test data constants
    COMPANIES = [
        ('Acme Corp', 'technology'),
        ('Global Industries', 'manufacturing'),
        ('HealthTech Solutions', 'healthcare'),
        ('Finance Plus', 'finance'),
        ('Retail Giants', 'retail'),
        ('Tech Innovators', 'technology'),
        ('Manufacturing Pro', 'manufacturing'),
        ('MediCare Systems', 'healthcare'),
        ('Investment Solutions', 'finance'),
        ('Shop Express', 'retail')
    ]

    OPPORTUNITY_STAGES = [
        ('prospecting', 0.3, (5000, 50000)),
        ('qualification', 0.2, (10000, 100000)),
        ('needs_analysis', 0.15, (20000, 150000)),
        ('value_proposition', 0.15, (30000, 200000)),
        ('negotiation', 0.1, (40000, 250000)),
        ('closed_won', 0.07, (50000, 300000)),
        ('closed_lost', 0.03, (20000, 150000))
    ]

    EMAIL_SUBJECTS = [
        "Product Demo Request",
        "Pricing Discussion",
        "Meeting Follow-up",
        "Project Timeline",
        "Contract Review",
        "Technical Questions",
        "Partnership Opportunity",
        "Service Upgrade",
        "Support Request",
        "Feature Inquiry"
    ]

    EMAIL_TEMPLATES = [
        "Thank you for your interest in our {product}. I'd be happy to schedule a demo at your convenience.",
        "I've reviewed your requirements and attached a detailed pricing proposal for your consideration.",
        "It was great meeting with you today. Here's a summary of our discussion and next steps.",
        "Based on our timeline discussion, I've outlined the key milestones and deliverables.",
        "I've attached the revised contract incorporating your requested changes.",
        "Here are the technical specifications you requested for {product}.",
        "I believe there's a great opportunity for partnership between our organizations.",
        "I noticed you might benefit from upgrading to our premium service tier.",
        "I'm following up on your support request regarding {product}.",
        "Here are the details about the features you inquired about."
    ]

    FOLLOW_UP_NOTES = [
        "Schedule follow-up call",
        "Send additional information",
        "Get technical team involved",
        "Review proposal with team",
        "Discuss timeline adjustments"
    ]

    PRODUCTS = ['Product A', 'Service B', 'Solution C', 'Platform D']

    def create_test_user(self) -> User:
        """Create a test user if none exists."""
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created test user'))
        return user

    def create_accounts(self, user: User) -> List[Account]:
        """Create test accounts with predefined company names and industries."""
        accounts = []
        for company_name, industry in self.COMPANIES:
            account, created = Account.objects.get_or_create(
                name=company_name,
                defaults={
                    'industry': industry,
                    'account_owner': user,
                    'annual_revenue': decimal.Decimal(random.randint(1000000, 10000000))
                }
            )
            accounts.append(account)
            if created:
                self.stdout.write(f'Created account: {account.name}')
        return accounts

    def create_opportunities(self, accounts: List[Account], user: User, total_opps: int = 100):
        """Create opportunities with realistic distribution across stages."""
        Opportunity.objects.all().delete()

        for stage, probability, amount_range in self.OPPORTUNITY_STAGES:
            num_opps = int(total_opps * probability)
            for _ in range(num_opps):
                account = random.choice(accounts)
                self._create_single_opportunity(account, stage, amount_range, user)

    def _create_single_opportunity(self, account: Account, stage: str, amount_range: Tuple[int, int], user: User):
        """Helper method to create a single opportunity."""
        amount = decimal.Decimal(random.randint(amount_range[0], amount_range[1]))
        close_date = timezone.now() + timedelta(days=random.randint(30, 180))
        
        Opportunity.objects.create(
            name=f"{account.name} - {random.choice(self.PRODUCTS)}",
            account=account,
            amount=amount,
            stage=stage,
            probability=random.randint(20, 90),
            close_date=close_date,
            owner=user
        )

    def create_email_communications(self, accounts: List[Account], user: User):
        """Create email communications for each account."""
        EmailCommunication.objects.all().delete()

        for account in accounts:
            num_emails = random.randint(5, 10)
            for _ in range(num_emails):
                self._create_single_email_communication(account, user)

    def _create_single_email_communication(self, account: Account, user: User):
        """Helper method to create a single email communication."""
        direction = random.choice(['inbound', 'outbound'])
        subject = random.choice(self.EMAIL_SUBJECTS)
        body = random.choice(self.EMAIL_TEMPLATES).format(product=random.choice(self.PRODUCTS))
        sent_date = timezone.now() - timedelta(days=random.randint(1, 30))
        
        follow_up_data = self._generate_follow_up_data(sent_date)
        
        EmailCommunication.objects.create(
            account=account,
            direction=direction,
            subject=subject,
            body=body,
            sent_date=sent_date,
            sender=self._get_sender_email(direction, account),
            recipients=self._get_recipient_email(direction, account),
            requires_follow_up=follow_up_data['requires_follow_up'],
            follow_up_date=follow_up_data['follow_up_date'],
            follow_up_notes=follow_up_data['follow_up_notes'],
            follow_up_completed=False,
            owner=user
        )

    def _generate_follow_up_data(self, sent_date: timezone.datetime) -> Dict[str, Any]:
        """Generate follow-up related data for email communications."""
        requires_follow_up = random.random() < 0.3  # 30% chance of needing follow-up
        
        if not requires_follow_up:
            return {
                'requires_follow_up': False,
                'follow_up_date': None,
                'follow_up_notes': ""
            }
        
        return {
            'requires_follow_up': True,
            'follow_up_date': (sent_date + timedelta(days=random.randint(3, 14))).date(),
            'follow_up_notes': random.choice(self.FOLLOW_UP_NOTES)
        }

    def _get_sender_email(self, direction: str, account: Account) -> str:
        """Get sender email based on communication direction."""
        return ('sales@ourcompany.com' if direction == 'outbound' 
                else f'contact@{account.name.lower().replace(" ", "")}.com')

    def _get_recipient_email(self, direction: str, account: Account) -> str:
        """Get recipient email based on communication direction."""
        return (f'contact@{account.name.lower().replace(" ", "")}.com' if direction == 'outbound'
                else 'sales@ourcompany.com')

    def handle(self, *args, **kwargs):
        """Main command handler."""
        # Create test user
        user = self.create_test_user()

        # Create accounts
        accounts = self.create_accounts(user)

        # Create opportunities
        self.create_opportunities(accounts, user)

        # Create email communications
        self.create_email_communications(accounts, user)

        self.stdout.write(self.style.SUCCESS('Successfully generated test data')) 
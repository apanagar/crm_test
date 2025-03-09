# Generated by Django 5.1.7 on 2025-03-09 03:46

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0003_approvalprocess_approvalstep_approvalrequest_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailCommunication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direction', models.CharField(choices=[('inbound', 'Inbound'), ('outbound', 'Outbound')], max_length=10)),
                ('subject', models.CharField(max_length=200)),
                ('body', models.TextField()),
                ('sent_date', models.DateTimeField()),
                ('sender', models.EmailField(max_length=254)),
                ('recipients', models.TextField(help_text='Comma-separated list of email addresses')),
                ('requires_follow_up', models.BooleanField(default=False)),
                ('follow_up_date', models.DateField(blank=True, null=True)),
                ('follow_up_notes', models.TextField(blank=True)),
                ('follow_up_completed', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='communications', to='crm.account')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='communications', to='crm.contact')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-sent_date'],
            },
        ),
    ]

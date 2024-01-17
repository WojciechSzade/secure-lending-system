# Generated by Django 4.2.7 on 2024-01-16 17:32

from django.db import migrations, models
import uuid


def gen_uuid(apps, schema_editor):
    User = apps.get_model('sls', 'User')
    for user in User.objects.all():
        user.account_number = uuid.uuid4()
        user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('sls', '0002_transfer_executed_transfer_valid_transfer_validated_and_more'),
    ]

    operations = [
                migrations.RunPython(gen_uuid),
    ]
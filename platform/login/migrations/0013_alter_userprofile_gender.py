# Generated by Django 5.0.4 on 2024-05-16 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0012_remove_hiddenprofile_is_deleted_deletedprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Others')], max_length=1, null=True),
        ),
    ]

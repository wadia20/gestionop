# Generated by Django 5.0.4 on 2024-07-31 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employe', '0013_alter_companyinfo_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyinfo',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='logos/', verbose_name='Logo'),
        ),
    ]

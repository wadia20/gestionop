# Generated by Django 5.0.4 on 2024-07-31 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employe', '0012_alter_companyinfo_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyinfo',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Logo'),
        ),
    ]

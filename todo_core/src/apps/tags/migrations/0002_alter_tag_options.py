# Generated by Django 5.1.1 on 2024-09-08 10:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'verbose_name_plural': 'tags'},
        ),
    ]

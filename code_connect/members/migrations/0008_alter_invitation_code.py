# Generated by Django 5.0.3 on 2024-03-11 19:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0007_invitation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invitation",
            name="code",
            field=models.CharField(blank=True, max_length=10, unique=True),
        ),
    ]

# Generated by Django 5.0.3 on 2024-03-29 08:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0011_invitation_accepted_invitation_sent_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invitation",
            name="sent_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

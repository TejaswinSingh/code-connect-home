# Generated by Django 5.0.3 on 2024-03-23 06:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0008_alter_invitation_code"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="invitation",
            name="user",
        ),
        migrations.AddField(
            model_name="invitation",
            name="mail_address",
            field=models.EmailField(
                default="jatt43@gmail.com", max_length=100, unique=True
            ),
            preserve_default=False,
        ),
    ]

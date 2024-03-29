# Generated by Django 5.0.3 on 2024-03-08 23:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0002_alter_member_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="member",
            name="programme",
            field=models.CharField(
                choices=[
                    ("CSE", "Computer Science & Engineering"),
                    ("CCS", "Computer Science & Cyber Security"),
                    ("ECE", "Electronics and Communication Engineering"),
                    ("AVI", "Avionics"),
                ],
                default="",
                max_length=3,
            ),
        ),
        migrations.AlterField(
            model_name="member",
            name="semester",
            field=models.CharField(
                choices=[
                    ("1", "1st Semester"),
                    ("2", "2nd Semester"),
                    ("3", "3rd Semester"),
                    ("4", "4th Semester"),
                    ("5", "5th Semester"),
                    ("6", "6th Semester"),
                    ("7", "7th Semester"),
                    ("8", "8th Semester"),
                ],
                default="",
                max_length=1,
            ),
        ),
    ]

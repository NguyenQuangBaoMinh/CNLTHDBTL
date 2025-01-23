# Generated by Django 5.1.5 on 2025-01-22 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialmediabook', '0002_question_alter_user_options_userprofile_location_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='profileimg',
        ),
        migrations.AddField(
            model_name='user',
            name='profileimg',
            field=models.ImageField(default='blank=profile', upload_to='UserProfiles/%Y/%m'),
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='Posts/%Y/%m'),
        ),
    ]

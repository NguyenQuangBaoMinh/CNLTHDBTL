# Generated by Django 5.1.5 on 2025-01-24 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialmediabook', '0005_alter_comment_content_alter_post_content_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_public',
            field=models.BooleanField(default=True),
        ),
    ]

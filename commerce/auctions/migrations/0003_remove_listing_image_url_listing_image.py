# Generated by Django 4.1.3 on 2023-06-30 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_category_listing_comment_bid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='image_url',
        ),
        migrations.AddField(
            model_name='listing',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='listing_images/'),
        ),
    ]

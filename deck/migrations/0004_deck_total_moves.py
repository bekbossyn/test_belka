# Generated by Django 2.0 on 2018-02-28 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deck', '0003_remove_deck_moves'),
    ]

    operations = [
        migrations.AddField(
            model_name='deck',
            name='total_moves',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

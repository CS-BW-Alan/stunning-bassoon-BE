# Generated by Django 3.0.3 on 2020-03-06 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adventure', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='color',
            field=models.CharField(default='gold', max_length=50),
        ),
    ]
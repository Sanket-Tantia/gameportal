# Generated by Django 3.0.4 on 2020-03-28 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrantedToken',
            fields=[
                ('session', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('granted_token', models.PositiveIntegerField()),
            ],
        ),
    ]
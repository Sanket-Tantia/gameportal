# Generated by Django 3.0.4 on 2020-03-22 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_gameround'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tokentransaction',
            name='transaction_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
# Generated by Django 2.2.19 on 2022-06-19 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20220619_1949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ipaddres',
            name='ip',
            field=models.CharField(max_length=50),
        ),
    ]

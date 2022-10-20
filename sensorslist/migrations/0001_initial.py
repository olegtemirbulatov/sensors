# Generated by Django 4.1.1 on 2022-10-19 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('user', models.CharField(max_length=30)),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
            ],
        ),
    ]

# Generated by Django 3.2.8 on 2021-10-16 13:14

import auth_app.models
from django.db import migrations, models
import enumchoicefield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=80, unique=True)),
                ('country_code', models.CharField(max_length=11)),
                ('contact_num', models.IntegerField()),
                ('password', models.CharField(max_length=256)),
                ('usertype', enumchoicefield.fields.EnumChoiceField(default=auth_app.models.UserType(1), enum_class=auth_app.models.UserType, max_length=20)),
            ],
            options={
                'db_table': 'user',
            },
        ),
    ]
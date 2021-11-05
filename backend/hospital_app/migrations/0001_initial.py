# Generated by Django 3.2.8 on 2021-11-03 06:54

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import enumchoicefield.fields
import hospital_app.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area', models.CharField(max_length=100)),
                ('address', models.TextField()),
                ('landmark', models.TextField()),
                ('zipcode', models.IntegerField()),
                ('country_code', models.CharField(max_length=11)),
                ('phone', models.BigIntegerField()),
                ('is_default', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CheckupAppointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('desired_date', models.DateField()),
                ('desired_time', models.CharField(max_length=256)),
                ('sample_collection_time', models.DateTimeField()),
                ('expected_delivery_date', models.DateField()),
                ('actual_delivery_time', models.DateTimeField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Pathlab',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pathlab_name', models.CharField(max_length=100)),
                ('details', models.TextField(blank=True)),
                ('contact_details', models.TextField(blank=True)),
                ('additional_details', models.TextField(blank=True)),
                ('address', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='hospital_app.address')),
                ('pathlab_admin', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('hospital_name', models.CharField(max_length=100)),
                ('details', models.TextField(blank=True)),
                ('contact_details', models.TextField(blank=True)),
                ('additional_details', models.TextField(blank=True)),
                ('address', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='hospital_app.address')),
                ('hospital_admin', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CheckupStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', enumchoicefield.fields.EnumChoiceField(default=hospital_app.models.CheckupAppointmentStatus['CREATED'], enum_class=hospital_app.models.CheckupAppointmentStatus, max_length=9)),
                ('remark', models.CharField(blank=True, max_length=256)),
                ('checkup_appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hospital_app.checkupappointment')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Checkupreports',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('files_paths', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), size=None)),
                ('remark', models.TextField()),
                ('checkup_appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hospital_app.checkupappointment')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CheckupPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', enumchoicefield.fields.EnumChoiceField(enum_class=hospital_app.models.CheckupPlanTypes, max_length=17)),
                ('home_sample_collection', models.BooleanField()),
                ('timing', models.CharField(max_length=256)),
                ('available_days', django.contrib.postgres.fields.ArrayField(base_field=enumchoicefield.fields.EnumChoiceField(enum_class=hospital_app.models.Weekday, max_length=9), size=None)),
                ('plan_name', models.CharField(max_length=256)),
                ('description', models.TextField(blank=True)),
                ('additional_details', models.TextField(blank=True)),
                ('charges', models.FloatField()),
                ('hospital', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hospital_app.hospital')),
                ('pathlab', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hospital_app.pathlab')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CheckupDefalutTiming',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('day_name', enumchoicefield.fields.EnumChoiceField(enum_class=hospital_app.models.Weekday, max_length=9)),
                ('start_hour', models.PositiveIntegerField()),
                ('start_minute', models.PositiveIntegerField()),
                ('start_period', enumchoicefield.fields.EnumChoiceField(enum_class=hospital_app.models.SlotPeriod, max_length=2)),
                ('end_hour', models.PositiveIntegerField()),
                ('end_minute', models.PositiveIntegerField()),
                ('end_period', enumchoicefield.fields.EnumChoiceField(enum_class=hospital_app.models.SlotPeriod, max_length=2)),
                ('checkup_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hospital_app.checkupplan')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='checkupappointment',
            name='checkup_plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hospital_app.checkupplan'),
        ),
        migrations.AddField(
            model_name='checkupappointment',
            name='original_checkupappointment_ref',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='original_checkup_appointment_ref', to='hospital_app.checkupappointment'),
        ),
        migrations.AddField(
            model_name='address',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hospital_app.city'),
        ),
    ]

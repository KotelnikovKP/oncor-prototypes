# Generated by Django 4.2.4 on 2023-09-09 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_semddiagnosis_rc_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='SemdService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ptn_id', models.CharField(db_index=True, max_length=16, verbose_name='Patient @rid')),
                ('ptn_code', models.CharField(max_length=16, null=True, verbose_name='Patient extra abbreviation')),
                ('ptn_tags', models.JSONField(null=True, verbose_name='Patient tags')),
                ('rc_id', models.CharField(db_index=True, max_length=16, verbose_name='SEMD record @rid')),
                ('time_rc', models.DateTimeField(null=True, verbose_name='SEMD time')),
                ('document_type', models.CharField(max_length=8, null=True, verbose_name='SEMD type')),
                ('nsi_doc_type', models.CharField(max_length=8, null=True, verbose_name='SEMD nsi type')),
                ('profile', models.CharField(max_length=8, null=True, verbose_name='SEMD profile')),
                ('author_mo_oid', models.CharField(max_length=64, null=True, verbose_name='SEMD author MO OID')),
                ('author_snils', models.CharField(max_length=14, null=True, verbose_name='SEMD author SNILS')),
                ('author_post', models.CharField(max_length=64, null=True, verbose_name='SEMD author post OID')),
                ('internal_message_id', models.CharField(max_length=64, null=True, verbose_name='SEMD internal_message_id')),
                ('external_message_id', models.CharField(max_length=64, null=True, verbose_name='SEMD external_message_id')),
                ('service_code', models.CharField(db_index=True, max_length=20, verbose_name='Service code')),
                ('service_date', models.DateField(null=True, verbose_name='Service date')),
                ('instrumental_diagnostics_code', models.CharField(max_length=10, null=True, verbose_name='Instrumental diagnostics code')),
            ],
            options={
                'verbose_name': 'Patient-SEMD-service',
                'verbose_name_plural': 'Patient-SEMD-service cube',
                'ordering': ['id'],
                'indexes': [models.Index(fields=['ptn_id', 'service_code', 'service_date'], name='api_semdservice_ptn_srv_dat')],
            },
        ),
    ]

# Generated by Django 4.2.4 on 2023-09-09 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_semddiagnosis_rc_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='semddiagnosis',
            name='rc_id',
            field=models.CharField(max_length=16, verbose_name='SEMD record @rid'),
        ),
        migrations.AddIndex(
            model_name='semddiagnosis',
            index=models.Index(fields=['ptn_id', 'diagnosis_mkb10', 'diagnosis_date'], name='api_semddiagnosis_ptn_dz_dat'),
        ),
    ]

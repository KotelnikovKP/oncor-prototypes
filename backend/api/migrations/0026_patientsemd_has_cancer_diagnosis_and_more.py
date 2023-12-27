# Generated by Django 4.2.4 on 2023-12-03 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_patientsemd_content_error'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientsemd',
            name='has_cancer_diagnosis',
            field=models.BooleanField(default=False, verbose_name='Patient has cancer diagnosis flag'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patientsemd',
            name='has_precancer_diagnosis',
            field=models.BooleanField(default=False, verbose_name='Patient has precancer diagnosis flag'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patientsemd',
            name='is_cancer_diagnoses',
            field=models.BooleanField(default=False, verbose_name='Cancer diagnoses flag'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patientsemd',
            name='is_cancer_diagnosis',
            field=models.BooleanField(default=False, verbose_name='Cancer diagnosis flag'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patientsemd',
            name='is_precancer_diagnoses',
            field=models.BooleanField(default=False, verbose_name='Precancer diagnoses flag'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patientsemd',
            name='is_precancer_diagnosis',
            field=models.BooleanField(default=False, verbose_name='Precancer diagnosis flag'),
            preserve_default=False,
        ),
    ]

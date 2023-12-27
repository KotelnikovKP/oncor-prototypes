# Generated by Django 4.2.4 on 2023-11-27 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_patientdiagnosismilestones_api_p_d_milestones_ptn_dat'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='birthday',
            field=models.DateField(null=True, verbose_name='Patient birthday'),
        ),
        migrations.AddField(
            model_name='patient',
            name='code',
            field=models.CharField(max_length=16, null=True, verbose_name='Patient extra abbreviation'),
        ),
        migrations.AddField(
            model_name='patient',
            name='firstname',
            field=models.CharField(max_length=255, null=True, verbose_name='Patient first name'),
        ),
        migrations.AddField(
            model_name='patient',
            name='gender',
            field=models.CharField(max_length=1, null=True, verbose_name='Patient gender'),
        ),
        migrations.AddField(
            model_name='patient',
            name='lastname',
            field=models.CharField(max_length=255, null=True, verbose_name='Patient last name'),
        ),
        migrations.AddField(
            model_name='patient',
            name='med_terr',
            field=models.CharField(max_length=255, null=True, verbose_name='Patient medical territory'),
        ),
        migrations.AddField(
            model_name='patient',
            name='middlename',
            field=models.CharField(max_length=255, null=True, verbose_name='Patient middle name'),
        ),
        migrations.AddField(
            model_name='patient',
            name='mo_oid',
            field=models.CharField(max_length=64, null=True, verbose_name='Patient assigned clinic oid'),
        ),
        migrations.AddField(
            model_name='patient',
            name='snils',
            field=models.CharField(max_length=14, null=True, verbose_name='Patient SNILS'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='rid',
            field=models.CharField(max_length=16, primary_key=True, serialize=False, verbose_name='Patient rid'),
        ),
    ]

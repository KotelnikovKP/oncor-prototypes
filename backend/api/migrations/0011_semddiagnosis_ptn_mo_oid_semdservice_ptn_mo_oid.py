# Generated by Django 4.2.4 on 2023-09-11 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_oncorsettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='semddiagnosis',
            name='ptn_mo_oid',
            field=models.CharField(max_length=64, null=True, verbose_name='Patient MO OID'),
        ),
        migrations.AddField(
            model_name='semdservice',
            name='ptn_mo_oid',
            field=models.CharField(max_length=64, null=True, verbose_name='Patient MO OID'),
        ),
    ]
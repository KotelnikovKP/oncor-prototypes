from django.db import models
from django.db.models import Index


class DiagnosisRegistry(models.Model):
    name = models.CharField(max_length=150, verbose_name='Diagnosis registry name', blank=True, null=True)
    short_name = models.CharField(max_length=25, verbose_name='Diagnosis registry short name', blank=True, null=True)
    oncor_tag_rid = models.CharField(max_length=25, verbose_name='Oncor tag @rid', blank=True, null=True)
    medical_record_transcript_settings = \
        models.JSONField(verbose_name='Settings of medical record transcript', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Diagnosis registry'
        verbose_name_plural = 'Diagnosis registers'
        ordering = ['name']
        indexes = (
            Index(fields=['name'], name='dia_reg__name__idx'),
        )

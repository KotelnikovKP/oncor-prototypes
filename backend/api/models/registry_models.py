from django.db import models
from django.db.models import Index


class DiagnosisRegistry(models.Model):
    name = models.CharField(max_length=150, verbose_name='Diagnosis registry name')
    short_name = models.CharField(max_length=25, verbose_name='Diagnosis registry short name')
    medical_record_transcript_settings = models.JSONField(verbose_name='Settings of medical record transcript')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Diagnosis registry'
        verbose_name_plural = 'Diagnosis registers'
        ordering = ['name']
        indexes = (
            Index(fields=['name'], name='dia_reg__name__idx'),
        )


class DiagnosisRegistryItem(models.Model):
    registry = models.ForeignKey('DiagnosisRegistry', on_delete=models.CASCADE, related_name='diagnoses',
                                 verbose_name='registry')
    diagnosis = models.ForeignKey('Diagnosis', on_delete=models.CASCADE, related_name='registers',
                                  verbose_name='diagnosis')

    def __str__(self):
        return self.pk

    class Meta:
        verbose_name = 'Diagnosis registry item'
        verbose_name_plural = 'Diagnosis registry items'
        ordering = ['pk']



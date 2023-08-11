from django.db import models
from django.db.models import Index

from api.models.patient_models import Patient


class SEMD(models.Model):
    # SEMD
    internal_message_id = models.CharField(max_length=36, primary_key=True,
                                           verbose_name='Structured Electronic Medical Document identifier')
    document_type = models.CharField(max_length=8, verbose_name='Structured Electronic Medical Document type')
    sms_profile = models.CharField(max_length=10, verbose_name='Structured Electronic Medical Document profile')
    date_time_create = models.DateTimeField(verbose_name='Date time create')
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='semd',
                                null=True, blank=True, verbose_name='Patient')
    medical_organization = models.ForeignKey('MedicalOrganization', on_delete=models.PROTECT, related_name='semd',
                                             null=True, blank=True, verbose_name='Medical organization')
    doctor = models.CharField(max_length=255, null=True, blank=True, verbose_name='Doctor name')
    medical_position = models.ForeignKey('MedicalPosition', on_delete=models.PROTECT, related_name='semd',
                                         null=True, blank=True, verbose_name='Medical position')
    diagnoses = models.CharField(max_length=150, null=True, blank=True, verbose_name='Diagnosis codes')
    medical_service = models.ForeignKey('MedicalService', on_delete=models.PROTECT, related_name='semd',
                                        null=True, blank=True, verbose_name='Medical service')
    service_time = models.DateTimeField(null=True, blank=True, verbose_name='Medical service date time')

    # SEMD 2
    place_of_service = models.CharField(max_length=25, null=True, blank=True, verbose_name='Place of service')

    # SEMD 2, 5
    res_protocol = models.CharField(null=True, blank=True, verbose_name='Result protocol')
    res_conclusion = models.CharField(null=True, blank=True, verbose_name='Result conclusion')
    res_recommendation = models.CharField(null=True, blank=True, verbose_name='Result recommendation')

    # SEMD 5
    patient_condition = models.CharField(null=True, blank=True, verbose_name='Doctor visit patient condition')
    patient_diagnosis = models.ForeignKey('Diagnosis', on_delete=models.PROTECT, related_name='semd',
                                          null=True, blank=True, verbose_name='Doctor visit diagnosis')

    # SEMD 3 (tests result in SemdTest)

    # SEMD 8
    patient_in_condition = models.CharField(null=True, blank=True, verbose_name='Hospital patient in condition')
    patient_out_condition = models.CharField(null=True, blank=True, verbose_name='Hospital patient out condition')
    start_date = models.DateField(null=True, blank=True, verbose_name='Hospital start date')
    end_date = models.DateField(null=True, blank=True, verbose_name='Hospital end date')
    hospitalization_urgency = models.CharField(null=True, blank=True, verbose_name='Hospital urgency')
    hospitalization_results = models.CharField(null=True, blank=True, verbose_name='Hospital results')

    def __str__(self):
        return self.internal_message_id

    class Meta:
        verbose_name = 'SEMD'
        verbose_name_plural = 'SEMD'
        ordering = ['date_time_create']
        indexes = (
            Index(fields=['date_time_create'], name='semd__date_time_create__idx'),
            Index(fields=['patient_id', 'service_time'], name='semd__pat_time__idx'),
            Index(fields=['patient_id', 'medical_service_id', 'service_time'], name='semd__pat_srv_tim__idx'),
        )


class SemdTest(models.Model):
    semd = models.ForeignKey('SEMD', on_delete=models.CASCADE, related_name='tests',
                             verbose_name='SEMD')
    laboratory_test = models.ForeignKey('LaboratoryTest', on_delete=models.PROTECT, related_name='tests',
                                        verbose_name='Laboratory test')
    value = models.CharField(null=True, blank=True, verbose_name='Tests value')
    patient = models.ForeignKey('Patient', on_delete=models.PROTECT, related_name='tests',
                                null=True, blank=True, verbose_name='Patient')
    test_time = models.DateTimeField(null=True, blank=True, verbose_name='Test date time')

    def __str__(self):
        return self.pk

    class Meta:
        verbose_name = 'SEMD Test'
        verbose_name_plural = 'SEMD Tests'
        ordering = ['id']
        indexes = (
            Index(fields=['test_time'], name='semd_test__time__idx'),
            Index(fields=['patient_id', 'test_time'], name='semd_test__pat_tim__idx'),
            Index(fields=['patient_id', 'laboratory_test_id', 'test_time'], name='semd_test__pat_lt_tim__idx'),
        )

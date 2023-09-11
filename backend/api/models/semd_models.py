from django.db import models
from django.db.models import Index


class SemdDiagnosis(models.Model):
    # Patient-SEMD-diagnosis cube
    ptn_id = models.CharField(max_length=16, verbose_name='Patient @rid', db_index=True)
    ptn_code = models.CharField(max_length=16, null=True, verbose_name='Patient extra abbreviation')
    ptn_mo_oid = models.CharField(max_length=64, null=True, verbose_name='Patient MO OID')
    ptn_tags = models.JSONField(null=True, verbose_name='Patient tags')
    rc_id = models.CharField(max_length=16, verbose_name='SEMD record @rid', db_index=True)
    time_rc = models.DateTimeField(null=True, verbose_name='SEMD time')
    document_type = models.CharField(max_length=8, null=True, verbose_name='SEMD type')
    nsi_doc_type = models.CharField(max_length=8, null=True, verbose_name='SEMD nsi type')
    profile = models.CharField(max_length=8, null=True, verbose_name='SEMD profile')
    author_mo_oid = models.CharField(max_length=64, null=True, verbose_name='SEMD author MO OID')
    author_snils = models.CharField(max_length=14, null=True, verbose_name='SEMD author SNILS')
    author_post = models.CharField(max_length=64, null=True, verbose_name='SEMD author post OID')
    internal_message_id = models.CharField(max_length=64, null=True, verbose_name='SEMD internal_message_id')
    external_message_id = models.CharField(max_length=64, null=True, verbose_name='SEMD external_message_id')
    diagnosis_mkb10 = models.CharField(max_length=10, verbose_name='Diagnosis mkb10 code', db_index=True)
    diagnosis_date = models.DateField(null=True, verbose_name='Diagnosis set date')
    diagnosis_code1379 = models.CharField(max_length=10, null=True, verbose_name='Diagnosis SEMD section')
    diagnosis_code1076 = models.CharField(max_length=10, null=True, verbose_name='Diagnosis accuracy type')
    diagnosis_code1077 = models.CharField(max_length=10, null=True, verbose_name='Diagnosis type')

    def __str__(self):
        return str(self.ptn_id) + '-' + str(self.rc_id) + '-' + \
            str(self.diagnosis_mkb10) + '-' + str(self.diagnosis_date)

    class Meta:
        verbose_name = 'Patient-SEMD-diagnosis'
        verbose_name_plural = 'Patient-SEMD-diagnosis cube'
        ordering = ['id']
        indexes = (
            Index(fields=['ptn_id', 'diagnosis_mkb10', 'diagnosis_date'], name='api_semddiagnosis_ptn_dz_dat'),
        )


class SemdService(models.Model):
    # Patient-SEMD-service cube
    ptn_id = models.CharField(max_length=16, verbose_name='Patient @rid', db_index=True)
    ptn_code = models.CharField(max_length=16, null=True, verbose_name='Patient extra abbreviation')
    ptn_mo_oid = models.CharField(max_length=64, null=True, verbose_name='Patient MO OID')
    ptn_tags = models.JSONField(null=True, verbose_name='Patient tags')
    rc_id = models.CharField(max_length=16, verbose_name='SEMD record @rid', db_index=True)
    time_rc = models.DateTimeField(null=True, verbose_name='SEMD time')
    document_type = models.CharField(max_length=8, null=True, verbose_name='SEMD type')
    nsi_doc_type = models.CharField(max_length=8, null=True, verbose_name='SEMD nsi type')
    profile = models.CharField(max_length=8, null=True, verbose_name='SEMD profile')
    author_mo_oid = models.CharField(max_length=64, null=True, verbose_name='SEMD author MO OID')
    author_snils = models.CharField(max_length=14, null=True, verbose_name='SEMD author SNILS')
    author_post = models.CharField(max_length=64, null=True, verbose_name='SEMD author post OID')
    internal_message_id = models.CharField(max_length=64, null=True, verbose_name='SEMD internal_message_id')
    external_message_id = models.CharField(max_length=64, null=True, verbose_name='SEMD external_message_id')
    service_code = models.CharField(max_length=20, verbose_name='Service code', db_index=True)
    service_date = models.DateField(null=True, verbose_name='Service date')
    instrumental_diagnostics_code = models.CharField(max_length=10, null=True,
                                                     verbose_name='Instrumental diagnostics code')

    def __str__(self):
        return str(self.ptn_id) + '-' + str(self.rc_id) + '-' + \
            str(self.service_code) + '-' + str(self.service_date)

    class Meta:
        verbose_name = 'Patient-SEMD-service'
        verbose_name_plural = 'Patient-SEMD-service cube'
        ordering = ['id']
        indexes = (
            Index(fields=['ptn_id', 'service_code', 'service_date'], name='api_semdservice_ptn_srv_dat'),
        )


class OncorSettings(models.Model):
    # Patient-SEMD-service cube
    code = models.CharField(max_length=40, primary_key=True, verbose_name='Setting code')
    value = models.JSONField(null=True, verbose_name='Setting value')

    def __str__(self):
        return str(self.code)

    class Meta:
        verbose_name = 'Oncor settings'
        verbose_name_plural = 'Oncor settings'
        ordering = ['code']


# class SEMD(models.Model):
#     # SEMD
#     internal_message_id = models.CharField(max_length=36, primary_key=True,
#                                            verbose_name='Structured Electronic Medical Document identifier')
#     document_type = models.CharField(max_length=8, verbose_name='Structured Electronic Medical Document type')
#     sms_profile = models.CharField(max_length=10, verbose_name='Structured Electronic Medical Document profile')
#     date_time_create = models.DateTimeField(verbose_name='Date time create')
#     patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='semd',
#                                 null=True, blank=True, verbose_name='Patient')
#     medical_organization = models.ForeignKey('MedicalOrganization', on_delete=models.PROTECT, related_name='semd',
#                                              null=True, blank=True, verbose_name='Medical organization')
#     doctor = models.CharField(max_length=255, null=True, blank=True, verbose_name='Doctor name')
#     medical_position = models.ForeignKey('MedicalPosition', on_delete=models.PROTECT, related_name='semd',
#                                          null=True, blank=True, verbose_name='Medical position')
#     diagnoses = models.CharField(max_length=150, null=True, blank=True, verbose_name='Diagnosis codes')
#     medical_service = models.ForeignKey('MedicalService', on_delete=models.PROTECT, related_name='semd',
#                                         null=True, blank=True, verbose_name='Medical service')
#     service_time = models.DateTimeField(null=True, blank=True, verbose_name='Medical service date time')
#
#     # SEMD 2
#     place_of_service = models.CharField(max_length=25, null=True, blank=True, verbose_name='Place of service')
#
#     # SEMD 2, 5
#     res_protocol = models.CharField(null=True, blank=True, verbose_name='Result protocol')
#     res_conclusion = models.CharField(null=True, blank=True, verbose_name='Result conclusion')
#     res_recommendation = models.CharField(null=True, blank=True, verbose_name='Result recommendation')
#
#     # SEMD 5
#     patient_condition = models.CharField(null=True, blank=True, verbose_name='Doctor visit patient condition')
#     patient_diagnosis = models.ForeignKey('Diagnosis', on_delete=models.PROTECT, related_name='semd',
#                                           null=True, blank=True, verbose_name='Doctor visit diagnosis')
#
#     # SEMD 3 (tests result in SemdTest)
#
#     # SEMD 8
#     patient_in_condition = models.CharField(null=True, blank=True, verbose_name='Hospital patient in condition')
#     patient_out_condition = models.CharField(null=True, blank=True, verbose_name='Hospital patient out condition')
#     start_date = models.DateField(null=True, blank=True, verbose_name='Hospital start date')
#     end_date = models.DateField(null=True, blank=True, verbose_name='Hospital end date')
#     hospitalization_urgency = models.CharField(null=True, blank=True, verbose_name='Hospital urgency')
#     hospitalization_results = models.CharField(null=True, blank=True, verbose_name='Hospital results')
#
#     def __str__(self):
#         return self.internal_message_id
#
#     class Meta:
#         verbose_name = 'SEMD'
#         verbose_name_plural = 'SEMD'
#         ordering = ['date_time_create']
#         indexes = (
#             Index(fields=['date_time_create'], name='semd__date_time_create__idx'),
#             Index(fields=['patient_id', 'service_time'], name='semd__pat_time__idx'),
#             Index(fields=['patient_id', 'medical_service_id', 'service_time'], name='semd__pat_srv_tim__idx'),
#         )
#
#
# class SemdTest(models.Model):
#     semd = models.ForeignKey('SEMD', on_delete=models.CASCADE, related_name='tests',
#                              verbose_name='SEMD')
#     laboratory_test = models.ForeignKey('LaboratoryTest', on_delete=models.PROTECT, related_name='tests',
#                                         verbose_name='Laboratory test')
#     value = models.CharField(null=True, blank=True, verbose_name='Tests value')
#     patient = models.ForeignKey('Patient', on_delete=models.PROTECT, related_name='tests',
#                                 null=True, blank=True, verbose_name='Patient')
#     test_time = models.DateTimeField(null=True, blank=True, verbose_name='Test date time')
#
#     def __str__(self):
#         return self.pk
#
#     class Meta:
#         verbose_name = 'SEMD Test'
#         verbose_name_plural = 'SEMD Tests'
#         ordering = ['id']
#         indexes = (
#             Index(fields=['test_time'], name='semd_test__time__idx'),
#             Index(fields=['patient_id', 'test_time'], name='semd_test__pat_tim__idx'),
#             Index(fields=['patient_id', 'laboratory_test_id', 'test_time'], name='semd_test__pat_lt_tim__idx'),
#         )

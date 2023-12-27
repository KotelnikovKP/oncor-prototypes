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
            Index(fields=['ptn_id', 'diagnosis_mkb10', 'time_rc'], name='api_semddiagnosis_ptn_dz_rcdat'),
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
            Index(fields=['ptn_id', 'service_code', 'time_rc'], name='api_semdservice_ptn_srv_rcdat'),
        )


class OncorSettings(models.Model):
    code = models.CharField(max_length=40, primary_key=True, verbose_name='Setting code')
    value = models.JSONField(null=True, verbose_name='Setting value')

    def __str__(self):
        return str(self.code)

    class Meta:
        verbose_name = 'Oncor settings'
        verbose_name_plural = 'Oncor settings'
        ordering = ['code']


class PatientDiagnosisMilestones(models.Model):
    # Patient-Diagnosis cube
    ptn_id = models.CharField(max_length=16, verbose_name='Patient @rid', db_index=True)
    ptn_code = models.CharField(max_length=16, null=True, verbose_name='Patient extra abbreviation')
    ptn_mo_oid = models.CharField(max_length=64, null=True, verbose_name='Patient MO OID')
    ptn_tags = models.JSONField(null=True, verbose_name='Patient tags')
    diagnosis_mkb10 = models.CharField(max_length=10, verbose_name='Diagnosis mkb10 code', db_index=True)
    diagnosis_date = models.DateField(null=True, verbose_name='Diagnosis set date', db_index=True)
    diagnosis_milestones = models.JSONField(null=True, verbose_name='Diagnosis milestones')

    def __str__(self):
        return str(self.ptn_id) + '-' + str(self.diagnosis_mkb10) + '-' + str(self.diagnosis_date)

    class Meta:
        verbose_name = 'Patient-Diagnosis'
        verbose_name_plural = 'Patient-Diagnosis cube'
        ordering = ['id']
        indexes = (
            Index(fields=['ptn_id', 'diagnosis_date'], name='api_p_d_milestones_ptn_dat'),
            Index(fields=['ptn_id', 'diagnosis_mkb10', 'diagnosis_date'], name='api_p_d_milestones_ptn_dz_dat'),
        )


class PatientRecord(models.Model):
    # Patient Cancer Register Records
    ptn_id = models.CharField(max_length=16, verbose_name='Patient @rid', db_index=True)
    rc_id = models.CharField(max_length=16, verbose_name='Record @rid', db_index=True)
    rc_type = models.CharField(max_length=32, verbose_name='Record type', db_index=True)
    rc_time = models.DateTimeField(null=True, verbose_name='Record time', db_index=True)
    rc_time_in = models.DateTimeField(null=True, verbose_name='Record time in')
    rc_time_out = models.DateTimeField(null=True, verbose_name='Record time out')
    rc_summary = models.JSONField(null=True, verbose_name='Record summary')

    def __str__(self):
        return str(self.ptn_id) + '-' + str(self.rc_id) + '-' + \
            str(self.rc_type) + '-' + str(self.rc_time)

    class Meta:
        verbose_name = 'Patient Cancer Register Record'
        verbose_name_plural = 'Patient Cancer Register Records'
        ordering = ['id']
        indexes = (
            Index(fields=['ptn_id', 'rc_type', 'rc_time'], name='api_patientrecord_ptn_typ_tim'),
            Index(fields=['ptn_id', 'rc_time'], name='api_patientrecord_ptn_tim'),
        )


class PatientDiagnosis(models.Model):
    # Patient Cancer Register diagnosis
    ptn_id = models.CharField(max_length=16, verbose_name='Patient @rid', db_index=True)
    rc_id = models.CharField(max_length=16, verbose_name='Record @rid', db_index=True)
    diagnosis_date = models.DateField(null=True, verbose_name='Diagnosis set date', db_index=True)
    diagnosis_mkb10 = models.CharField(max_length=10, verbose_name='Diagnosis mkb10 code', db_index=True)
    status = models.CharField(max_length=64, null=True, verbose_name='Diagnosis status')
    primacy = models.CharField(max_length=64, null=True, verbose_name='Diagnosis primacy')
    morph_class_disabled = models.CharField(max_length=64, null=True, verbose_name='Diagnosis morph_class_disabled')
    morph_class_child_count = models.CharField(max_length=64, null=True,
                                               verbose_name='Diagnosis morph_class_child_count')
    morph_class_sname = models.CharField(max_length=64, null=True, verbose_name='Diagnosis morph_class_s_name')
    tumor_main = models.CharField(max_length=64, null=True, verbose_name='Diagnosis tumor_main')
    tumor_side = models.CharField(max_length=64, null=True, verbose_name='Diagnosis tumor_side')
    how_discover = models.CharField(max_length=64, null=True, verbose_name='Diagnosis how_discover')
    method = models.CharField(max_length=64, null=True, verbose_name='Diagnosis method')
    plural = models.CharField(max_length=64, null=True, verbose_name='Diagnosis plural')
    res_autopsy = models.CharField(max_length=64, null=True, verbose_name='Diagnosis res_autopsy')
    why_old = models.CharField(max_length=64, null=True, verbose_name='Diagnosis why_old')
    loc_met = models.CharField(max_length=64, null=True, verbose_name='Diagnosis loc_met')
    tnm_t = models.CharField(max_length=64, null=True, verbose_name='Diagnosis tnm_t')
    tnm_n = models.CharField(max_length=64, null=True, verbose_name='Diagnosis tnm_n')
    tnm_m = models.CharField(max_length=64, null=True, verbose_name='Diagnosis tnm_m')
    tnm_g = models.CharField(max_length=64, null=True, verbose_name='Diagnosis tnm_g')
    stage = models.CharField(max_length=64, null=True, verbose_name='Diagnosis stage')

    def __str__(self):
        return str(self.ptn_id) + '-' + str(self.rc_id) + '-' + \
            str(self.diagnosis_mkb10) + '-' + str(self.diagnosis_date)

    class Meta:
        verbose_name = 'Patient Cancer Register diagnosis'
        verbose_name_plural = 'Patient Cancer Register diagnoses'
        ordering = ['id']
        indexes = (
            Index(fields=['ptn_id', 'diagnosis_mkb10', 'diagnosis_date'], name='api_patientdiagnosis_ptn_dz_dt'),
            Index(fields=['ptn_id', 'diagnosis_date'], name='api_patientdiagnosis_ptn_dat'),
        )


class PatientSEMD(models.Model):
    # Patient SEMDs
    ptn_id = models.CharField(max_length=16, verbose_name='Patient @rid', db_index=True)
    ptn_code = models.CharField(max_length=16, verbose_name='Patient code')
    rc_sms_id = models.CharField(max_length=16, null=True, verbose_name='SMS Record @rid')
    rc_cda_id = models.CharField(max_length=16, null=True, verbose_name='CDA Record @rid')
    is_external_semd = models.BooleanField(verbose_name='External SEMD flag')
    is_external_semd_sendable = models.BooleanField(null=True, verbose_name='External SEMD flag')
    send_task_step = models.CharField(max_length=64, null=True, verbose_name='Send task step')
    send_task_status = models.CharField(max_length=64, null=True, verbose_name='Send task status')
    sms_status = models.JSONField(null=True, verbose_name='SMS status')
    cda_status = models.JSONField(null=True, verbose_name='CDA status')
    rc_time = models.DateTimeField(verbose_name='SEMD time', db_index=True)
    cda_local_date = models.DateField(verbose_name='SEMD date', db_index=True)
    attachment = models.CharField(max_length=64, null=True, verbose_name='Attachment id')
    profile = models.CharField(max_length=8, verbose_name='SEMD profile')
    soap_doc_type = models.CharField(max_length=8, null=True, verbose_name='SEMD type')
    author_mo_oid = models.CharField(max_length=64, null=True, verbose_name='Author MO oid')
    author_mo_dpt_oid = models.CharField(max_length=64, null=True, verbose_name='Author MO department oid')
    author_snils = models.CharField(max_length=14, null=True, verbose_name='Author SNILS')
    author_post = models.CharField(max_length=8, null=True, verbose_name='Author post id')
    diagnosis_mkb10 = models.CharField(max_length=10, null=True, verbose_name='Diagnosis mkb10 code')
    diagnosis_date = models.DateField(null=True, verbose_name='Diagnosis date')
    diagnosis_code197 = models.CharField(max_length=32, null=True, verbose_name='Diagnosis code197')
    diagnosis_code1076 = models.CharField(max_length=8, null=True, verbose_name='Diagnosis code1076')
    diagnosis_code1077 = models.CharField(max_length=8, null=True, verbose_name='Diagnosis code1077')
    is_cancer_diagnosis = models.BooleanField(verbose_name='Cancer diagnosis flag')
    is_precancer_diagnosis = models.BooleanField(verbose_name='Precancer diagnosis flag')
    diagnoses = models.JSONField(null=True, verbose_name='SEMD diagnoses')
    is_cancer_diagnoses = models.BooleanField(verbose_name='Cancer diagnoses flag')
    is_precancer_diagnoses = models.BooleanField(verbose_name='Precancer diagnoses flag')
    services = models.JSONField(null=True, verbose_name='SEMD services')
    cda_time = models.DateTimeField(null=True, verbose_name='CDA time')
    sms_type = models.CharField(max_length=32, null=True, verbose_name='SMS type')
    is_in_cancer_register = models.BooleanField(verbose_name='Patient is in Cancer register flag')
    has_cancer_diagnosis = models.BooleanField(verbose_name='Patient has cancer diagnosis flag')
    has_precancer_diagnosis = models.BooleanField(verbose_name='Patient has precancer diagnosis flag')
    rc_diagnosis_mkb10 = models.CharField(max_length=10, null=True, verbose_name='Cancer Register diagnosis mkb10 code')
    rc_diagnosis_date = models.DateField(null=True, verbose_name='Cancer Register diagnosis date')
    semd_content = models.JSONField(null=True, verbose_name='SEMD content')
    content_error = models.CharField(max_length=300, verbose_name='Content error', db_index=True)
    diagnosis_error = models.CharField(max_length=150, verbose_name='Diagnosis error', db_index=True)

    def __str__(self):
        return str(self.ptn_id) + '-' + str(self.rc_sms_id) + '-' + str(self.rc_cda_id) + '-' + str(self.profile)

    class Meta:
        verbose_name = 'Patient SEMD'
        verbose_name_plural = 'Patient SEMDs'
        ordering = ['id']
        indexes = (
            Index(fields=['ptn_id', 'soap_doc_type', 'cda_local_date'], name='api_patientsemd_ptn_typ_dat'),
            Index(fields=['ptn_id', 'cda_local_date'], name='api_patientsemd_ptn_dat'),
        )

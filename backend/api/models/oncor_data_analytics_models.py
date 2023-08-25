from django.db import models


class DataPopulation(models.Model):
    terr_id = models.CharField(max_length=16)
    year = models.IntegerField()
    gender = models.CharField(max_length=2)
    age = models.IntegerField()
    population = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'data_population'


class DataTerritoryName(models.Model):
    terr_id = models.CharField(primary_key=True, max_length=16)
    unq = models.CharField(max_length=50)
    name = models.CharField(max_length=150)
    status = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'data_territory_name'


class Departments(models.Model):
    id = models.BigAutoField(primary_key=True)
    department_ptn_id = models.CharField(max_length=16)
    department_id = models.CharField(max_length=16)
    department_name = models.CharField(max_length=128)

    class Meta:
        managed = False
        db_table = 'departments'


class EhrRegisterRvpp(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16)
    ehr_id = models.CharField(max_length=16)
    disability = models.JSONField(blank=True, null=True)
    palliat_medication = models.JSONField()
    palliat_med_items = models.JSONField()
    palliat_inclusion_date = models.DateField(blank=True, null=True)
    diagnosis = models.JSONField(blank=True, null=True)
    palliat_med_org_id = models.CharField(max_length=16, blank=True, null=True)
    palliat_org_unit_id_set = models.JSONField()
    rc_identity_document_passport_id = models.CharField(max_length=16, blank=True, null=True)
    palliat_med_proc = models.JSONField()
    ref_to_social_security = models.JSONField()
    palliat_hosp = models.JSONField()
    palliat_refuse_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ehr_register_rvpp'


class EhrScreening(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16)
    ehr_id = models.CharField(max_length=16)
    name = models.CharField(max_length=16)
    type = models.CharField(max_length=16)
    begin_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    onco_health_group = models.CharField(max_length=4, blank=True, null=True)
    diagnosis_days = models.IntegerField(blank=True, null=True)
    diagnosis_stage = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ehr_screening'


class Inspections(models.Model):
    id = models.BigAutoField(primary_key=True)
    level = models.CharField(max_length=16)
    inspection_date_time = models.DateTimeField()
    date_time = models.DateTimeField(blank=True, null=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=20, blank=True, null=True)
    ehr_id = models.CharField(max_length=16, blank=True, null=True)
    rc_id = models.CharField(max_length=16, blank=True, null=True)
    rc_class = models.CharField(max_length=32, blank=True, null=True)
    is_rc_published = models.BooleanField(blank=True, null=True)
    type = models.CharField(max_length=64)
    field = models.CharField(max_length=64, blank=True, null=True)
    field_value = models.CharField(max_length=64, blank=True, null=True)
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    json = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'inspections'


class InstanceStatus(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16, blank=True, null=True)
    rc_id = models.CharField(max_length=16)
    rc_class = models.CharField(max_length=64)
    json = models.JSONField(blank=True, null=True)
    user_id = models.CharField(max_length=16)
    user_login = models.CharField(max_length=32)
    status_time = models.DateTimeField()
    status_date = models.DateField()
    history = models.JSONField()

    class Meta:
        managed = False
        db_table = 'instance_status'


class Medstat(models.Model):
    a1 = models.CharField(max_length=2)  # The composite primary key (a1, a2, a4, a5, a6) found, that is not supported. The first column is selected.
    a2 = models.CharField(max_length=4)
    a4 = models.CharField(max_length=7)
    a5 = models.CharField(max_length=6)
    a6 = models.CharField(max_length=3)
    a81 = models.DecimalField(max_digits=12, decimal_places=2)
    a82 = models.DecimalField(max_digits=12, decimal_places=2)
    a83 = models.DecimalField(max_digits=12, decimal_places=2)
    a84 = models.DecimalField(max_digits=12, decimal_places=2)
    a85 = models.DecimalField(max_digits=12, decimal_places=2)
    a86 = models.DecimalField(max_digits=12, decimal_places=2)
    a87 = models.DecimalField(max_digits=12, decimal_places=2)
    a88 = models.DecimalField(max_digits=12, decimal_places=2)
    a89 = models.DecimalField(max_digits=12, decimal_places=2)
    a810 = models.DecimalField(max_digits=12, decimal_places=2)
    a811 = models.DecimalField(max_digits=12, decimal_places=2)
    a812 = models.DecimalField(max_digits=12, decimal_places=2)
    a813 = models.DecimalField(max_digits=12, decimal_places=2)
    a814 = models.DecimalField(max_digits=12, decimal_places=2)
    a815 = models.DecimalField(max_digits=12, decimal_places=2)
    a816 = models.DecimalField(max_digits=12, decimal_places=2)
    a817 = models.DecimalField(max_digits=12, decimal_places=2)
    a818 = models.DecimalField(max_digits=12, decimal_places=2)
    a819 = models.DecimalField(max_digits=12, decimal_places=2)
    a820 = models.DecimalField(max_digits=12, decimal_places=2)
    a821 = models.DecimalField(max_digits=12, decimal_places=2)
    a822 = models.DecimalField(max_digits=12, decimal_places=2)
    a823 = models.DecimalField(max_digits=12, decimal_places=2)
    a824 = models.DecimalField(max_digits=12, decimal_places=2)
    a825 = models.DecimalField(max_digits=12, decimal_places=2)
    a826 = models.DecimalField(max_digits=12, decimal_places=2)
    a827 = models.DecimalField(max_digits=12, decimal_places=2)
    a828 = models.DecimalField(max_digits=12, decimal_places=2)
    a829 = models.DecimalField(max_digits=12, decimal_places=2)
    a830 = models.DecimalField(max_digits=12, decimal_places=2)
    a831 = models.DecimalField(max_digits=12, decimal_places=2)
    a832 = models.DecimalField(max_digits=12, decimal_places=2)
    a833 = models.DecimalField(max_digits=12, decimal_places=2)
    a834 = models.DecimalField(max_digits=12, decimal_places=2)
    a835 = models.DecimalField(max_digits=12, decimal_places=2)
    a836 = models.DecimalField(max_digits=12, decimal_places=2)
    a837 = models.DecimalField(max_digits=12, decimal_places=2)
    a838 = models.DecimalField(max_digits=12, decimal_places=2)
    a839 = models.DecimalField(max_digits=12, decimal_places=2)
    a840 = models.DecimalField(max_digits=12, decimal_places=2)
    a841 = models.DecimalField(max_digits=12, decimal_places=2)
    a842 = models.DecimalField(max_digits=12, decimal_places=2)
    a843 = models.DecimalField(max_digits=12, decimal_places=2)
    a844 = models.DecimalField(max_digits=12, decimal_places=2)
    a845 = models.DecimalField(max_digits=12, decimal_places=2)
    a846 = models.DecimalField(max_digits=12, decimal_places=2)
    a847 = models.DecimalField(max_digits=12, decimal_places=2)
    a848 = models.DecimalField(max_digits=12, decimal_places=2)
    a849 = models.DecimalField(max_digits=12, decimal_places=2)
    a850 = models.DecimalField(max_digits=12, decimal_places=2)
    srt = models.CharField(max_length=25)
    n1 = models.IntegerField()
    n2 = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'medstat'
        unique_together = (('a1', 'a2', 'a4', 'a5', 'a6'),)


class MedstatImportMetadata(models.Model):
    id = models.BigAutoField(primary_key=True)
    file_digest = models.CharField(max_length=100)
    info = models.TextField()

    class Meta:
        managed = False
        db_table = 'medstat_import_metadata'


class MvRcListByPtn(models.Model):
    ptn_id = models.CharField(primary_key=True, max_length=16)
    ptn_code = models.CharField(max_length=16)
    ptn_tags = models.JSONField(blank=True, null=True)
    rc_list = models.JSONField()
    max_time_published = models.DateTimeField(blank=True, null=True)
    max_time_published_common = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mv_rc_list_by_ptn'


class OncorInspections(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.CharField(max_length=32)
    inspection = models.CharField(max_length=32)
    level = models.CharField(max_length=8)
    internal_date_time = models.DateTimeField()
    date_time = models.DateTimeField(blank=True, null=True)
    range_start = models.DateTimeField(blank=True, null=True)
    range_end = models.DateTimeField(blank=True, null=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16, blank=True, null=True)
    ehr_id = models.CharField(max_length=16, blank=True, null=True)
    ehr_kind = models.CharField(max_length=20, blank=True, null=True)
    rc_id = models.CharField(max_length=16, blank=True, null=True)
    rc_class = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'oncor_inspections'


class PtnTag(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=20)
    tag_id = models.CharField(max_length=16)
    tag_time = models.DateTimeField(blank=True, null=True)
    tag_owner_id = models.CharField(max_length=16, blank=True, null=True)
    tag_owner_login = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ptn_tag'


class Rc(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16)
    ptn_tags = models.JSONField(blank=True, null=True)
    ehr_id = models.CharField(max_length=16)
    ehr_class = models.CharField(max_length=32)
    ehr_kind = models.CharField(max_length=64, blank=True, null=True)
    rc_id = models.CharField(max_length=16)
    rc_class = models.CharField(max_length=64)
    rc_title = models.CharField(max_length=128, blank=True, null=True)
    time_rc = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField()
    time_created = models.DateTimeField(blank=True, null=True)
    time_published = models.DateTimeField(blank=True, null=True)
    user_id = models.CharField(max_length=16)
    user_login = models.CharField(max_length=128)
    org_unit_id = models.CharField(max_length=16)
    med_org_oid = models.CharField(max_length=32, blank=True, null=True)
    user_med_terrs = models.JSONField()
    meta = models.JSONField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rc'


class RcDocs(models.Model):
    id = models.BigAutoField(primary_key=True)
    time_rc = models.DateTimeField(blank=True, null=True)
    time_created = models.DateTimeField(blank=True, null=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16)
    ehr_id = models.CharField(max_length=16, blank=True, null=True)
    rc_id = models.CharField(max_length=16)
    summary = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=128, blank=True, null=True)
    attachments_count = models.IntegerField()
    is_published = models.BooleanField()
    json = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rc_docs'


class RcInsuranceIncident(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16, blank=True, null=True)
    ehr_id = models.CharField(max_length=16)
    rc_id = models.CharField(max_length=16)
    rc_local_date_time = models.DateTimeField(blank=True, null=True)
    incident_type = models.CharField(max_length=64)
    days_to_react = models.BigIntegerField()
    smo_id = models.CharField(max_length=16)
    responsible_user_id = models.CharField(max_length=16, blank=True, null=True)
    contact_json = models.JSONField()
    request_json = models.JSONField()
    result = models.CharField(max_length=64, blank=True, null=True)
    rate = models.CharField(max_length=64, blank=True, null=True)
    protocol = models.TextField(blank=True, null=True)
    protocol_date = models.DateField(blank=True, null=True)
    is_on_permanent_control = models.BooleanField(blank=True, null=True)
    status = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rc_insurance_incident'


class RcLaunched(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16)
    ehr_id = models.CharField(max_length=16, blank=True, null=True)
    rc_id = models.CharField(max_length=16)
    first_come_lpu_date = models.DateField(blank=True, null=True)
    launch_date = models.DateField(blank=True, null=True)
    why_old = models.CharField(max_length=64, blank=True, null=True)
    dz_mkb = models.CharField(max_length=16, blank=True, null=True)
    dz_stage = models.CharField(max_length=16, blank=True, null=True)
    user_id = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rc_launched'


class RcMammography(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16)
    ehr_id = models.CharField(max_length=16)
    rc_id = models.CharField(max_length=16)
    rc_cs_id = models.CharField(max_length=16, blank=True, null=True)
    rc_cs_date = models.DateTimeField(blank=True, null=True)
    research_date = models.DateTimeField(blank=True, null=True)
    equivalent_dose = models.CharField(max_length=8, blank=True, null=True)
    nsi_birads_right_id = models.CharField(max_length=16, blank=True, null=True)
    nsi_birads_left_id = models.CharField(max_length=16, blank=True, null=True)
    nsi_birads_conclusion_id = models.CharField(max_length=16, blank=True, null=True)
    contacts = models.CharField(max_length=32, blank=True, null=True)
    rc_contact_event_id = models.CharField(max_length=16, blank=True, null=True)
    rc_contact_event_date = models.DateField(blank=True, null=True)
    rc_contact_event_result = models.CharField(max_length=32, blank=True, null=True)
    med_org_oid = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rc_mammography'


class RcOmsSlR56(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ehr_id = models.CharField(max_length=16)
    rc_id = models.CharField(max_length=16)
    date_in = models.DateTimeField(blank=True, null=True)
    date_out = models.DateTimeField(blank=True, null=True)
    icd10 = models.CharField(max_length=16, blank=True, null=True)
    usl_count = models.IntegerField()
    case_goal = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rc_oms_sl_r56'


class RcOrder(models.Model):
    id = models.CharField(primary_key=True, max_length=16)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16, blank=True, null=True)
    ehr_id = models.CharField(max_length=16)
    rc_date = models.DateField(blank=True, null=True)
    rc_time = models.DateTimeField(blank=True, null=True)
    purpose = models.CharField(max_length=32, blank=True, null=True)
    diagnostics_type = models.CharField(max_length=32, blank=True, null=True)
    dz_icd_10 = models.CharField(max_length=16, blank=True, null=True)
    dz_text = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    client_id = models.CharField(max_length=32, blank=True, null=True)
    client_code = models.CharField(max_length=32, blank=True, null=True)
    client_mo_id = models.CharField(max_length=32, blank=True, null=True)
    client_mo_code = models.CharField(max_length=32, blank=True, null=True)
    expert_mo_id = models.CharField(max_length=32, blank=True, null=True)
    expert_mo_code = models.CharField(max_length=32, blank=True, null=True)
    deleted = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'rc_order'


class RcOrderResponse(models.Model):
    id = models.CharField(primary_key=True, max_length=16)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16, blank=True, null=True)
    ehr_id = models.CharField(max_length=16)
    rc_class_name = models.CharField(max_length=64)
    rc_date = models.DateField(blank=True, null=True)
    rc_time = models.DateTimeField(blank=True, null=True)
    rc_order = models.ForeignKey(RcOrder, models.DO_NOTHING)
    response = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    pdf = models.CharField(max_length=16, blank=True, null=True)
    pdf_ds = models.CharField(max_length=16, blank=True, null=True)
    expert_id = models.CharField(max_length=32, blank=True, null=True)
    expert_code = models.CharField(max_length=32, blank=True, null=True)
    expert_d_id = models.CharField(max_length=32, blank=True, null=True)
    expert_d_code = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rc_order_response'


class RcPtnAccess(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16)
    rc_id = models.CharField(max_length=16)
    request_time = models.DateTimeField()
    response_time = models.DateTimeField(blank=True, null=True)
    for_mo_id = models.CharField(max_length=16)
    status = models.CharField(max_length=16)

    class Meta:
        managed = False
        db_table = 'rc_ptn_access'


class RcRefTmk(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16)
    diagnosis = models.CharField(max_length=10)
    ehr_id = models.CharField(max_length=16)
    rc_ref_tmk_id = models.CharField(max_length=16)
    rc_date_time = models.DateTimeField()
    rc_tmk_id = models.CharField(max_length=16, blank=True, null=True)
    rc_tmk_date_time = models.DateTimeField(blank=True, null=True)
    tmk_status = models.CharField(max_length=16, blank=True, null=True)
    rc_tmk_mo_reject = models.CharField(max_length=64, blank=True, null=True)
    purpose = models.CharField(max_length=64)
    author_mo = models.CharField(max_length=64, blank=True, null=True)
    author_fio = models.CharField(max_length=100, blank=True, null=True)
    rc_referral_mo_oid = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'rc_ref_tmk'


class RcSemd(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16)
    rc_sms_id = models.CharField(max_length=16, blank=True, null=True)
    rc_cda_id = models.CharField(max_length=16, blank=True, null=True)
    profile = models.CharField(max_length=8)
    nsi_doc_type = models.CharField(max_length=8)
    soap_doc_type = models.CharField(max_length=8)
    author_mo_oid = models.CharField(max_length=64, blank=True, null=True)
    author_mo_dpt_oid = models.CharField(max_length=64, blank=True, null=True)
    author_snils = models.CharField(max_length=14, blank=True, null=True)
    cda_local_date = models.DateField(blank=True, null=True)
    sms_event_date_start = models.DateField(blank=True, null=True)
    sms_event_date_end = models.DateField(blank=True, null=True)
    sms_summary = models.JSONField(blank=True, null=True)
    ds_codes = models.JSONField(blank=True, null=True)
    ds_groups = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rc_semd'


class RcSms(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16)
    ehr_id = models.CharField(max_length=16, blank=True, null=True)
    rc_id = models.CharField(max_length=16)
    time_rc = models.DateTimeField()
    document_type_id = models.CharField(max_length=16)
    title = models.CharField(max_length=128)
    sms_listener_class = models.CharField(max_length=32, blank=True, null=True)
    sms_json_class_version = models.CharField(max_length=16)
    based_records = models.JSONField()
    internal_message_id = models.CharField(max_length=64, blank=True, null=True)
    external_message_id = models.CharField(max_length=64, blank=True, null=True)
    soap_doc_type = models.CharField(max_length=8, blank=True, null=True)
    profile = models.CharField(max_length=8, blank=True, null=True)
    cda_local_date = models.DateField(blank=True, null=True)
    cda_sent_local_date = models.DateField(blank=True, null=True)
    sms_summary = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rc_sms'


class Referrals(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16)
    ehr_id = models.CharField(max_length=16)
    rc_referral_id = models.CharField(max_length=16)
    referral_type = models.CharField(max_length=16, blank=True, null=True)
    rc_appointment_id = models.CharField(max_length=16, blank=True, null=True)
    rc_appointment_status = models.CharField(max_length=16, blank=True, null=True)
    mkb = models.CharField(max_length=8)
    tnm = models.CharField(max_length=20)
    stage = models.CharField(max_length=8, blank=True, null=True)
    stage_base = models.CharField(max_length=8, blank=True, null=True)
    clinical_group = models.CharField(max_length=8, blank=True, null=True)
    clinical_group_base = models.CharField(max_length=8, blank=True, null=True)
    max_date = models.DateTimeField()
    date = models.DateTimeField()
    number = models.CharField(max_length=32, blank=True, null=True)
    from_mo_id = models.CharField(max_length=16)
    to_mo_id = models.CharField(max_length=16)
    confirmed = models.BooleanField(blank=True, null=True)
    confirmed_date = models.DateTimeField(blank=True, null=True)
    appointment_date = models.DateTimeField(blank=True, null=True)
    appointment_doctor = models.CharField(max_length=32, blank=True, null=True)
    appointment_room = models.CharField(max_length=32, blank=True, null=True)
    appointment_department = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'referrals'


class Routing(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16)
    ehr_id = models.CharField(max_length=16)
    referral_id = models.CharField(max_length=16)
    referral_type = models.CharField(max_length=16, blank=True, null=True)
    dz_mkb = models.CharField(max_length=10, blank=True, null=True)
    dz_stage = models.CharField(max_length=16, blank=True, null=True)
    last_visit_other_sick_date = models.DateTimeField(blank=True, null=True)
    last_visit_consultant_lpu = models.DateTimeField(blank=True, null=True)
    first_come_lpu_date = models.DateTimeField(blank=True, null=True)
    ood_consult_date_plan = models.DateTimeField(blank=True, null=True)
    ood_consult_date_fact = models.DateTimeField(blank=True, null=True)
    ood_end_diag_date = models.DateTimeField(blank=True, null=True)
    ood_start_therapy_date = models.DateTimeField(blank=True, null=True)
    mo_diagnostics = models.JSONField(blank=True, null=True)
    launched_date = models.DateTimeField(blank=True, null=True)
    first_sign_date = models.DateTimeField(blank=True, null=True)
    first_lpu = models.CharField(max_length=16, blank=True, null=True)
    first_dz_date = models.DateTimeField(blank=True, null=True)
    first_dz_lpu = models.CharField(max_length=16, blank=True, null=True)
    history = models.TextField(blank=True, null=True)
    review_data = models.TextField(blank=True, null=True)
    conference_org_unit = models.CharField(max_length=16, blank=True, null=True)
    conference_date = models.DateTimeField(blank=True, null=True)
    conclusion = models.TextField(blank=True, null=True)
    diagnosis_why_old = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'routing'


class StatEhr(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16)
    ehr_id = models.CharField(max_length=16)
    ehr_index = models.IntegerField(blank=True, null=True)
    dz_date = models.DateField(blank=True, null=True)
    last_dz_date = models.DateField(blank=True, null=True)
    dz_age = models.IntegerField(blank=True, null=True)
    dz_status = models.CharField(max_length=16, blank=True, null=True)
    dz_mkb = models.CharField(max_length=16, blank=True, null=True)
    dz_group_id = models.CharField(max_length=64, blank=True, null=True)
    is_neglected_case = models.BooleanField(blank=True, null=True)
    dz_stage = models.CharField(max_length=16, blank=True, null=True)
    dz_primary = models.CharField(max_length=16, blank=True, null=True)
    dz_morph = models.CharField(max_length=16, blank=True, null=True)
    dz_tnm_t = models.CharField(max_length=16, blank=True, null=True)
    dz_tnm_n = models.CharField(max_length=16, blank=True, null=True)
    dz_tnm_m = models.CharField(max_length=16, blank=True, null=True)
    dz_tnm_g = models.CharField(max_length=16, blank=True, null=True)
    is_main_death_reason = models.BooleanField()
    is_min_dz_date = models.BooleanField()
    tumor_main = models.CharField(max_length=16)
    dz_side = models.CharField(max_length=16, blank=True, null=True)
    dz_multiple = models.CharField(max_length=32, blank=True, null=True)
    dz_how_discovered = models.CharField(max_length=32, blank=True, null=True)
    dz_verify_method = models.CharField(max_length=32, blank=True, null=True)
    dz_late_reason = models.CharField(max_length=64, blank=True, null=True)
    dz_autopsy = models.CharField(max_length=16, blank=True, null=True)
    dz_loc_metastasis = models.JSONField(blank=True, null=True)
    onco_dispensary_group = models.CharField(max_length=16, blank=True, null=True)
    onco_dispensary_date_recommended = models.DateField(blank=True, null=True)
    onco_dispensary_date_recommended_next = models.DateField(blank=True, null=True)
    onco_dispensary_last_dispensary_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stat_ehr'


class StatEhrRegister(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=16)
    ehr_id = models.CharField(max_length=16)
    include_clause = models.CharField(max_length=8)
    exclude_reason = models.CharField(max_length=12, blank=True, null=True)
    in_date = models.DateField()
    type = models.CharField(max_length=32)
    out_date = models.DateField(blank=True, null=True)
    dz_date = models.DateField(blank=True, null=True)
    dz_mkb = models.CharField(max_length=16, blank=True, null=True)
    dz_group_id = models.CharField(max_length=64, blank=True, null=True)
    dz_comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stat_ehr_register'


class StatPatients(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_code = models.CharField(max_length=20)
    ptn_id = models.CharField(max_length=16)
    ehr_id = models.CharField(max_length=16, blank=True, null=True)
    ehr_kind = models.CharField(max_length=20, blank=True, null=True)
    ehr_index = models.BigIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=16)
    birth = models.DateField()
    living_area = models.CharField(max_length=8, blank=True, null=True)
    terr_id = models.CharField(max_length=16, blank=True, null=True)
    org_observer_id = models.CharField(max_length=16, blank=True, null=True)
    smo = models.CharField(max_length=16, blank=True, null=True)
    ptn_disable = models.CharField(max_length=30, blank=True, null=True)
    reg_in_date = models.DateField(blank=True, null=True)
    reg_in_clause = models.CharField(max_length=50, blank=True, null=True)
    reg_out_date = models.DateField(blank=True, null=True)
    reg_out_reason = models.CharField(max_length=50, blank=True, null=True)
    reg_death_date = models.DateField(blank=True, null=True)
    death_reason = models.CharField(max_length=16, blank=True, null=True)
    main_death_reason = models.BooleanField()
    death_age = models.BigIntegerField(blank=True, null=True)
    dz_date = models.DateField(blank=True, null=True)
    dz_status = models.CharField(max_length=15, blank=True, null=True)
    dz_status_nullable = models.CharField(max_length=16, blank=True, null=True)
    dz_mkb = models.CharField(max_length=10, blank=True, null=True)
    dz_morph = models.CharField(max_length=10, blank=True, null=True)
    dz_tnm_t = models.CharField(max_length=5, blank=True, null=True)
    dz_tnm_n = models.CharField(max_length=5, blank=True, null=True)
    dz_tnm_m = models.CharField(max_length=5, blank=True, null=True)
    dz_tnm_g = models.CharField(max_length=5, blank=True, null=True)
    dz_stage = models.CharField(max_length=16, blank=True, null=True)
    dz_group_id = models.CharField(max_length=50, blank=True, null=True)
    dz_primary = models.CharField(max_length=16, blank=True, null=True)
    is_min_dz_date = models.BooleanField()
    clinical_group = models.CharField(max_length=16)
    tumor_main = models.CharField(max_length=16)
    dz_side = models.CharField(max_length=50, blank=True, null=True)
    dz_multiple = models.CharField(max_length=50, blank=True, null=True)
    dz_how_discovered = models.CharField(max_length=50, blank=True, null=True)
    dz_verify_method = models.CharField(max_length=50, blank=True, null=True)
    dz_loc_metastasis_unknown = models.BooleanField()
    dz_loc_metastasis_rln = models.BooleanField()
    dz_loc_metastasis_bones = models.BooleanField()
    dz_loc_metastasis_liver = models.BooleanField()
    dz_loc_metastasis_lung = models.BooleanField()
    dz_loc_metastasis_brain = models.BooleanField()
    dz_loc_metastasis_skin = models.BooleanField()
    dz_loc_metastasis_kidney = models.BooleanField()
    dz_loc_metastasis_ovary = models.BooleanField()
    dz_loc_metastasis_perotoneum = models.BooleanField()
    dz_loc_metastasis_bone_marrow = models.BooleanField()
    dz_loc_metastasis_other_organs = models.BooleanField()
    dz_loc_metastasis_plural = models.BooleanField()
    dz_late_reason = models.CharField(max_length=50, blank=True, null=True)
    dz_autopsy = models.CharField(max_length=16, blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)
    t_lifetime = models.BigIntegerField(blank=True, null=True)
    terr_unq = models.CharField(max_length=50, blank=True, null=True)
    onco_disp_last_dispensary_date = models.DateField(blank=True, null=True)
    register_json = models.JSONField()

    class Meta:
        managed = False
        db_table = 'stat_patients'


class StatPtn(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=20)
    created_date = models.DateField(blank=True, null=True)
    tags = models.JSONField(blank=True, null=True)
    snils_status = models.CharField(max_length=8, blank=True, null=True)
    gender = models.CharField(max_length=16)
    birth = models.DateField()
    blood_type = models.CharField(max_length=16, blank=True, null=True)
    living_area = models.CharField(max_length=8, blank=True, null=True)
    terr_id = models.CharField(max_length=16, blank=True, null=True)
    org_observer_id = models.CharField(max_length=16, blank=True, null=True)
    smo_id = models.CharField(max_length=16, blank=True, null=True)
    ptn_disable = models.CharField(max_length=30, blank=True, null=True)
    reg_in_date = models.DateField(blank=True, null=True)
    reg_in_age = models.IntegerField(blank=True, null=True)
    reg_in_clause = models.CharField(max_length=50, blank=True, null=True)
    reg_out_date = models.DateField(blank=True, null=True)
    reg_out_age = models.IntegerField(blank=True, null=True)
    reg_out_reason = models.CharField(max_length=50, blank=True, null=True)
    death_date = models.DateField(blank=True, null=True)
    death_age = models.IntegerField(blank=True, null=True)
    death_reason = models.CharField(max_length=16, blank=True, null=True)
    death_groups = models.JSONField()
    clinical_group = models.CharField(max_length=16)
    clinical_group_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stat_ptn'


class StatTreatment(models.Model):
    id = models.BigAutoField(primary_key=True)
    ptn_id = models.CharField(max_length=16)
    ptn_code = models.CharField(max_length=20)
    ehr_id = models.CharField(max_length=16)
    rc_id = models.CharField(max_length=16)
    rc_class_name = models.CharField(max_length=64)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    json = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stat_treatment'

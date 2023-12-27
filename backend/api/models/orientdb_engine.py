from django.db import models
from pyorient import OrientDB

from backend.settings import ORIENTDB_HOST, ORIENTDB_PORT, ORIENTDB_NAME, ORIENTDB_USER, ORIENTDB_PASSWORD

orient_db_client = OrientDB(ORIENTDB_HOST, ORIENTDB_PORT)
orient_db_client.db_open(ORIENTDB_NAME, ORIENTDB_USER, ORIENTDB_PASSWORD)


# Fantom OrientDB models for ModelViewSet
class Patient(models.Model):
    rid = models.CharField(max_length=16, primary_key=True, verbose_name='Patient rid')
    lastname = models.CharField(max_length=255, null=True, verbose_name='Patient last name')
    firstname = models.CharField(max_length=255, null=True, verbose_name='Patient first name')
    middlename = models.CharField(max_length=255, null=True, verbose_name='Patient middle name')
    birthday = models.DateField(null=True, verbose_name='Patient birthday')
    gender = models.CharField(max_length=1, null=True, verbose_name='Patient gender')
    code = models.CharField(max_length=16,  null=True, verbose_name='Patient extra abbreviation')
    snils = models.CharField(max_length=14, null=True, verbose_name='Patient SNILS')
    mo_oid = models.CharField(max_length=64, null=True, verbose_name='Patient assigned clinic oid')
    med_terr = models.CharField(max_length=255, null=True, verbose_name='Patient medical territory')
    is_in_cancer_register = models.BooleanField(verbose_name='Patient is in Cancer register flag')

    def __str__(self):
        return str(self.rid) + ': ' + str(self.lastname) + ' ' + \
            str(self.firstname) + ' ' + str(self.middlename)

    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'


"""
select @rid, person.lastName as lastname, person.firstName as firstname, person.middleName as middlename, person.birthDay as birthday, person.gender.value as gender, person.snils as shils from ptn where person.snils='093-643-704 85'
select from RcSms where @rid in (select records from ptn where @rid=#70:16091)
select diagnosis.registerDz.mkb10 as mkb10, diagnosis.registerDz.name as name from RcDz where @rid in (select records from ptn where @rid=#65:313)
select diagnosis.registerDz as rid, diagnosis.registerDz.mkb10 as mkb10, diagnosis.registerDz.name as name from (select EXPAND(records) from ptn where @rid=#65:1) where @class="RcDz"
select * from Ptn where tags.tags CONTAINS(tag in [#3058:1]) 
select @class, @rid, internalMessageId, title, smsSummaryJson, cdaXml.digest as cdaXml from (select EXPAND(records) from ptn where @rid=#70:16091) where @class="RcSMS"
select @rid, ehr.patient.@rid as ptn_rid, timeRc, internalMessageId, title, smsDocumentType, cdaXml.digest as cdaXml, smsSummaryJson from (select EXPAND(records) from ptn where @rid=#67:19790) where @class="RcSMS" order by timeRc
select timeRc as clinical_group_date, groupType as clinical_group_type from (select EXPAND(records) from ptn where @rid=#65:1) where @class="RcClinicalGroup"

select @rid, timeRc as diagnosis_date, diagnosis.icd10.rbps.MKB_CODE.value as mkb10, diagnosis.status.value as status, diagnosis.primacy.value as primacy, diagnosis.morphClass.rbps.DISABLED.value as morphClass_disabled, diagnosis.morphClass.rbps.CHILDCOUNT.value as morphClass_childcount, 
diagnosis.tumorMain.value as tumorMain, diagnosis.tumorSide.value as tumorSide, diagnosis.howDiscover.value as howDiscover,
diagnosis.method.value as method, diagnosis.plural.value as plural, diagnosis.resAutopsy.value as resAutopsy, diagnosis.whyOld.value as whyOld, diagnosis.locMet.names as locMet, diagnosis.tnm.t as tnm_t, diagnosis.tnm.n as tnm_n, diagnosis.tnm.m as tnm_m, diagnosis.tnm.g as tnm_g, 
diagnosis.stage as stage from (select EXPAND(records) from ptn where @rid=#65:313) where @class="RcDz"
"""

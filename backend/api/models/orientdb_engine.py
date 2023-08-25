from django.db import models
from pyorient import OrientDB

from backend.settings import ORIENTDB_HOST, ORIENTDB_PORT, ORIENTDB_NAME, ORIENTDB_USER, ORIENTDB_PASSWORD

orient_db_client = OrientDB(ORIENTDB_HOST, ORIENTDB_PORT)
orient_db_client.db_open(ORIENTDB_NAME, ORIENTDB_USER, ORIENTDB_PASSWORD)


# Fantom OrientDB models for ModelViewSet
class Patient(models.Model):
    rid = models.CharField(primary_key=True, verbose_name='Patient rid')

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
"""

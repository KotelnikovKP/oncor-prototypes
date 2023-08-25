from django.db import models


class FrmrReceiving(models.Model):
    id = models.BigAutoField(primary_key=True)
    message_id = models.CharField(max_length=64)
    external_message_id = models.CharField(max_length=64)
    payload = models.TextField()
    oid = models.CharField(max_length=128)
    date_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'frmr_receiving'


class FrmrSending(models.Model):
    internal_message_id = models.CharField(primary_key=True, max_length=64)
    external_message_id = models.CharField(max_length=64, blank=True, null=True)
    service_name = models.CharField(max_length=32)
    payload = models.TextField()
    oid = models.CharField(max_length=128)
    state = models.CharField(max_length=16)
    date_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'frmr_sending'


class Logs(models.Model):
    code = models.UUIDField(primary_key=True)
    internal_message_id = models.CharField(max_length=64, blank=True, null=True)
    exception_class_name = models.CharField(max_length=64)
    exception_message = models.TextField(blank=True, null=True)
    datetime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'logs'


class VimisReceiving(models.Model):
    id = models.BigAutoField(primary_key=True)
    external_message_id = models.CharField(max_length=64)
    message_id = models.CharField(max_length=64)
    status = models.CharField(max_length=32)
    status_description = models.TextField(blank=True, null=True)
    date_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'vimis_receiving'


class VimisSending(models.Model):
    internal_message_id = models.CharField(primary_key=True, max_length=64)
    external_message_id = models.CharField(max_length=64, blank=True, null=True)
    document_type = models.CharField(max_length=8)
    document_type_version = models.CharField(max_length=4)
    vmcl = models.CharField(max_length=4)
    payload = models.TextField()
    sms_profile = models.CharField(max_length=8)
    state = models.CharField(max_length=16)
    date_time = models.DateTimeField()
    parameters = models.JSONField(blank=True, null=True)
    trigger_point = models.CharField(max_length=4)

    class Meta:
        managed = False
        db_table = 'vimis_sending'

from django.db import models


class Directory(models.Model):
    passport_oid = models.CharField(max_length=128)  # The composite primary key (passport_oid, version, id) found, that is not supported. The first column is selected.
    version = models.CharField(max_length=32)
    id = models.CharField(max_length=8)
    code = models.CharField(max_length=42, blank=True, null=True)
    oid = models.CharField(max_length=64, blank=True, null=True)
    name = models.CharField(max_length=2048)
    raw_json = models.JSONField()
    json = models.JSONField()

    class Meta:
        managed = False
        db_table = 'directory'
        unique_together = (('passport_oid', 'version', 'id'),)

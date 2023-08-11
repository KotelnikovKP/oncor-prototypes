from django.db import models
from django.db.models import Index


class MedicalService(models.Model):
    ms_code = models.CharField(max_length=25, primary_key=True, verbose_name='Medical service code')
    name = models.CharField(max_length=500, verbose_name='Medical service name')
    rel = models.IntegerField(verbose_name='Sign of relevance')
    dateout = models.DateField(null=True, blank=True, verbose_name='Date out')

    def __str__(self):
        return str(self.ms_code) + ' ' + str(self.name)

    class Meta:
        verbose_name = 'Medical service'
        verbose_name_plural = 'Medical services'
        ordering = ['ms_code']
        indexes = (
            Index(fields=['name'], name='med_ser__name__idx'),
        )


class Diagnosis(models.Model):
    mkb_code = models.CharField(max_length=15, primary_key=True, verbose_name='Diagnosis code (MKB-10)')
    rec_code = models.CharField(max_length=15, verbose_name='Sorted code')
    id = models.IntegerField(verbose_name='Identifier')
    id_parent = models.IntegerField(null=True, blank=True, verbose_name='Parent identifier')
    name = models.CharField(max_length=300, verbose_name='Diagnosis name')
    add_code = models.IntegerField(null=True, blank=True, verbose_name='Addition code')
    rel = models.IntegerField(verbose_name='Sign of relevance')
    dateout = models.DateField(null=True, blank=True, verbose_name='Date out')

    def __str__(self):
        return str(self.mkb_code) + ' ' + str(self.name)

    class Meta:
        verbose_name = 'Diagnosis'
        verbose_name_plural = 'Diagnoses'
        ordering = ['rec_code']
        indexes = (
            Index(fields=['rec_code'], name='dia__rec_code__idx'),
            Index(fields=['name'], name='dia__name__idx'),
            Index(fields=['id'], name='dia__id__idx'),
            Index(fields=['id_parent'], name='dia__id_parent__idx'),
        )


class MedicalOrganization(models.Model):
    oid = models.CharField(max_length=35, primary_key=True, verbose_name='Medical organization code')
    id = models.IntegerField(verbose_name='Identifier')
    nameFull = models.CharField(max_length=400, verbose_name='Medical organization full name')
    nameShort = models.CharField(max_length=350, null=True, blank=True, verbose_name='Medical organization short name')
    medicalSubjectId = models.IntegerField(null=True, blank=True, verbose_name='Medical subject code')
    medicalSubjectName = models.CharField(max_length=140, null=True, blank=True, verbose_name='Medical subject name')
    inn = models.CharField(max_length=12, null=True, blank=True, verbose_name='INN')
    kpp = models.CharField(max_length=9, null=True, blank=True, verbose_name='KPP')
    ogrn = models.CharField(max_length=15, null=True, blank=True, verbose_name='OGRN')
    regionId = models.IntegerField(null=True, blank=True, verbose_name='Region code')
    regionName = models.CharField(max_length=50, null=True, blank=True, verbose_name='Region name')
    moAgencyKind = models.CharField(max_length=70, null=True, blank=True, verbose_name='Agency kind')

    def __str__(self):
        return str(self.oid) + ' ' + str(self.nameShort)

    class Meta:
        verbose_name = 'Medical organization'
        verbose_name_plural = 'Medical organizations'
        ordering = ['oid']
        indexes = (
            Index(fields=['nameShort'], name='med_org__name__idx'),
            Index(fields=['id'], name='med_org__id__idx'),
        )


class LaboratoryTest(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='Laboratory test code')
    name = models.CharField(max_length=300, verbose_name='Laboratory test name')
    eng_name = models.CharField(max_length=300, null=True, blank=True, verbose_name='Laboratory test english name')
    short_name = models.CharField(max_length=250, null=True, blank=True, verbose_name='Laboratory test short name')
    group_tests = models.CharField(max_length=100, null=True, blank=True, verbose_name='Group tests name')
    mkb10_codes = models.CharField(max_length=300, null=True, blank=True, verbose_name='Medical service codes')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Laboratory test'
        verbose_name_plural = 'Laboratory tests'
        ordering = ['id']
        indexes = (
            Index(fields=['name'], name='lab_tes__name__idx'),
        )


class MedicalPosition(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='Medical position code')
    pid = models.IntegerField(null=True, blank=True, verbose_name='Parent code')
    sort = models.IntegerField(verbose_name='Sort number')
    name = models.CharField(max_length=180, verbose_name='Medical position name')
    equivalent = models.CharField(max_length=180, null=True, blank=True,
                                  verbose_name='Medical position name equivalent')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Medical position'
        verbose_name_plural = 'Medical positions'
        ordering = ['sort']
        indexes = (
            Index(fields=['sort'], name='med_pos__sort__idx'),
            Index(fields=['name'], name='med_pos__name__idx'),
        )

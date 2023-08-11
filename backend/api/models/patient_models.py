from django.db import models
from django.db.models import Index, UniqueConstraint


class Patient(models.Model):
    snils = models.CharField(max_length=11, primary_key=True, verbose_name='Patient SNILS')
    name = models.CharField(max_length=255, verbose_name='Patient name')
    gender = models.CharField(max_length=7, null=True, blank=True, verbose_name='Patient gender')
    birthday = models.DateField(null=True, blank=True, verbose_name='Patient birthday')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['name']
        indexes = (
            Index(fields=['name'], name='pat__name__idx'),
        )


class PatientDiagnosis(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.PROTECT, related_name='diagnoses',
                                null=True, blank=True, verbose_name='patient')
    diagnosis = models.ForeignKey('Diagnosis', on_delete=models.PROTECT, related_name='patients',
                                  null=True, blank=True, verbose_name='diagnosis')

    def __str__(self):
        return str(self.patient_id) + ' ' + str(self.diagnosis_id)

    class Meta:
        verbose_name = 'Patient diagnosis'
        verbose_name_plural = 'Patients diagnoses'
        ordering = ['patient_id']
        indexes = (
            Index(fields=['diagnosis_id'], name='pat_dia__diagnosis__idx'),
        )
        constraints = (
            UniqueConstraint(fields=['patient_id', 'diagnosis_id'], name='pat_dia__snils_dia__unq'),
        )


class PatientMedicalCard(models.Model):
    card_type = models.CharField(max_length=3, verbose_name='Medical card type')
    card_number = models.CharField(max_length=40, verbose_name='Medical card number')
    patient = models.ForeignKey('Patient', on_delete=models.PROTECT, related_name='medical_cards',
                                null=True, blank=True, verbose_name='patient')

    def __str__(self):
        return str(self.patient_id) + ' ' + str(self.card_type) + ' ' + str(self.card_number)

    class Meta:
        verbose_name = 'Patient medical card'
        verbose_name_plural = 'Patients medical cards'
        ordering = ['patient_id']
        indexes = (
            Index(fields=['card_number'], name='pat_car__card_number__idx'),
        )
        constraints = (
            UniqueConstraint(fields=['patient_id', 'card_type', 'card_number'], name='pat_car__snils_t_n__unq'),
        )



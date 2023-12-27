from datetime import datetime

from django.db import transaction

from api.models.orientdb_engine import orient_db_client
from api.models.semd_models import PatientRecord, PatientDiagnosis


def run(*args):
    print("-----------------------------------------------------------------------")
    print(f"Procedure FILL PATIENTS CANCER REGISTER DIAGNOSES was stated!")
    if 'erase-diagnoses' in args:
        print("Found 'erase-diagnoses' parameter, it is starting delete records...")
        with transaction.atomic():
            patient_diagnosis = PatientDiagnosis.objects.all()
            patient_diagnosis.delete()
        print("    Patient Cancer Register Diagnoses were cleaned")

    # Get queryset
    patient_records = PatientRecord.objects.filter(rc_type='RcDz')
    count = len(patient_records)
    print(f'Found {count} diagnoses.')

    i = n = 0
    # Get records for each diagnoses in queryset
    for record in patient_records:
        ptn_id = record.ptn_id
        rc_id = record.rc_id
        i += 1

        print(f"{str(i).zfill(6)} from {count}: {rc_id}")
        # Define diagnosis query
        query_body = f'''
            select 
                @rid, 
                timeRc.format('yyyy-MM-dd') as diagnosis_date, 
                diagnosis.registerDz.mkb10 as diagnosis_mkb10, 
                diagnosis.status.value as status, 
                diagnosis.primacy.value as primacy, 
                diagnosis.morphClass.rbps.DISABLED.value as morphClass_disabled, 
                diagnosis.morphClass.rbps.CHILDCOUNT.value as morphClass_childcount, 
                diagnosis.morphClass.rbps.S_NAME.value as morphClass_sname, 
                diagnosis.tumorMain.value as tumorMain, 
                diagnosis.tumorSide.value as tumorSide, 
                diagnosis.howDiscover.value as howDiscover,
                diagnosis.method.value as method, 
                diagnosis.plural.value as plural, 
                diagnosis.resAutopsy.value as resAutopsy, 
                diagnosis.whyOld.value as whyOld, 
                diagnosis.locMet.names as locMet, 
                diagnosis.tnm.t as tnm_t, 
                diagnosis.tnm.n as tnm_n, 
                diagnosis.tnm.m as tnm_m, 
                diagnosis.tnm.g as tnm_g, 
                diagnosis.stage as stage 
            from 
                RcDz
            where
                @rid={rc_id}
        '''

        # Get records
        try:
            diagnosis = orient_db_client.query(query_body, -1)[0]
        except Exception:
            diagnosis = None

        if diagnosis and diagnosis.oRecordData.get('diagnosis_mkb10', None):
            with transaction.atomic():
                # Save patient diagnosis
                diagnosis_date = diagnosis.oRecordData.get('diagnosis_date', None)
                if diagnosis_date and len(diagnosis_date) != 10:
                    diagnosis_date = diagnosis_date.split('-')
                    if len(diagnosis_date) == 3:
                        diagnosis_date = diagnosis_date[0][:4] + '-' + diagnosis_date[1][:2] + '-' + diagnosis_date[2][:2]
                    diagnosis_date = datetime.strptime(diagnosis_date, '%Y-%m-%d').date()
                diagnosis_mkb10 = diagnosis.oRecordData.get('diagnosis_mkb10', None)
                if diagnosis_mkb10:
                    diagnosis_mkb10 = str(diagnosis_mkb10)[:10]
                status = diagnosis.oRecordData.get('status', None)
                if status:
                    status = str(status)[:64]
                primacy = diagnosis.oRecordData.get('primacy', None)
                if primacy:
                    primacy = str(primacy)[:64]
                morph_class_disabled = diagnosis.oRecordData.get('morphClass_disabled', None)
                if morph_class_disabled:
                    morph_class_disabled = str(morph_class_disabled)[:64]
                morph_class_child_count = diagnosis.oRecordData.get('morphClass_childcount', None)
                if morph_class_child_count:
                    morph_class_child_count = str(morph_class_child_count)[:64]
                morph_class_sname = diagnosis.oRecordData.get('morphClass_sname', None)
                if morph_class_sname:
                    morph_class_sname = str(morph_class_sname)[:64]
                tumor_main = diagnosis.oRecordData.get('tumorMain', None)
                if tumor_main:
                    tumor_main = str(tumor_main)[:64]
                tumor_side = diagnosis.oRecordData.get('tumorSide', None)
                if tumor_side:
                    tumor_side = str(tumor_side)[:64]
                how_discover = diagnosis.oRecordData.get('howDiscover', None)
                if how_discover:
                    how_discover = str(how_discover)[:64]
                method = diagnosis.oRecordData.get('method', None)
                if method:
                    method = str(method)[:64]
                plural = diagnosis.oRecordData.get('plural', None)
                if plural:
                    plural = str(plural)[:64]
                res_autopsy = diagnosis.oRecordData.get('resAutopsy', None)
                if res_autopsy:
                    res_autopsy = str(res_autopsy)[:64]
                why_old = diagnosis.oRecordData.get('whyOld', None)
                if why_old:
                    why_old = str(why_old)[:64]
                loc_met = diagnosis.oRecordData.get('locMet', None)
                if loc_met:
                    loc_met = str(loc_met)[:64]
                tnm_t = diagnosis.oRecordData.get('tnm_t', None)
                if tnm_t:
                    tnm_t = str(tnm_t)[:64]
                tnm_n = diagnosis.oRecordData.get('tnm_n', None)
                if tnm_n:
                    tnm_n = str(tnm_n)[:64]
                tnm_m = diagnosis.oRecordData.get('tnm_m', None)
                if tnm_m:
                    tnm_m = str(tnm_m)[:64]
                tnm_g = diagnosis.oRecordData.get('tnm_g', None)
                if tnm_g:
                    tnm_g = str(tnm_g)[:64]
                stage = diagnosis.oRecordData.get('stage', None)
                if stage:
                    stage = str(stage)[:64]

                patient_diagnosis = PatientDiagnosis(
                    ptn_id=ptn_id,
                    rc_id=rc_id,
                    diagnosis_date=diagnosis_date,
                    diagnosis_mkb10=diagnosis_mkb10,
                    status=status,
                    primacy=primacy,
                    morph_class_disabled=morph_class_disabled,
                    morph_class_child_count=morph_class_child_count,
                    morph_class_sname=morph_class_sname,
                    tumor_main=tumor_main,
                    tumor_side=tumor_side,
                    how_discover=how_discover,
                    method=method,
                    plural=plural,
                    res_autopsy=res_autopsy,
                    why_old=why_old,
                    loc_met=loc_met,
                    tnm_t=tnm_t,
                    tnm_n=tnm_n,
                    tnm_m=tnm_m,
                    tnm_g=tnm_g,
                    stage=stage
                )
                patient_diagnosis.save()
                n += 1

    print(f"Diagnoses count = {n} (from {count})")

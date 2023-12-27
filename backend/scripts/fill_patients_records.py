from datetime import datetime, timezone

from django.db import transaction, connection

from api.models.orientdb_engine import orient_db_client, Patient
from api.models.semd_models import PatientRecord


def run(*args):
    first_rid = None
    for arg in args:
        if arg[:4] == 'rid=':
            try:
                first_rid = arg[4:]
            except Exception:
                pass
    print("-----------------------------------------------------------------------")
    print(f"Procedure FILL PATIENTS RECORDS with first rid = {first_rid} was stated!")
    if 'erase-records' in args:
        print("Found 'erase-records' parameter, it is starting delete records...")
        with transaction.atomic():
            patient_record = PatientRecord.objects.all()
            patient_record.delete()
        print("    Patient Cancer Register Records were cleaned")
        with transaction.atomic():
            patient = Patient.objects.all()
            patient.delete()
        print("    Patients were cleaned")

    # Define queries
    query_body = """
        SELECT
            @rid,
            person.lastName as lastname,
            person.firstName as firstname,
            person.middleName as middlename,
            person.birthDay.format('yyyy-MM-dd') as birthday,
            person.gender.value as gender,
            person.code as code,
            person.snils as snils,
            observer.nsiMedOrg.oid as mo_oid,
            person.address.medTerr.name as med_terr
        FROM
            ptn
    """
    query_count_body = """
        SELECT
            count(*)
        FROM
            ptn
    """
    if first_rid:
        query_body += f"""
        WHERE
            @rid >= {first_rid}
        """
        query_count_body += f"""
        WHERE
            @rid >= {first_rid}
        """

    # Calculate count of queryset
    orient_result = orient_db_client.query(query_count_body, -1)
    count = orient_result[0].count
    print(f'Found {count} patients.')

    # Get queryset
    patients = orient_db_client.query(query_body, -1)

    i = 0
    # Get records for each patient in queryset
    for patient in patients:
        # Get patient parameters
        ptn_id = str(patient.oRecordData.get('rid', None))
        ptn_lastname = patient.oRecordData.get('lastname', None)
        ptn_firstname = patient.oRecordData.get('firstname', None)
        ptn_middlename = patient.oRecordData.get('middlename', None)
        ptn_birthday = patient.oRecordData.get('birthday', None)
        if ptn_birthday:
            if len(ptn_birthday) != 10:
                ptn_birthday = ptn_birthday.split('-')
                if len(ptn_birthday) == 3:
                    ptn_birthday = ptn_birthday[0][:4] + '-' + ptn_birthday[1][:2] + '-' + ptn_birthday[2][:2]
            ptn_birthday = datetime.strptime(ptn_birthday, '%Y-%m-%d').date()
        ptn_gender = patient.oRecordData.get('gender', None)
        ptn_code = patient.oRecordData.get('code', None)
        ptn_snils = patient.oRecordData.get('snils', None)
        if ptn_snils:
            ptn_snils = ptn_snils.replace('-', '')
            ptn_snils = ptn_snils.replace(' ', '')
            ptn_snils = ptn_snils[:3] + '-' + ptn_snils[3:6] + '-' + ptn_snils[6:9] + ' ' + ptn_snils[9:11]
        ptn_mo_oid = patient.oRecordData.get('mo_oid', None)
        ptn_med_terr = patient.oRecordData.get('med_terr', None)
        i += 1
        print(f"{str(i).zfill(6)} from {count}: {ptn_id}")

        if not ptn_id:
            continue

        # Start transaction for each patient
        with transaction.atomic():
            # Save patient
            patient = Patient(
                rid=ptn_id,
                lastname=ptn_lastname,
                firstname=ptn_firstname,
                middlename=ptn_middlename,
                birthday=ptn_birthday,
                gender=None if ptn_gender is None else ptn_gender[:1],
                code=ptn_code,
                snils=ptn_snils,
                mo_oid=ptn_mo_oid,
                med_terr=ptn_med_terr,
                is_in_cancer_register=False
            )
            patient.save()

    n = 0
    for cls in ["RcChem", "RcHorm", "RcHosp", "RcOper", "RcRay", "RcSpecTreat", "RcClinicalGroup", "RcDeath", "RcForm90", "RcObs", "RcRegIn", "RcRegOut", "RcDz"]:
        # Define records queries
        query_body = f'''
            SELECT 
                @rid, timeRc, timeRcIn, timeRcOut, ehr.patient as ptn_id
            FROM
                {cls} 
        '''
        query_count_body = f"""
            SELECT 
                count(*) 
            FROM 
                {cls}
        """

        # Calculate count of queryset
        orient_result = orient_db_client.query(query_count_body, -1)
        count = orient_result[0].count
        print(f'Found {count} {cls} records.')

        # Get records
        records = orient_db_client.query(query_body, -1)
        n += count

        # Save patient records
        i = 0
        for record in records:
            rc_time = record.oRecordData.get('timeRc', None)
            if rc_time:
                rc_time = datetime(rc_time.year, rc_time.month, rc_time.day, rc_time.hour,
                                   rc_time.minute, rc_time.second, tzinfo=timezone.utc)
            rc_time_in = record.oRecordData.get('timeRcIn', None)
            if rc_time_in:
                rc_time_in = datetime(rc_time_in.year, rc_time_in.month, rc_time_in.day, rc_time_in.hour,
                                      rc_time_in.minute, rc_time_in.second, tzinfo=timezone.utc)
            rc_time_out = record.oRecordData.get('timeRcOut', None)
            if rc_time_out:
                rc_time_out = datetime(rc_time_out.year, rc_time_out.month, rc_time_out.day, rc_time_out.hour,
                                       rc_time_out.minute, rc_time_out.second, tzinfo=timezone.utc)

            ptn_id = record.oRecordData.get('ptn_id', 'None')
            rc_id = record.oRecordData.get('rid', 'None')

            i += 1
            print(f"{str(i).zfill(6)} from {count} in {cls}: {rc_id}")
            with transaction.atomic():
                patient_record = PatientRecord(
                    ptn_id=ptn_id,
                    rc_id=rc_id,
                    rc_type=cls,
                    rc_time=rc_time,
                    rc_time_in=rc_time_in,
                    rc_time_out=rc_time_out
                )
                patient_record.save()

    print(f"Records count = {n}")

    query_body = """
        UPDATE
            api_patient p
        SET
            is_in_cancer_register = true
        WHERE EXISTS (
            SELECT
                r.*
            FROM
                api_patientrecord r
            WHERE
                r.ptn_id = p.rid
        );
    """

    with connection.cursor() as cursor:
        cursor.execute(query_body)

    print("Is cancer register flags were set")

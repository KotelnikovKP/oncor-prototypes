from django.db import connections, transaction

from api.models.egisz_db_66_models import VimisSending
from api.models.rosminzdrav_directories_models import Directory


def run():
    print("-----------------------------------------------------------------------")
    print("Procedure FILL EGIZ-DB-66 was stated!")
    bad_xml = []
    i = 0
    while True:
        with transaction.atomic():
            vss = (
                VimisSending.objects
                .using('egisz-db-66')
                .filter(
                    medical_organization_id__isnull=True
                )
                .exclude(internal_message_id__in=bad_xml)
            )[:1000]
            is_empty = True
            for vs in vss:
                is_empty = False
                try:
                    query_body = """
                        SELECT
                            array_to_string(xpath('/x:ClinicalDocument/x:author/x:assignedAuthor/x:representedOrganization/x:id/@root', regexp_replace(s.payload,':DocType','','g')::xml, '{{x,urn:hl7-org:v3}}'), ' ') as medical_organization_id,
                            array_to_string(xpath('/x:ClinicalDocument/x:author/x:assignedAuthor/x:representedOrganization/x:id/@extension', regexp_replace(s.payload,':DocType','','g')::xml, '{{x,urn:hl7-org:v3}}'), ' ') as medical_organization_extension
                        FROM
                            vimis_sending s
                        WHERE
                            s.internal_message_id = '""" + vs.internal_message_id + "'"

                    with connections['egisz-db-66'].cursor() as cursor:
                        cursor.execute(query_body)
                        medical_organization_id, medical_organization_extension = cursor.fetchone()

                    medical_organization_name = None
                    medical_organization_city = None
                    mo = None
                    try:
                        mo = (
                            Directory.objects
                            .using('rosminzdrav-directories')
                            .filter(
                                passport_oid='1.2.643.5.1.13.13.11.1461',
                                oid=medical_organization_id
                            )
                        )[0]
                    except:
                        pass
                    if mo:
                        medical_organization_name = mo.name
                        medical_organization_city = mo.json["areaName"]

                    medical_organization_extension_name = None
                    me = None
                    try:
                        me = (
                            Directory.objects
                            .using('rosminzdrav-directories')
                            .filter(
                                passport_oid='1.2.643.5.1.13.13.99.2.114',
                                oid=medical_organization_extension
                            )
                        )[0]
                    except:
                        pass
                    if me:
                        medical_organization_extension_name = me.name

                    vs.medical_organization_id = medical_organization_id
                    vs.medical_organization_extension = medical_organization_extension
                    vs.medical_organization_name = medical_organization_name
                    vs.medical_organization_city = medical_organization_city
                    vs.medical_organization_extension_name = medical_organization_extension_name
                    vs.save()
                    i += 1

                except Exception as e:
                    bad_xml.append(vs.internal_message_id)
                    print(f"internal_message_id={vs.internal_message_id}, error={type(e)}, {str(e)}")

        print(i)
        if is_empty:
            break

    print('Finish!')
    print(bad_xml)
    print(len(bad_xml))

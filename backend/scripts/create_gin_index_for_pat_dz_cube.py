from django.db import connection


def run(*args):
    # Get protocols count
    query_body = """
        CREATE INDEX api_patientdiagnosismilestones_diagnosis_milestones
        ON api_patientdiagnosismilestones
        USING GIN (diagnosis_milestones)
    """
    with connection.cursor() as cursor:
        cursor.execute(query_body)

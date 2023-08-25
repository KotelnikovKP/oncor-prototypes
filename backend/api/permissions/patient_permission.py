from rest_framework import permissions


class PatientPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        if view.action in ['list', 'retrieve', 'diagnoses', 'semds', 'tests', 'registry_report']:
            return request.user.is_authenticated
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.method == 'OPTIONS':
            return True
        if view.action in ['list', 'retrieve', 'diagnoses', 'semds', 'tests', 'registry_report']:
            return request.user.is_authenticated
        else:
            return False

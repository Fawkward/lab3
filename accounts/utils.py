import logging
from .models import AuditLog

def log_audit_action(user, description):
    AuditLog.objects.create(user=user, description=description)

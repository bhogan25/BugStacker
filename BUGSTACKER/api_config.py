# API Error Response Messages
JSON_ERROR_MESSAGES = {
    "unknown_error": {"error": "SERVER: Unknown error"},
    "invalid_action": {"error": "SERVER: Invalid action."},
    "access_denied": {"error": "SERVER: Access denied."},
    "invalid_payload": {"error": "SERVER: Invalid payload."},
    "mulitple_objects": {"error": "SERVER: Action returned multiple objects."},
    "object_does_not_exist": {"error": "SERVER: Action requested object that does not exist."},
}

# API Access Permissions
# ----------------------
# Project API
PROJECT_API_ALLOWED_ACTIONS = ['change_status', 'complete']

# Workflow API
WORKFLOW_API_ALLOWED_ACTIONS = ['change_archive_state']

# Ticket API
TICKET_API_ALLOWED_ACTIONS = ['advance-status']
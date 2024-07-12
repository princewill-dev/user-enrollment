# enroll/utils.py

def create_response(status, statuscode, message, details=None):
    if status == 'error':
        error_message = message
        if isinstance(details, dict):
            error_details = list(details.values())[0][0] if details else message
            error_message = error_details if error_details else message
        return {
            'status': status,
            'message': error_message,
            'code': statuscode,
            'details': details
        }
    else:
        return {
            'status': status,
            'message': message,
            'details': details
        }

# enroll/utils.py

def create_response(status, statuscode, message, details=None):
    response = {
        'status': status,
        'message': message,
        'details': details,
    }
    if status == 'error':
        response['error'] = {
            'code': statuscode,
            'message': message,
            'details': details,
        }
    return response

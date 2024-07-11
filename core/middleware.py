# core/middleware.py

from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin

class JSONErrorMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, ValidationError):
            response_data = {
                'status': 'error',
                'error': {
                    'code': 400,
                    'message': 'Validation Error',
                    'details': exception.message_dict if hasattr(exception, 'message_dict') else str(exception)
                }
            }
            return JsonResponse(response_data, status=400)
        
        if isinstance(exception, Http404):
            response_data = {
                'status': 'error',
                'error': {
                    'code': 404,
                    'message': 'Not Found',
                    'details': str(exception)
                }
            }
            return JsonResponse(response_data, status=404)
        
        response_data = {
            'status': 'error',
            'error': {
                'code': 500,
                'message': 'Internal Server Error',
                'details': str(exception)
            }
        }
        return JsonResponse(response_data, status=500)

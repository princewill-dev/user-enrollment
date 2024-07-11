# core/views.py

from django.http import JsonResponse

def custom_404(request, exception):
    response_data = {
        'status': 'error',
        'error': {
            'code': 404,
            'message': 'Not Found',
            'details': 'The requested resource was not found'
        }
    }
    return JsonResponse(response_data, status=404)

def custom_500(request):
    response_data = {
        'status': 'error',
        'error': {
            'code': 500,
            'message': 'Internal Server Error',
            'details': 'An unexpected error occurred'
        }
    }
    return JsonResponse(response_data, status=500)

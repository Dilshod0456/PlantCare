import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

# Try to import AI utils, fallback to simple version
try:
    from .ai_utils import chat_with_ai
except ImportError:
    from .ai_utils_simple import chat_with_ai

@csrf_exempt
@require_http_methods(["POST"])
def chat_ai(request):
    try:
        # Get data from request
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
            
        question = data.get('question', '').strip()
        lang = data.get('lang', 'uz')
        
        if not question:
            return JsonResponse({
                'error': True,
                'message': 'Savol bo\'sh bo\'lmasligi kerak.'
            }, status=400)
        
        # Get AI response
        answer = chat_with_ai(question, lang=lang)
        
        return JsonResponse({
            'error': False,
            'answer': answer,
            'question': question
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': True,
            'message': 'Noto\'g\'ri JSON format.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': True,
            'message': f'Server xatolik: {str(e)}'
        }, status=500)

"""
Views for handling webhook endpoints.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .validators import validate_twilio_webhook


@csrf_exempt
@require_http_methods(["POST"])
def twilio_events_webhook(request):
    """
    Webhook endpoint for receiving event streams from Twilio.
    """
    try:
        '''
        # Validate Twilio webhook signature here (uncomment, when auth token is ready)

        auth_token = os.environ.get('TWILIO_AUTH_TOKEN', '')
        
        is_valid, error_response = validate_twilio_webhook(request, auth_token)
        if not is_valid:
            return error_response

        '''
        
        content_type = request.content_type
        
        if 'application/json' in content_type:
            data = json.loads(request.body)
        else:
            data = dict(request.POST)
        
        print("Received Twilio event:")
        print(json.dumps(data, indent=2))
        
        # for logging (will be removed later) [line 43 - 52]
        event_logs_dir = os.path.join(settings.BASE_DIR, 'event_logs')
        os.makedirs(event_logs_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f') ## creating folder
        filename = f'twilio_event_{timestamp}.json'
        filepath = os.path.join(event_logs_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        

        # business logic here
        
        return HttpResponse(status=204)
        
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return HttpResponse(status=400)
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return HttpResponse(status=500)

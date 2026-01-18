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
        # Validate Twilio webhook signature

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
        
        # Log the received event (you can replace this with your own logic)
        print("Received Twilio event:")
        print(json.dumps(data, indent=2))
        
        # Create event_logs directory if it doesn't exist
        event_logs_dir = os.path.join(settings.BASE_DIR, 'event_logs')
        os.makedirs(event_logs_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f'twilio_event_{timestamp}.json'
        filepath = os.path.join(event_logs_dir, filename)
        
        # Save event to file
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Event saved to: {filepath}")
        
        # Process the event here
        # Add your custom logic to handle different types of Twilio events
        
        return HttpResponse(status=204)
        
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return HttpResponse(status=400)
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return HttpResponse(status=500)

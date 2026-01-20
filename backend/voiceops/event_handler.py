"""
Event handler for processing Twilio events in real-time.
Sends events to frontend via Socket.IO and stores in database.
"""
import socketio
from datetime import datetime
from asgiref.sync import sync_to_async
from events.models import (
    Call, CallInitiatedEvent, CallRingingEvent, 
    CallAnsweredEvent, CallCompletedEvent, ErrorEvent
)

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',  # for development
    logger=True,
    engineio_logger=True
)


def get_or_create_call(event_data):
    """
    Get or create a Call record from event data.
    """
    params = {}
    
    if 'data' in event_data and 'request' in event_data['data']:
        params = event_data['data']['request'].get('parameters', {})
    elif 'request' in event_data:
        params = event_data['request'].get('parameters', {})
    
    call_sid = params.get('CallSid')
    
    if not call_sid:
        raise ValueError("Cannot find CallSid in event data")
    
    from_number = params.get('From')
    to_number = params.get('To')
    direction = params.get('Direction')
    call_status = params.get('CallStatus', '')
    
    call, created = Call.objects.get_or_create(
        call_sid=call_sid,
        defaults={
            'direction': direction,
            'from_number': from_number,
            'to_number': to_number,
            'call_status': call_status,
            'additional_data': event_data
        }
    )
    
    # Update fields if call already exists
    if not created:
        if from_number and not call.from_number:
            call.from_number = from_number
        if to_number and not call.to_number:
            call.to_number = to_number
        if direction and not call.direction:
            call.direction = direction
        if call_status:
            call.call_status = call_status
        call.save()
    
    return call


def store_event_in_database(event_data):
    """
    Store event in database based on event type.
    """
    try:
        call = get_or_create_call(event_data)
        
        event_type_full = event_data.get('type', '')
        event_type = None
        
        if 'call.initiated' in event_type_full:
            event_type = 'initiated'
        elif 'call.ringing' in event_type_full:
            event_type = 'ringing'
        elif 'call.answer' in event_type_full:
            event_type = 'answered'
        elif 'call.completed' in event_type_full:
            event_type = 'completed'
        elif 'error' in event_type_full:
            event_type = 'error'
        
        if event_type == 'initiated':
            CallInitiatedEvent.objects.create(
                call=call,
                event_data=event_data
            )
        elif event_type == 'ringing':
            CallRingingEvent.objects.create(
                call=call,
                event_data=event_data
            )
        elif event_type == 'answered' or event_type == 'in-progress':
            CallAnsweredEvent.objects.create(
                call=call,
                event_data=event_data
            )
        elif event_type == 'completed':
            CallCompletedEvent.objects.create(
                call=call,
                event_data=event_data
            )
        elif event_type == 'error':
            # Extract params for error checking
            params = {}
            if 'data' in event_data and 'request' in event_data['data']:
                params = event_data['data']['request'].get('parameters', {})
            elif 'request' in event_data:
                params = event_data['request'].get('parameters', {})
            
            ErrorEvent.objects.create(
                call=call,
                error_code=params.get('ErrorCode', ''),
                error_message=params.get('ErrorMessage', ''),
                event_data=event_data
            )
        else:
            # Default: store as completed if we can't determine type
            print(f"Unknown event type: {event_type}, storing as additional data in Call")
        
        return True, call
    except Exception as e:
        print(f"Error storing event in database: {e}")
        return False, None


async def process_and_emit_event(event_data):
    """
    Main function to process event: emit to frontend and store in DB.
    This ensures low latency by emitting first, then storing.
    """
    try:
        # Check for error event 
        event_type_full = event_data.get('type', '')
        
        if 'error-logs.error.logged' in event_type_full:
            data = event_data.get('data', {})
            error_code = data.get('error_code', '')
            call_sid = data.get('correlation_sid', '')
            error_message = data.get('level', 'WARNING')
            
            error_emit_data = {
                'event_id': event_data.get('id', ''),
                'call_sid': call_sid,
                'timestamp': event_data.get('time') or datetime.now().isoformat(),
                'error_code': error_code,
                'error_message': error_message,
            }
            await sio.emit('new_error', error_emit_data)
            print(f"Emitted error event to frontend: {error_code}") ## for testing
        else:
            # Handle call event 
            params = {}
            if 'data' in event_data and 'request' in event_data['data']:
                params = event_data['data']['request'].get('parameters', {})
            elif 'request' in event_data:
                params = event_data['request'].get('parameters', {})
            
            call_sid = params.get('CallSid')
            direction = params.get('Direction', '')
            
            event_type = None
            if 'call.initiated' in event_type_full:
                event_type = 'initiated'
            elif 'call.ringing' in event_type_full:
                event_type = 'ringing'
            elif 'call.answer' in event_type_full:
                event_type = 'answered'
            elif 'call.completed' in event_type_full:
                event_type = 'completed'
            
            call_emit_data = {
                'event_id': event_data.get('id', ''),
                'call_sid': call_sid,
                'timestamp': event_data.get('time') or datetime.now().isoformat(),
                'direction': direction,
                'event_type': event_type,
                'from_number': params.get('From', ''),
                'to_number': params.get('To', ''),
                'call_status': params.get('CallStatus', ''),
            }
            await sio.emit('new_event', call_emit_data)
            print(f"Emitted event to frontend: {call_emit_data['event_type']}")
        
        # storing in database
        success, call = await sync_to_async(store_event_in_database)(event_data)
        
        if success and call:
            print(f"Event stored in database successfully")
        
        return success
    except Exception as e:
        print(f"Error in process_and_emit_event: {e}")
        import traceback
        traceback.print_exc()
        return False


# Socket.IO connection testing (for development purposes - will remove later)
@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    print(f"Client disconnected: {sid}")

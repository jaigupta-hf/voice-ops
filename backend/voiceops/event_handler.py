"""
Event handler for processing Twilio events in real-time.
Sends events to frontend via Socket.IO and stores in database.
"""
import socketio
from datetime import datetime
from asgiref.sync import sync_to_async
from voiceops.models import (
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
        event_type_full = event_data.get('type', '')
        event_id = event_data.get('id', '')
        
        from django.utils.dateparse import parse_datetime
        timestamp_str = event_data.get('time', '')
        timestamp = parse_datetime(timestamp_str)
        
        is_error = 'error-logs.error.logged' in event_type_full
        
        # Get or create call (not for error events)
        call = None
        if not is_error:
            call = get_or_create_call(event_data)
        
        event_type = None
        if 'call.initiated' in event_type_full:
            event_type = 'initiated'
        elif 'call.ringing' in event_type_full:
            event_type = 'ringing'
        elif 'call.answer' in event_type_full:
            event_type = 'answered'
        elif 'call.completed' in event_type_full:
            event_type = 'completed'
        elif is_error:
            event_type = 'error'
        
        # Store based on event type
        if event_type == 'initiated':
            CallInitiatedEvent.objects.create(
                event_id=event_id,
                call_sid=call,
                timestamp=timestamp,
                additional_data=event_data
            )
        elif event_type == 'ringing':
            CallRingingEvent.objects.create(
                event_id=event_id,
                call_sid=call,
                timestamp=timestamp,
                additional_data=event_data
            )
        elif event_type == 'answered':
            CallAnsweredEvent.objects.create(
                event_id=event_id,
                call_sid=call,
                timestamp=timestamp,
                additional_data=event_data
            )
        elif event_type == 'completed':
            CallCompletedEvent.objects.create(
                event_id=event_id,
                call_sid=call,
                timestamp=timestamp,
                additional_data=event_data
            )
        elif event_type == 'error':
            data = event_data.get('data', {})
            error_code = data.get('error_code', '')
            error_message = data.get('level', '')
            correlation_sid = data.get('correlation_sid', '')
            
            # Get or create call for correlation_sid
            error_call = None
            if correlation_sid:
                try:
                    error_call = Call.objects.get(call_sid=correlation_sid)
                    print(f"Found existing call for error event: {correlation_sid}")
                except Call.DoesNotExist:
                    # Create a placeholder Call record for non-existent SIDs
                    error_call = Call.objects.create(
                        call_sid=correlation_sid,
                        direction='unknown',
                        from_number='',
                        to_number='',
                        call_status='',
                        additional_data={'note': 'Created from error event correlation_sid'}
                    )
                    print(f"Created placeholder call for error event: {correlation_sid}")
            else:
                print(f"No correlation_sid in error event")
            
            ErrorEvent.objects.create(
                event_id=event_id,
                resource_sid=error_call,
                timestamp=timestamp,
                error_code=error_code,
                error_message=error_message,
                additional_data=event_data
            )
        else:
            print(f"Unknown event type: {event_type_full}, storing only Call record")
        
        return True, call
    except Exception as e:
        print(f"Error storing event in database: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def process_and_emit_event(event_data):
    """
    Main function to process event: emit to frontend and store in DB.
    """
    try:
        # Check for error event 
        event_type_full = event_data.get('type', '')
        
        if 'error-logs.error.logged' in event_type_full:
            data = event_data.get('data', {})
            error_code = data.get('error_code', '')
            resource_sid = data.get('correlation_sid', '')
            error_message = data.get('level', 'WARNING')
            
            error_emit_data = {
                'event_id': event_data.get('id', ''),
                'resource_sid': resource_sid,
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

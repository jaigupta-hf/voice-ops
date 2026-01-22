"""
API Views for VoiceOps - Optimized for frontend dashboard
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Call, CallInitiatedEvent, CallRingingEvent, CallAnsweredEvent, CallCompletedEvent, ErrorEvent
from .serializers import CallEventSerializer, ErrorEventSerializer


class RecentCallEventsAPIView(APIView):
    """
    API endpoint to get call events.
    Supports 'all' query parameter to fetch all events, otherwise returns 100 most recent.
    """
    
    def get(self, request):
        # Check if 'all' query parameter is present
        fetch_all = request.query_params.get('all', 'false').lower() == 'true'
        
        # Get all event types, with or without limit based on fetch_all
        if fetch_all:
            initiated = CallInitiatedEvent.objects.select_related('call_sid').order_by('-timestamp')
            ringing = CallRingingEvent.objects.select_related('call_sid').order_by('-timestamp')
            answered = CallAnsweredEvent.objects.select_related('call_sid').order_by('-timestamp')
            completed = CallCompletedEvent.objects.select_related('call_sid').order_by('-timestamp')
        else:
            initiated = CallInitiatedEvent.objects.select_related('call_sid').order_by('-timestamp')[:100]
            ringing = CallRingingEvent.objects.select_related('call_sid').order_by('-timestamp')[:100]
            answered = CallAnsweredEvent.objects.select_related('call_sid').order_by('-timestamp')[:100]
            completed = CallCompletedEvent.objects.select_related('call_sid').order_by('-timestamp')[:100]
        
        # Combine all events into a unified list
        all_events = []
        
        for event in initiated:
            all_events.append({
                'event_id': event.event_id,
                'call_sid': event.call_sid.call_sid,
                'timestamp': event.timestamp,
                'direction': event.call_sid.direction,
                'event_type': 'initiated',
                'from_number': event.call_sid.from_number,
                'to_number': event.call_sid.to_number,
                'call_status': event.call_sid.call_status,
            })
        
        for event in ringing:
            all_events.append({
                'event_id': event.event_id,
                'call_sid': event.call_sid.call_sid,
                'timestamp': event.timestamp,
                'direction': event.call_sid.direction,
                'event_type': 'ringing',
                'from_number': event.call_sid.from_number,
                'to_number': event.call_sid.to_number,
                'call_status': event.call_sid.call_status,
            })
        
        for event in answered:
            all_events.append({
                'event_id': event.event_id,
                'call_sid': event.call_sid.call_sid,
                'timestamp': event.timestamp,
                'direction': event.call_sid.direction,
                'event_type': 'answered',
                'from_number': event.call_sid.from_number,
                'to_number': event.call_sid.to_number,
                'call_status': event.call_sid.call_status,
            })
        
        for event in completed:
            all_events.append({
                'event_id': event.event_id,
                'call_sid': event.call_sid.call_sid,
                'timestamp': event.timestamp,
                'direction': event.call_sid.direction,
                'event_type': 'completed',
                'from_number': event.call_sid.from_number,
                'to_number': event.call_sid.to_number,
                'call_status': event.call_sid.call_status,
            })
        
        # Sort all events by timestamp (most recent first)
        all_events.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit to 100 if not fetching all
        if not fetch_all:
            all_events = all_events[:100]
        
        serializer = CallEventSerializer(all_events, many=True)
        return Response(serializer.data)


class RecentErrorEventsAPIView(APIView):
    """
    API endpoint to get error events.
    Supports 'all' query parameter to fetch all events, otherwise returns 100 most recent.
    """
    
    def get(self, request):
        # Check if 'all' query parameter is present
        fetch_all = request.query_params.get('all', 'false').lower() == 'true'
        
        # Get errors with or without limit based on fetch_all
        if fetch_all:
            errors = ErrorEvent.objects.select_related('resource_sid').order_by('-timestamp')
        else:
            errors = ErrorEvent.objects.select_related('resource_sid').order_by('-timestamp')[:100]
        
        serializer = ErrorEventSerializer(errors, many=True)
        return Response(serializer.data)


class CallDetailEventsAPIView(APIView):
    """
    API endpoint to get all events for a specific call_sid.
    """
    
    def get(self, request, call_sid):
        try:
            # Verify the call exists
            call = Call.objects.get(call_sid=call_sid)
        except Call.DoesNotExist:
            return Response({'error': 'Call not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get all event types for this call
        initiated = CallInitiatedEvent.objects.filter(call_sid=call).order_by('timestamp')
        ringing = CallRingingEvent.objects.filter(call_sid=call).order_by('timestamp')
        answered = CallAnsweredEvent.objects.filter(call_sid=call).order_by('timestamp')
        completed = CallCompletedEvent.objects.filter(call_sid=call).order_by('timestamp')
        errors = ErrorEvent.objects.filter(resource_sid=call).order_by('timestamp')
        
        # Combine all events
        all_events = []
        
        for event in initiated:
            all_events.append({
                'event_id': event.event_id,
                'event_type': 'initiated',
                'timestamp': event.timestamp,
            })
        
        for event in ringing:
            all_events.append({
                'event_id': event.event_id,
                'event_type': 'ringing',
                'timestamp': event.timestamp,
            })
        
        for event in answered:
            all_events.append({
                'event_id': event.event_id,
                'event_type': 'answered',
                'timestamp': event.timestamp,
            })
        
        for event in completed:
            all_events.append({
                'event_id': event.event_id,
                'event_type': 'completed',
                'timestamp': event.timestamp,
            })
        
        for event in errors:
            all_events.append({
                'event_id': event.event_id,
                'event_type': 'error',
                'timestamp': event.timestamp,
                'error_code': event.error_code,
                'error_message': event.error_message,
            })
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x['timestamp'])
        
        return Response({
            'call_sid': call.call_sid,
            'direction': call.direction,
            'from_number': call.from_number,
            'to_number': call.to_number,
            'call_status': call.call_status,
            'events': all_events
        })

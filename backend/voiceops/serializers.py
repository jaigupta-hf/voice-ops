"""
Serializers for VoiceOps API
"""
from rest_framework import serializers
from .models import Call, CallInitiatedEvent, CallRingingEvent, CallAnsweredEvent, CallCompletedEvent, ErrorEvent


class CallEventSerializer(serializers.Serializer):
    """Unified serializer for all call events"""
    event_id = serializers.CharField()
    call_sid = serializers.CharField()
    timestamp = serializers.DateTimeField()
    direction = serializers.CharField()
    event_type = serializers.CharField()
    from_number = serializers.CharField()
    to_number = serializers.CharField()
    call_status = serializers.CharField()


class ErrorEventSerializer(serializers.ModelSerializer):
    """Serializer for error events"""
    resource_sid = serializers.SerializerMethodField()
    
    class Meta:
        model = ErrorEvent
        fields = ['event_id', 'resource_sid', 'timestamp', 'error_code', 'error_message']
    
    def get_resource_sid(self, obj):
        return obj.resource_sid.call_sid if obj.resource_sid else None

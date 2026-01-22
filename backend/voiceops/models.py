"""
Django models for Twilio event storage.
"""
from django.db import models


class Call(models.Model):
    """
    Main table to store call information.
    """
    call_sid = models.CharField(max_length=255, primary_key=True, db_index=True)
    account_sid = models.CharField(max_length=255, blank=True, default='', db_index=True)
    direction = models.CharField(max_length=50) 
    from_number = models.CharField(max_length=50, blank=True, default='') 
    to_number = models.CharField(max_length=50, blank=True, default='') 
    call_status = models.CharField(max_length=50, blank=True, default='') 
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Timestamp from first event
    additional_data = models.JSONField(default=dict)  # All remaining data for future use
    
    class Meta:
        db_table = 'calls'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.call_sid


class CallInitiatedEvent(models.Model):
    """
    Store call initiated events.
    """
    event_id = models.CharField(max_length=255, primary_key=True)
    call_sid = models.ForeignKey(Call, on_delete=models.CASCADE, db_column='call_sid')
    timestamp = models.DateTimeField(db_index=True)
    additional_data = models.JSONField(default=dict)  # All remaining data for future use
    
    class Meta:
        db_table = 'call_initiated_events'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.event_id} - {self.call_sid_id}"


class CallRingingEvent(models.Model):
    """
    Store call ringing events.
    """
    event_id = models.CharField(max_length=255, primary_key=True)
    call_sid = models.ForeignKey(Call, on_delete=models.CASCADE, db_column='call_sid')
    timestamp = models.DateTimeField(db_index=True)
    additional_data = models.JSONField(default=dict)  # All remaining data for future use
    
    class Meta:
        db_table = 'call_ringing_events'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.event_id} - {self.call_sid_id}"


class CallAnsweredEvent(models.Model):
    """
    Store call answered events.
    """
    event_id = models.CharField(max_length=255, primary_key=True)
    call_sid = models.ForeignKey(Call, on_delete=models.CASCADE, db_column='call_sid')
    timestamp = models.DateTimeField(db_index=True) 
    additional_data = models.JSONField(default=dict)  # All remaining data for future use
    
    class Meta:
        db_table = 'call_answered_events'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.event_id} - {self.call_sid_id}"


class CallCompletedEvent(models.Model):
    """
    Store call completed events.
    """
    event_id = models.CharField(max_length=255, primary_key=True)
    call_sid = models.ForeignKey(Call, on_delete=models.CASCADE, db_column='call_sid')
    timestamp = models.DateTimeField(db_index=True) 
    additional_data = models.JSONField(default=dict)  # All remaining data for future use
    
    class Meta:
        db_table = 'call_completed_events'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.event_id} - {self.call_sid_id}"


class ErrorEvent(models.Model):
    """
    Store error events.
    """
    event_id = models.CharField(max_length=255, primary_key=True)
    resource_sid = models.ForeignKey(Call, on_delete=models.CASCADE, null=True, blank=True, db_column='call_sid')
    timestamp = models.DateTimeField(db_index=True)
    error_code = models.CharField(max_length=100, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    additional_data = models.JSONField(default=dict)  # All remaining data for future use
    
    class Meta:
        db_table = 'error_events'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.event_id} - Error: {self.error_code}"

from django.contrib import admin
from django.utils.html import format_html
import json
from .models import (
    Call, CallInitiatedEvent, CallRingingEvent,
    CallAnsweredEvent, CallCompletedEvent, ErrorEvent
)


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ('call_sid', 'direction', 'from_number', 'to_number', 'call_status', 'created_at')
    search_fields = ('call_sid', 'from_number', 'to_number')
    list_filter = ('direction', 'call_status', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('call_sid', 'direction', 'from_number', 'to_number', 'call_status', 'created_at', 'formatted_additional_data')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('call_sid', 'direction', 'from_number', 'to_number', 'call_status', 'created_at')
        }),
        ('Additional Data', {
            'fields': ('formatted_additional_data',),
            'classes': ('collapse',)
        }),
    )
    
    def formatted_additional_data(self, obj):
        """Display additional_data as formatted JSON."""
        return format_html('<pre>{}</pre>', json.dumps(obj.additional_data, indent=2))
    formatted_additional_data.short_description = 'Additional Data (JSON)'


@admin.register(CallInitiatedEvent)
class CallInitiatedEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'get_call_sid', 'timestamp')
    search_fields = ('event_id', 'call_sid__call_sid')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)
    readonly_fields = ('event_id', 'call_sid', 'timestamp', 'formatted_additional_data')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('event_id', 'call_sid', 'timestamp')
        }),
        ('Additional Data', {
            'fields': ('formatted_additional_data',),
            'classes': ('collapse',)
        }),
    )
    
    def get_call_sid(self, obj):
        """Display only the call_sid without direction."""
        return obj.call_sid.call_sid if obj.call_sid else None
    get_call_sid.short_description = 'Call SID'
    
    def formatted_additional_data(self, obj):
        """Display additional_data as formatted JSON."""
        return format_html('<pre>{}</pre>', json.dumps(obj.additional_data, indent=2))
    formatted_additional_data.short_description = 'Additional Data (JSON)'


@admin.register(CallRingingEvent)
class CallRingingEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'get_call_sid', 'timestamp')
    search_fields = ('event_id', 'call_sid__call_sid')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)
    readonly_fields = ('event_id', 'call_sid', 'timestamp', 'formatted_additional_data')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('event_id', 'call_sid', 'timestamp')
        }),
        ('Additional Data', {
            'fields': ('formatted_additional_data',),
            'classes': ('collapse',)
        }),
    )
    
    def get_call_sid(self, obj):
        """Display only the call_sid without direction."""
        return obj.call_sid.call_sid if obj.call_sid else None
    get_call_sid.short_description = 'Call SID'
    
    def formatted_additional_data(self, obj):
        """Display additional_data as formatted JSON."""
        return format_html('<pre>{}</pre>', json.dumps(obj.additional_data, indent=2))
    formatted_additional_data.short_description = 'Additional Data (JSON)'


@admin.register(CallAnsweredEvent)
class CallAnsweredEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'get_call_sid', 'timestamp')
    search_fields = ('event_id', 'call_sid__call_sid')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)
    readonly_fields = ('event_id', 'call_sid', 'timestamp', 'formatted_additional_data')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('event_id', 'call_sid', 'timestamp')
        }),
        ('Additional Data', {
            'fields': ('formatted_additional_data',),
            'classes': ('collapse',)
        }),
    )
    
    def get_call_sid(self, obj):
        """Display only the call_sid without direction."""
        return obj.call_sid.call_sid if obj.call_sid else None
    get_call_sid.short_description = 'Call SID'
    
    def formatted_additional_data(self, obj):
        """Display additional_data as formatted JSON."""
        return format_html('<pre>{}</pre>', json.dumps(obj.additional_data, indent=2))
    formatted_additional_data.short_description = 'Additional Data (JSON)'


@admin.register(CallCompletedEvent)
class CallCompletedEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'get_call_sid', 'timestamp')
    search_fields = ('event_id', 'call_sid__call_sid')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)
    readonly_fields = ('event_id', 'call_sid', 'timestamp', 'formatted_additional_data')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('event_id', 'call_sid', 'timestamp')
        }),
        ('Additional Data', {
            'fields': ('formatted_additional_data',),
            'classes': ('collapse',)
        }),
    )
    
    def get_call_sid(self, obj):
        """Display only the call_sid without direction."""
        return obj.call_sid.call_sid if obj.call_sid else None
    get_call_sid.short_description = 'Call SID'
    
    def formatted_additional_data(self, obj):
        """Display additional_data as formatted JSON."""
        return format_html('<pre>{}</pre>', json.dumps(obj.additional_data, indent=2))
    formatted_additional_data.short_description = 'Additional Data (JSON)'


@admin.register(ErrorEvent)
class ErrorEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'get_resource_sid', 'timestamp', 'error_code')
    search_fields = ('event_id', 'error_code', 'error_message')
    list_filter = ('timestamp', 'error_code')
    ordering = ('-timestamp',)
    readonly_fields = ('event_id', 'resource_sid', 'timestamp', 'error_code', 'error_message', 'formatted_additional_data')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('event_id', 'resource_sid', 'timestamp')
        }),
        ('Error Details', {
            'fields': ('error_code', 'error_message')
        }),
        ('Additional Data', {
            'fields': ('formatted_additional_data',),
            'classes': ('collapse',)
        }),
    )
    
    def get_resource_sid(self, obj):
        """Display only the resource_sid without direction."""
        return obj.resource_sid.call_sid if obj.resource_sid else None
    get_resource_sid.short_description = 'Resource SID'
    
    def formatted_additional_data(self, obj):
        """Display additional_data as formatted JSON."""
        return format_html('<pre>{}</pre>', json.dumps(obj.additional_data, indent=2))
    formatted_additional_data.short_description = 'Additional Data (JSON)'

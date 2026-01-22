"""
Slack notification system for error event monitoring.
Sends real-time alerts to Slack when error events occur.
"""
import os
import requests
from datetime import datetime, timezone, timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')


def send_slack_notification(error_data):
    """
    Args:
        error_data: Dictionary containing error event information
            - event_id: Unique event identifier
            - error_code: Error code from Twilio
            - error_message: Error message/level
            - resource_sid: Call SID or correlation ID
            - timestamp: When the error occurred
    """
    
    try:
        timestamp = error_data.get('timestamp', datetime.now().isoformat())
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            formatted_time = timestamp
        
        message_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Voice Ops Error Alert",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Error Code:*\n`{error_data.get('error_code', 'N/A')}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Level:*\n{error_data.get('error_message', 'WARNING')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Resource SID:*\n`{error_data.get('resource_sid', 'N/A')}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Time:*\n{formatted_time}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Event ID:* `{error_data.get('event_id', 'N/A')}`"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "channel": CHANNEL_ID,
            "blocks": message_blocks,
            "text": f"Error Alert: {error_data.get('error_code', 'Unknown')} - {error_data.get('resource_sid', 'N/A')}"  # Fallback text
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        if response_data.get('ok'):
            print(f"✓ Slack notification sent successfully for error: {error_data.get('error_code')}")
            return True
        else:
            print(f"✗ Failed to send Slack notification: {response_data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Exception while sending Slack notification: {e}")
        import traceback
        traceback.print_exc()
        return False


def is_business_hours():
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    current_hour = current_time.hour
    
    # Business hours: 9 AM to 5 PM IST (9-17)
    return 9 <= current_hour < 17


def send_performance_alert(alert_type, details):
    """
    Send a Slack notification for performance issues.
    
    Args:
        alert_type: Type of alert ('slow_processing' or 'no_events')
        details: Dictionary containing alert details
            - processing_time: Time taken to process event (for slow_processing)
            - last_event_time: Time of last event (for no_events)
            - idle_duration: Duration without events in minutes (for no_events)
            - event_id: Event identifier (optional)
    """
    
    if not is_business_hours():
        print("Outside business hours. Skipping performance alert.")
        return False
    
    try:
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S IST')
        
        if alert_type == 'slow_processing':
            # Alert for slow event processing (>2 seconds)
            processing_time = details.get('processing_time', 0)
            event_id = details.get('event_id', 'N/A')
            
            message_blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Slow Event Processing Alert",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Processing Time:*\n`{processing_time:.2f} seconds`"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Threshold:*\n`2.0 seconds`"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Event ID:*\n`{event_id}`"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Time:*\n{current_time}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Event processing is taking longer than expected. Please investigate system performance."
                    }
                }
            ]
            fallback_text = f"Slow Processing Alert: Event took {processing_time:.2f}s to process"
            
        elif alert_type == 'no_events':
            # Alert for no events received (>15 minutes)
            idle_duration = details.get('idle_duration', 0)
            last_event_time = details.get('last_event_time', 'N/A')
            
            message_blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "No Events Alert",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Idle Duration:*\n`{idle_duration:.1f} minutes`"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Threshold:*\n`15 minutes`"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Last Event:*\n{last_event_time}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Time:*\n{current_time}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "No events received for over 15 minutes during business hours. Please check event stream connectivity."
                    }
                }
            ]
            fallback_text = f"No Events Alert: {idle_duration:.1f} minutes without events"
            
        else:
            print(f"Unknown alert type: {alert_type}")
            return False
        
        # Add divider at the end
        message_blocks.append({"type": "divider"})
        
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "channel": CHANNEL_ID,
            "blocks": message_blocks,
            "text": fallback_text
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        if response_data.get('ok'):
            print(f"✓ Performance alert sent successfully: {alert_type}")
            return True
        else:
            print(f"✗ Failed to send performance alert: {response_data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Exception while sending performance alert: {e}")
        import traceback
        traceback.print_exc()
        return False
"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from .api_views import RecentCallEventsAPIView, RecentErrorEventsAPIView, CallDetailEventsAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhooks/twilio-events', views.twilio_events_webhook, name='twilio_events_webhook'),
    path('api/call-events/', RecentCallEventsAPIView.as_view(), name='recent-call-events'),
    path('api/error-events/', RecentErrorEventsAPIView.as_view(), name='recent-error-events'),
    path('api/call-events/<str:call_sid>/', CallDetailEventsAPIView.as_view(), name='call-detail-events'),
    path('api/', include('events.urls')),  # for testing purposes
]

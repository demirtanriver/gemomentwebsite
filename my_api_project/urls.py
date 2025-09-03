"""
URL configuration for my_api_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from rest_framework import routers
from core.views import (
    OrganisersListView, StoriesListView, SendersListView, StorySendersListView,
    StoryViewSet
)

# Use a router to automatically generate URL patterns for ViewSets
router = routers.DefaultRouter()
router.register(r'stories', StoryViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    # A single API entry point for all of our endpoints
    path('api/v1/', include(router.urls)),
    path('api/v1/organisers/', OrganisersListView.as_view(), name='organiser-list'),
    path('api/v1/all-stories/', StoriesListView.as_view(), name='story-list'),
    path('api/v1/senders/', SendersListView.as_view(), name='sender-list'),
    path('api/v1/story-senders/', StorySendersListView.as_view(), name='story-sender-list'),
]



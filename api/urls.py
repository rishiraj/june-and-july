# api/urls.py
from django.urls import path
from .views import ProfileListView, SwipeView

urlpatterns = [
    path('profiles/', ProfileListView.as_view(), name='profile-list'),
    path('swipe/', SwipeView.as_view(), name='swipe'),
    # Add auth, match list, and chat endpoints here
]

# backend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

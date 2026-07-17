from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import ContactView, health_check, metrics_view

router = DefaultRouter()
router.register(r'contact', ContactView, basename='contact')

urlpatterns = [
    path('', include(router.urls)),
    path('health/', health_check, name='health'),
    path('metrics/', metrics_view, name='metrics'),
]
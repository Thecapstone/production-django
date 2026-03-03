from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from core.apps.projects.views import ProjectViewSet

PREFIX = 'projects'


router = DefaultRouter()
router.register('projects', ProjectViewSet)
urlpatterns = router.urls

app_name = f"{PREFIX}"
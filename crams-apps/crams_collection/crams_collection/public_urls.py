"""crams_collection URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include

from rest_framework import routers

from crams_collection.views.lookup_api import grant_types
from crams_collection.viewsets.project_exists import ProjectExistsViewset

router = routers.SimpleRouter()

router.register(r'exists', ProjectExistsViewset, basename='project')

urlpatterns = [
    path('', include(router.urls)),
    # path('admin/', admin.site.urls),
    path('grant_types', grant_types, name='grant_types'),
]

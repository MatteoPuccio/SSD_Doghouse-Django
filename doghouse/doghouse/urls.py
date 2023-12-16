"""
URL configuration for doghouse project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from doghouse.views import RoleView
from dogs.views import FavouriteDogsView

API_TITLE = "Doghouse API"
API_DESCRIPTION = "A Web API for viewing and adopting different dogs."

urlpatterns = [
    path('admin-aLECHREoNfiG/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('docs/', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)),
    path('schema/', get_schema_view(title=API_TITLE)),
    path('api/v1/dogs/', include('dogs.urls')),
    path('api/v1/auth/', include('dj_rest_auth.urls')),
    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/v1/role/', RoleView.as_view(), name='get-role'),
    path('api/v1/favourite-dogs/', view=FavouriteDogsView.as_view(), name='favourite-dogs')
]

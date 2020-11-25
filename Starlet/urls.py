"""Starlet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Starlet API",
      default_version='v1',
      description="This is the documentation for the Starlet API powered by Django and Django Rest Framework",
      # terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="illyaredkolis@gmail.com"),
      license=openapi.License(name="GPL-3.0 License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = i18n_patterns(
    re_path(r'^doc(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('doc/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('api/movie/', include('films.urls')),
    path('rosetta/', include('rosetta.urls')),
)

if not settings.IS_DEPLOYED:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

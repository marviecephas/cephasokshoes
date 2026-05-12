"""
URL configuration for backend project.

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
from django.urls import path
from shop.views import whatsapp_webhook, manual_sale_view
from django.conf.urls import handler404
from django.conf import settings
from django.conf.urls.static import static

# Point to your custom view
handler404 = 'shop.views.custom_404'

urlpatterns = [
    path('admin/manual-sale/', manual_sale_view, name='manual-sale-form'),
    path('admin/', admin.site.urls),
    path('webhook/', whatsapp_webhook),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
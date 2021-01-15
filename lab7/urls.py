"""lab7 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.urls import include, re_path, path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', RedirectView.as_view(url='/login/')),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    re_path(r'^logout/$', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    re_path(r'^', include('trazabilidad.urls', namespace='trazabilidad')),
    path('muestras/covid19/', include('covid19.urls', namespace='covid19')),
    re_path(r'^muestras/alimentos/', include('alimentos.urls', namespace='alimentos')),
    re_path(r'^muestras/bebidas_alcoholicas/', include('bebidas_alcoholicas.urls', namespace='bebidas_alcoholicas')),
    re_path(r'^equipos/', include('equipos.urls', namespace='equipos')),
    re_path(r'^administracion/', include('administracion.urls', namespace='administracion')),
    re_path(r'^admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
        path('silk/', include('silk.urls', namespace='silk')),
    ] + urlpatterns

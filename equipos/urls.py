from django.urls import re_path
from . import views

__author__ = 'tania'

app_name = 'equipos'
urlpatterns = [
    re_path(r'^control_temperatura/$', views.control_temperatura, name='control_temperatura'),
    re_path(r'^control_temperatura/(?P<equipo>\d+)/nueva$', views.registro_temperatura, name='registro_temperatura_equipo'),
    re_path(r'^(?P<pk>\d+)/', views.DetalleEquipoView.as_view(), name='detalle_equipo_json'),
    re_path(r'^areas/(?P<pk>\d+)/equipo/', views.ListaEquiposAreaView.as_view(), name='lista_equipos_area_json'),
]

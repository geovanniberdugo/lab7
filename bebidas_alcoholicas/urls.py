from django.urls import re_path, path
from . import views

app_name = 'bebidas_alcoholicas'
urlpatterns = [
    path('nueva/', views.nueva_muestra, name='nueva_muestra'),
    path('<int:id>/', views.actualizar_muestra, name='actualizar_muestra'),
    path('<int:id>/estado/', views.estado_muestra, name='estado_muestra'),
    path('<int:id>/radicado/', views.radicado_muestra, name='radicado_muestra'),
    path('<int:id>/decreto/', views.decreto_muestras, name='decreto_muestras'),
    path('api/<int:pk>/productos/', views.ListaProductosGrupoView.as_view(), name='lista_productos_json'),
]

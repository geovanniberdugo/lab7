from django.urls import re_path, path
from . import views

app_name = 'alimentos'
urlpatterns = [
    path('nueva/', views.nueva_muestra, name='nueva_muestra'),
    path('<int:id>/', views.actualizar_muestra, name='actualizar_muestra'),
    path('<int:id>/estado/', views.estado_muestra, name='estado_muestra'),
    path('<int:id>/radicado/', views.radicado_muestra, name='radicado_muestra'),
    path('<int:id>/decreto/', views.decreto_muestras, name='decreto_muestras'),

    re_path(r'^grupo/(?P<pk>\d+)/tipos/$', views.ListaTiposAlimentoGrupoView.as_view(), name='lista_tipos_grupo_json'),

    re_path(r'^api/(?P<pk>\d+)/categorias/$', views.ListaCategoriasGrupoView.as_view(), name='lista_categorias_json'),
    re_path(r'^api/(?P<pk>\d+)/sub-categorias/$', views.ListaSubCategoriasCategoriaView.as_view(), name='lista_sub_categorias_json'),
]

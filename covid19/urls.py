from django.urls import re_path, path
from covid19 import views, api_views

__author__ = 'Geovanni'

app_name = 'covid19'
urlpatterns = [
    path('nueva/348/', views.nueva_muestra_348, name='nueva_muestra_348'),
    path('nueva/346/', views.nueva_muestra_346, name='nueva_muestra_346'),
    path('<int:id>/', views.actualizar_muestra, name='actualizar_muestra'),
    path('346/<int:id>/', views.actualizar_muestra_346, name='actualizar_muestra_346'),
    path('348/<int:id>/', views.actualizar_muestra_348, name='actualizar_muestra_348'),
    path('<int:id>/estado/', views.estado_muestra, name='estado_muestra'),
    path('<int:id>/radicado/', views.radicado_muestra, name='radicado_muestra'),
    path('consulta-resultados/', views.ConsultaResultadosView.as_view(), name='consulta_resultados'),
    path('impresion-lote-fichas/', views.ImpresionLoteFichasView.as_view(), name='impresion_lote_fichas'),
    path('exportacion-excel-ficha/', views.ExportacionExcelFichaView.as_view(), name='exportacion_excel_ficha'),
    path('envio-masivo-resultados/', views.EnvioMasivoResultadosMailView.as_view(), name='envio_masivo_resultados_mail'),
    
    path('ficha/<int:id>/', views.ficha_view, name='ficha'),
    
    path('upgd/', api_views.UpgdListView.as_view(), name='upgd_json'),
    path('cie10/', api_views.Cie10ListView.as_view(), name='cie10_json'),
    path('pacientes/', api_views.DetalleInfoPacienteView.as_view(), name='pacientes_json'),
    path('api/send-results-email/', api_views.SendResultsEmailView.as_view(), name='send_results_email_api'),
]

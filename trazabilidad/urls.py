from django.urls import re_path, path
from . import api_views
from . import views

__author__ = 'tania'

app_name = 'trazabilidad'
urlpatterns = [
    path('home/', views.home, name='home'),
    path('ingresos/', views.ingresos_recepcionados, name='ingresos'),
    path('ingresos/<int:id>/codigos/', views.codigos_muestra_ingreso, name='codigos_muestras_ingreso'),
    path('ingresos/<int:id>/comentario/', views.comentario_recepcionista_view, name='comentario_recepcionista'),

    path('analisis/', views.analisis, name='analisis'),
    path('ingresos/<int:id>/', views.detalle_ingreso, name='detalle_ingreso'),
    path('ingresos/<int:id>/pruebas/', views.pruebas_analizar, name='pruebas_analizar'),
    path('muestras/pruebas/<int:id>/', views.actualizar_estado, name='actualizar_estado'),
    path('ingreso/<int:id>/estado/', views.ingresar_estado_analista, name='ingresar_estado_analista'),
    path('analisis/actualizar/muestra/<int:id_muestra>/', views.actualizar_pruebas_muestra, name='actualizar_pruebas_muestra'),

    path('muestras/clinica/nueva/', views.nueva_muestra_clinica, name='nueva_muestra_clinica'),
    path('muestras/clinica/<int:id>/', views.actualizar_muestra_clinica, name='actualizar_muestra_clinica'),
    path('muestras/clinica/<int:id>/estado/', views.estado_muestra_clinica, name='estado_muestra_clinica'),
    path('muestras/clinica/<int:id>/radicado/', views.radicado_muestra_clinica, name='radicado_muestra_clinica'),

    re_path(r'^muestras/clinica/municipios/(?P<id_municipio>[0-9]+)/hermanos/$', views.get_municipios_hermanos_json,
        name='municipios_hermanos'),

    path('muestras/agua/nueva/', views.nueva_muestra_agua, name='nueva_muestra_agua'),
    path('muestras/agua/<int:id>/', views.actualizar_muestra_agua, name='actualizar_muestra_agua'),
    path('muestras/agua/<int:id>/estado/', views.estado_muestra_agua, name='estado_muestra_agua'),
    path('muestras/agua/<int:id>/radicado/', views.radicado_muestra_agua, name='radicado_muestra_agua'),

    path('muestras/entomologia/nueva/', views.nueva_muestra_entomologia, name='nueva_muestra_entomologia'),
    path('muestras/entomologia/<int:id>/', views.actualizar_muestra_entomologia, name='actualizar_muestra_entomologia'),
    path('muestras/entomologia/<int:id>/estado/', views.estado_muestra_entomologia, name='estado_muestra_entomologia'),
    path('muestras/entomologia/<int:id>/radicado/', views.radicado_muestra_entomologia, name='radicado_muestra_entomologia'),

    path('muestras/citohistopatologia/nueva/', views.nueva_muestra_citohistopatologia, name='nueva_muestra_citohistopatologia'),
    path('muestras/citohistopatologia/<int:id>/', views.actualizar_muestra_citohistopatologia, name='actualizar_muestra_citohistopatologia'),
    path('muestras/citohistopatologia/<int:id>/estado/', views.estado_muestra_citohistopatologia, name='estado_muestra_citohistopatologia'),
    path('muestras/citohistopatologia/<int:id>/radicado/', views.radicado_muestra_citohistopatologia, name='radicado_muestra_citohistopatologia'),

    path('muestras/banco_sangre/nueva/', views.nueva_muestra_banco_sangre, name='nueva_muestra_banco_sangre'),
    path('muestras/banco_sangre/<int:id>/', views.actualizar_muestra_banco_sangre, name='actualizar_muestra_banco_sangre'),
    path('muestras/banco_sangre/<int:id>/estado/', views.estado_muestra_banco_sangre, name='estado_muestra_banco_sangre'),
    path('muestras/banco_sangre/<int:id>/radicado/', views.radicado_muestra_banco_sangre, name='radicado_muestra_banco_sangre'),

    path('muestras/eedd/nueva/', views.nueva_muestra_eedd, name='nueva_muestra_eedd'),
    path('muestras/eedd/<int:id>/', views.actualizar_muestra_eedd, name='actualizar_muestra_eedd'),
    path('muestras/eedd/<int:id>/estado/', views.estado_muestra_eedd, name='estado_muestra_eedd'),
    path('muestras/eedd/<int:id>/radicado/', views.radicado_muestra_eedd, name='radicado_muestra_eedd'),

    path('muestras/eeid/nueva/', views.nueva_muestra_eeid, name='nueva_muestra_eeid'),
    path('muestras/eeid/<int:id>/', views.actualizar_muestra_eeid, name='actualizar_muestra_eeid'),
    path('muestras/eeid/<int:id>/estado/', views.estado_muestra_eeid, name='estado_muestra_eeid'),
    path('muestras/eeid/<int:id>/radicado/', views.radicado_muestra_eeid, name='radicado_muestra_eeid'),

    path('informes/nuevo/<int:id_recepcion>/', views.informe_nuevo, name='informe_nuevo'),
    path('informes/documento/<int:id_recepcion>/', views.informe_documento, name='informe_documento'),
    path('informes/aprobacion/', views.AprobacionInformeResultadosView.as_view(), name='aprobacion_informe'),
    path('informes/documento_parcial/<int:id_muestra>/<int:id_prueba>/', views.informe_documento_prueba, name='informe_documento_prueba'),
    path('api/informes/aprobar/', api_views.AprobarInformeResultadosAPIView.as_view(),name='aprobar_informes_api'),

    path('reportes/tipo_resultado/', views.tipo_resultado, name='tipo_resultado'),
    path('reportes/motivo_rechazo/', views.motivo_rechazo, name='motivo_rechazo'),
    path('reportes/muestras_rechazadas/', views.muestras_rechazadas, name='muestras_rechazadas'),
    path('reportes/productividad_recepcion/', views.productividad_recepcion, name='productividad_recepcion'),
    path('reportes/solicitudes_recepcionadas/', views.solicitudes_recepcionadas, name='solicitudes_recepcionadas'),
    path('reportes/cumplimiento_productividad/', views.cumplimiento_productividad, name='cumplimiento_productividad'),
    path('reportes/pendiente_aceptacion/', views.pendiente_aceptacion, name='pendiente_aceptacion'),
    path('reportes/informes_resultados/', views.informes_resultados, name='informes_resultados'),
    path('reportes/ingreso_parcial/', views.ingreso_parcial, name='ingreso_parcial'),
    path('reportes/produccion_area/', views.produccion_area, name='produccion_area'),
    path('reportes/multiconsulta/', views.multiconsulta, name='multiconsulta'),

    path('buscar_radicado/', views.buscar_radicado, name='buscar_radicado'),
    re_path(r'^devolver_ingreso/(?P<id>[0-9]+)/$', views.devolver_ingreso, name='devolver_ingreso'),
    re_path(r'^agregar_eliminar_prueba/(?P<id>[0-9]+)/$', views.agregar_quitar_pruebas, name='agregar_eliminar_pruebas'),

    # Json urls
    re_path(r'^pacientes/(?P<id>\d+)$', views.DetallePacienteView.as_view(), name='detalle_paciente_json'),
    re_path(r'^areas/(?P<pk>\d+)/pruebas/$', views.ListaPruebasAreaView.as_view(), name='lista_pruebas_area_json'),
    re_path(r'^codigos_puntos/(?P<pk>\d+)', views.DetalleCodigoPuntoView.as_view(), name='detalle_codigo_punto_json'),
    re_path(r'^poblados/(?P<pk>\d+)/epsa/', views.PobladoDetalleEpsaView.as_view(), name='poblado_detalle_epsa_json'),
    re_path(r'^programas/(?P<pk>\d+)/pruebas/$', views.ListaPruebasProgramaView.as_view(), name='lista_pruebas_programa_json'),
    re_path(r'^municipios/(?P<pk>\d+)/poblados/$', views.ListaPobladosMunicipioView.as_view(), name='lista_poblados_municipio_json'),
    re_path(r'^poblados/(?P<pk>\d+)/codigos_puntos/', views.ListaCodigosPuntoPobladoView.as_view(), name='lista_codigos_punto_poblados_json'),
    path('departamentos/<int:pk>/municipios/', views.ListaMunicipiosDepartamentoView.as_view(), name='lista_municipos_departamento_json'),
    re_path(r'^areas/(?P<pk>\d+)/programas/$', views.ListaProgramaAreasView.as_view(), name='lista_areas_programas_json'),

    re_path(r'^areas/control_temperatura/$', views.control_temperatura_area, name='control_temperatura_area'),
    re_path(r'^areas/(?P<id_area>\d+)/registro_temperatura/$', views.registro_temperatura_area, name='registro_temperatura_area'),
    re_path(r'^areas/(?P<pk>\d+)/api/detalle/$', views.DetalleAreaView.as_view(), name='detalle_area_json'),

    path('ingresos/en-curso/', api_views.IngresosEnCursoAPIView.as_view(), name='ingresos-en-curso-api'),
    path('ingresos/pendientes/', api_views.IngresosPendientesAPIView.as_view(), name='ingresos-pendientes-api'),
    path('ingresos/resultados/', api_views.IngresosConResultadoAPIView.as_view(), name='ingresos-con-resultados-api'),
    path('ingresos-recepcionados/en-curso/', api_views.IngresosRecepcionadosEnCursoAPIView.as_view(), name='ingresos-recepcionados-en-curso-api'),
    path('ingresos-recepcionados/parciales/', api_views.IngresosRecepcionadosParcialesAPIView.as_view(), name='ingresos-recepcionados-parciales-api'),
    path('ingresos-recepcionados/resultados/', api_views.IngresosRecepcionadosResultadoAPIView.as_view(), name='ingresos-recepcionados-resultados-api'),
    path('ingresos-recepcionados/rechazados-analista/', api_views.IngresosRecepcionadosRechazadosAnalistaAPIView.as_view(), name='ingresos-recepcionados-rechazados-analista-api'),
    path('ingresos-recepcionados/rechazados-recepcion/', api_views.IngresosRecepcionadosRechazadosRecepcionAPIView.as_view(), name='ingresos-recepcionados-rechazados-recepcion-api'),
]

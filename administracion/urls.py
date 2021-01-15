from django.urls import re_path, path
from . import views

__author__ = 'tania'

app_name = 'administracion'
urlpatterns = [
    path('pruebas/', views.ListaPruebasView.as_view(), name='lista_pruebas'),
    path('pruebas/nueva/', views.CrearPruebaView.as_view(), name='nueva_prueba'),
    path('pruebas/<int:pk>/', views.ActualizarPruebaView.as_view(), name='actualizar_prueba'),

    re_path(r'^metodos/$', views.ListaMetodosView.as_view(), name='lista_metodos'),
    re_path(r'^metodos/nuevo$', views.CrearMetodoView.as_view(), name='nuevo_metodo'),
    re_path(r'^metodos/(?P<pk>\d+)/$', views.ActualizarMetodoView.as_view(), name='actualizar_metodo'),

    re_path(r'^motivos_rechazo/$', views.ListaMotivoRechazosView.as_view(), name='lista_motivo_rechazos'),
    re_path(r'^motivos_rechazo/nuevo$', views.CrearMotivoRechazoView.as_view(), name='nuevo_motivo_rechazo'),
    re_path(r'^motivos_rechazo/(?P<pk>\d+)/$',
        views.ActualizarMotivoRechazoView.as_view(), name='actualizar_motivo_rechazo'),

    path('departamentos/', views.ListaDepartamentosView.as_view(), name='lista_departamentos'),
    path('departamentos/nuevo/', views.CrearDepartamentoView.as_view(), name='nuevo_departamento'),
    path('departamentos/<int:pk>/', views.ActualizarDepartamentoView.as_view(), name='actualizar_departamento'),

    path('municipios/', views.ListaMunicipiosView.as_view(), name='lista_municipios'),
    path('municipios/nuevo/', views.CrearMunicipioView.as_view(), name='nuevo_municipio'),
    path('municipios/<int:pk>/', views.ActualizarMunicipioView.as_view(), name='actualizar_municipio'),

    re_path(r'^poblados/$', views.ListaPobladosView.as_view(), name='lista_poblados'),
    re_path(r'^poblados/nuevo$', views.CrearPobladoView.as_view(), name='nuevo_poblado'),
    re_path(r'^poblados/(?P<pk>\d+)/$', views.ActualizarPobladoView.as_view(), name='actualizar_poblado'),

    re_path(r'^motivo_analisis/$', views.ListaMotivoAnalisisView.as_view(), name='lista_motivo_analisis'),
    re_path(r'^motivo_analisis/nuevo$', views.CrearMotivoAnalisisView.as_view(), name='nuevo_motivo_analisis'),
    re_path(r'^motivo_analisis/(?P<pk>\d+)/$', views.ActualizarMotivoAnalisisView.as_view(),
        name='actualizar_motivo_analisis'),

    re_path(r'^objeto_general_prueba/$', views.ListaObjetoPruebasView.as_view(), name='lista_objeto_pruebas'),
    re_path(r'^objeto_general_prueba/nuevo$', views.CrearObjetoPruebaView.as_view(), name='nuevo_objeto_general_prueba'),
    re_path(r'^objeto_general_prueba/(?P<pk>\d+)/$', views.ActualizarObjetoPruebaView.as_view(),
        name='actualizar_objeto_general_prueba'),

    re_path(r'^resultado_pruebas/$', views.ListaResultadoPruebasView.as_view(), name='lista_resultado_pruebas'),
    re_path(r'^resultado_pruebas/nuevo$', views.CrearResultadoPruebaView.as_view(), name='nuevo_resultado_prueba'),
    re_path(r'^resultado_pruebas/(?P<pk>\d+)/$',
        views.ActualizarResultadoPruebaView.as_view(), name='actualizar_resultado_prueba'),

    re_path(r'^tipo_muestra/$', views.ListaTipoMuestrasView.as_view(), name='lista_tipo_muestras'),
    re_path(r'^tipo_muestra/nuevo$', views.CrearTipoMuestraView.as_view(), name='nuevo_tipo_muestra'),
    re_path(r'^tipo_muestra/(?P<pk>\d+)/$', views.ActualizarTipoMuestraView.as_view(), name='actualizar_tipo_muestra'),

    re_path(r'^epsa/$', views.ListaEpsasView.as_view(), name='lista_epsas'),
    re_path(r'^epsa/nuevo$', views.CrearEpsaView.as_view(), name='nuevo_epsa'),
    re_path(r'^epsa/(?P<pk>\d+)/$', views.ActualizarEpsaView.as_view(), name='actualizar_epsa'),

    re_path(r'^categoria_agua/$', views.ListaCategoriaAguasView.as_view(), name='lista_categoria_aguas'),
    re_path(r'^categoria_agua/nuevo$', views.CrearCategoriaAguaView.as_view(), name='nuevo_categoria_agua'),
    re_path(r'^categoria_agua/(?P<pk>\d+)/$', views.ActualizarCategoriaAguaView.as_view(),
        name='actualizar_categoria_agua'),

    re_path(r'^tipo_agua/$', views.ListaTipoAguasView.as_view(), name='lista_tipo_aguas'),
    re_path(r'^tipo_agua/nuevo$', views.CrearTipoAguaView.as_view(), name='nuevo_tipo_agua'),
    re_path(r'^tipo_agua/(?P<pk>\d+)/$', views.ActualizarTipoAguaView.as_view(), name='actualizar_tipo_agua'),

    re_path(r'^temperatura/$', views.ListaTemperaturasView.as_view(), name='lista_temperaturas'),
    re_path(r'^temperatura/nuevo$', views.CrearTemperaturaView.as_view(), name='nuevo_temperatura'),
    re_path(r'^temperatura/(?P<pk>\d+)/$', views.ActualizarTemperaturaView.as_view(), name='actualizar_temperatura'),

    re_path(r'^solicitante/$', views.ListaSolicitantesView.as_view(), name='lista_solicitantes'),
    re_path(r'^solicitante/nuevo$', views.CrearSolicitanteView.as_view(), name='nuevo_solicitante'),
    re_path(r'^solicitante/(?P<pk>\d+)/$', views.ActualizarSolicitanteView.as_view(), name='actualizar_solicitante'),

    re_path(r'^descripcion_punto/$', views.ListaDescripcionPuntosView.as_view(), name='lista_descripcion_puntos'),
    re_path(r'^descripcion_punto/nuevo$', views.CrearDescripcionPuntoView.as_view(), name='nuevo_descripcion_punto'),
    re_path(r'^descripcion_punto/(?P<pk>\d+)/$', views.ActualizarDescripcionPuntoView.as_view(),
        name='actualizar_descripcion_punto'),

    re_path(r'^fuente_abastecimiento/$', views.ListaFuenteAbastecimientosView.as_view(),
        name='lista_fuente_abastecimientos'),
    re_path(r'^fuente_abastecimiento/nuevo$', views.CrearFuenteAbastecimientoView.as_view(),
        name='nuevo_fuente_abastecimiento'),
    re_path(r'^fuente_abastecimiento/(?P<pk>\d+)/$', views.ActualizarFuenteAbastecimientoView.as_view(),
        name='actualizar_fuente_abastecimiento'),

    re_path(r'^lugar_punto/$', views.ListaLugarPuntosView.as_view(), name='lista_lugar_puntos'),
    re_path(r'^lugar_punto/nuevo$', views.CrearLugarPuntoView.as_view(), name='nuevo_lugar_punto'),
    re_path(r'^lugar_punto/(?P<pk>\d+)/$', views.ActualizarLugarPuntoView.as_view(), name='actualizar_lugar_punto'),

    re_path(r'^codigo_punto/$', views.ListaCodigoPuntosView.as_view(), name='lista_codigo_puntos'),
    re_path(r'^codigo_punto/nuevo$', views.CrearCodigoPuntoView.as_view(), name='nuevo_codigo_punto'),
    re_path(r'^codigo_punto/(?P<pk>\d+)/$', views.ActualizarCodigoPuntoView.as_view(), name='actualizar_codigo_punto'),

    re_path(r'^paciente/$', views.ListaPacientesView.as_view(), name='lista_pacientes'),
    re_path(r'^paciente/nuevo$', views.CrearPacienteView.as_view(), name='nuevo_paciente'),
    re_path(r'^paciente/(?P<pk>\d+)/$', views.ActualizarPacienteView.as_view(), name='actualizar_paciente'),

    re_path(r'^eps/$', views.ListaEpssView.as_view(), name='lista_epss'),
    re_path(r'^eps/nuevo$', views.CrearEpsView.as_view(), name='nueva_eps'),
    re_path(r'^eps/(?P<pk>\d+)/$', views.ActualizarEpsView.as_view(), name='actualizar_eps'),

    re_path(r'^institucion/$', views.ListaInstitucionsView.as_view(), name='lista_institucions'),
    re_path(r'^institucion/nuevo$', views.CrearInstitucionView.as_view(), name='nueva_institucion'),
    re_path(r'^institucion/(?P<pk>\d+)/$', views.ActualizarInstitucionView.as_view(), name='actualizar_institucion'),

    re_path(r'^responsable_recoleccion/$', views.ListaResponsableRecoleccionsView.as_view(), name='lista_responsable_recoleccions'),
    re_path(r'^responsable_recoleccion/nuevo$', views.CrearResponsableRecoleccionView.as_view(), name='nuevo_responsable_recoleccion'),
    re_path(r'^responsable_recoleccion/(?P<pk>\d+)/$', views.ActualizarResponsableRecoleccionView.as_view(), name='actualizar_responsable_recoleccion'),

    re_path(r'^lugar_recoleccion/$', views.ListaLugarRecoleccionsView.as_view(), name='lista_lugar_recoleccions'),
    re_path(r'^lugar_recoleccion/nuevo$', views.CrearLugarRecoleccionView.as_view(), name='nuevo_lugar_recoleccion'),
    re_path(r'^lugar_recoleccion/(?P<pk>\d+)/$', views.ActualizarLugarRecoleccionView.as_view(), name='actualizar_lugar_recoleccion'),

    re_path(r'^tipo_vigilancia/$', views.ListaTipoVigilanciasView.as_view(), name='lista_tipo_vigilancias'),
    re_path(r'^tipo_vigilancia/nuevo$', views.CrearTipoVigilanciaView.as_view(), name='nuevo_tipo_vigilancia'),
    re_path(r'^tipo_vigilancia/(?P<pk>\d+)/$', views.ActualizarTipoVigilanciaView.as_view(), name='actualizar_tipo_vigilancia'),

    re_path(r'^tipo_envase/$', views.ListaTipoEnvasesView.as_view(), name='lista_tipo_envases'),
    re_path(r'^tipo_envase/nuevo$', views.CrearTipoEnvaseView.as_view(), name='nuevo_tipo_envase'),
    re_path(r'^tipo_envase/(?P<pk>\d+)/$', views.ActualizarTipoEnvaseView.as_view(), name='actualizar_tipo_envase'),

    re_path(r'^institucion_banco_sangre/$', views.ListaInstitucionBancoSangresView.as_view(), name='lista_institucion_banco_sangres'),
    re_path(r'^institucion_banco_sangre/nuevo$', views.CrearInstitucionBancoSangreView.as_view(), name='nuevo_institucion_banco_sangre'),
    re_path(r'^institucion_banco_sangre/(?P<pk>\d+)/$', views.ActualizarInstitucionBancoSangreView.as_view(), name='actualizar_institucion_banco_sangre'),

    re_path(r'^programa_evaluacion_externa/$', views.ListaProgramaEvaluacionExternasView.as_view(), name='lista_programa_evaluacion_externas'),
    re_path(r'^programa_evaluacion_externa/nuevo$', views.CrearProgramaEvaluacionExternaView.as_view(), name='nuevo_programa_evaluacion_externa'),
    re_path(r'^programa_evaluacion_externa/(?P<pk>\d+)/$', views.ActualizarProgramaEvaluacionExternaView.as_view(), name='actualizar_programa_evaluacion_externa'),

    re_path(r'^tipo_evento_evaluacion_externa/$', views.ListaTipoEventoEvaluacionExternasView.as_view(), name='lista_tipo_evento_evaluacion_externas'),
    re_path(r'^tipo_evento_evaluacion_externa/nuevo$', views.CrearTipoEventoEvaluacionExternaView.as_view(), name='nuevo_tipo_evento_evaluacion_externa'),
    re_path(r'^tipo_evento_evaluacion_externa/(?P<pk>\d+)/$', views.ActualizarTipoEventoEvaluacionExternaView.as_view(), name='actualizar_tipo_evento_evaluacion_externa'),

    re_path(r'^institucion_eedd/$', views.ListaInstitucionEEDDsView.as_view(), name='lista_institucion_eedds'),
    re_path(r'^institucion_eedd/nuevo$', views.CrearInstitucionEEDDView.as_view(), name='nuevo_institucion_eedd'),
    re_path(r'^institucion_eedd/(?P<pk>\d+)/$', views.ActualizarInstitucionEEDDView.as_view(), name='actualizar_institucion_eedd'),

    re_path(r'^institucion_eeid/$', views.ListaInstitucionEEIDsView.as_view(), name='lista_institucion_eeids'),
    re_path(r'^institucion_eeid/nuevo$', views.CrearInstitucionEEIDView.as_view(), name='nuevo_institucion_eeid'),
    re_path(r'^institucion_eeid/(?P<pk>\d+)/$', views.ActualizarInstitucionEEIDView.as_view(), name='actualizar_institucion_eeid'),

    re_path(r'^institucion_citohistopatologia/$', views.ListaInstitucionCitohistopatologiasView.as_view(), name='lista_institucion_citohistopatologias'),
    re_path(r'^institucion_citohistopatologia/nuevo$', views.CrearInstitucionCitohistopatologiaView.as_view(), name='nuevo_institucion_citohistopatologia'),
    re_path(r'^institucion_citohistopatologia/(?P<pk>\d+)/$', views.ActualizarInstitucionCitohistopatologiaView.as_view(), name='actualizar_institucion_citohistopatologia'),

    re_path(r'^control/$', views.ListaControlsView.as_view(), name='lista_controls'),
    re_path(r'^control/nuevo$', views.CrearControlView.as_view(), name='nuevo_control'),
    re_path(r'^control/(?P<pk>\d+)/$', views.ActualizarControlView.as_view(), name='actualizar_control'),

    re_path(r'^tipo_evento/$', views.ListaTipoEventosView.as_view(), name='lista_tipo_eventos'),
    re_path(r'^tipo_evento/nuevo$', views.CrearTipoEventoView.as_view(), name='nuevo_tipo_evento'),
    re_path(r'^tipo_evento/(?P<pk>\d+)/$', views.ActualizarTipoEventoView.as_view(), name='actualizar_tipo_evento'),

    path('usuario/nuevo/', views.CrearUsuarioView.as_view(), name='nuevo_usuario'),
    path('listar_usuarios/', views.ListaUsuariosView.as_view(), name='lista_usuarios'),
    path('usuario/<int:pk>/', views.ActualizarUsuarioView.as_view(), name='actualizar_usuario'),

    path('empleado/', views.ListaEmpleadosView.as_view(), name='lista_empleados'),
    path('empleado/nuevo/', views.CrearEmpleadoView.as_view(), name='nuevo_empleado'),
    path('empleado/<int:pk>/', views.ActualizarEmpleadoView.as_view(), name='actualizar_empleado'),

    re_path(r'^equipo/$', views.ListaEquiposView.as_view(), name='lista_equipos'),
    re_path(r'^equipo/nuevo$', views.CrearEquipoView.as_view(), name='nuevo_equipo'),
    re_path(r'^equipo/(?P<pk>\d+)/$', views.ActualizarEquipoView.as_view(), name='actualizar_equipo'),

    re_path(r'^solicitante_alimento/$', views.ListaSolicitanteAlimentosView.as_view(), name='lista_solicitante_alimentos'),
    re_path(r'^solicitante_alimento/nuevo$', views.CrearSolicitanteAlimentoView.as_view(), name='nuevo_solicitante_alimento'),
    re_path(r'^solicitante_alimento/(?P<pk>\d+)/$', views.ActualizarSolicitanteAlimentoView.as_view(), name='actualizar_solicitante_alimento'),

    re_path(r'^grupo/$', views.ListaGruposView.as_view(), name='lista_grupos'),
    re_path(r'^grupo/nuevo$', views.CrearGrupoView.as_view(), name='nuevo_grupo'),
    re_path(r'^grupo/(?P<pk>\d+)/$', views.ActualizarGrupoView.as_view(), name='actualizar_grupo'),

    re_path(r'^categoria/$', views.ListaCategoriasView.as_view(), name='lista_categorias'),
    re_path(r'^categoria/nuevo$', views.CrearCategoriaView.as_view(), name='nuevo_categoria'),
    re_path(r'^categoria/(?P<pk>\d+)/$', views.ActualizarCategoriaView.as_view(), name='actualizar_categoria'),

    re_path(r'^sub_categoria/$', views.ListaSubcategoriasView.as_view(), name='lista_sub_categorias'),
    re_path(r'^sub_categoria/nuevo$', views.CrearSubcategoriaView.as_view(), name='nuevo_sub_categoria'),
    re_path(r'^sub_categoria/(?P<pk>\d+)/$', views.ActualizarSubcategoriaView.as_view(), name='actualizar_sub_categoria'),

    re_path(r'^fabricante/$', views.ListaFabricantesView.as_view(), name='lista_fabricantes'),
    re_path(r'^fabricante/nuevo$', views.CrearFabricanteView.as_view(), name='nuevo_fabricante'),
    re_path(r'^fabricante/(?P<pk>\d+)/$', views.ActualizarFabricanteView.as_view(), name='actualizar_fabricante'),

    re_path(r'^distribuidor/$', views.ListaDistribuidorsView.as_view(), name='lista_distribuidors'),
    re_path(r'^distribuidor/nuevo$', views.CrearDistribuidorView.as_view(), name='nuevo_distribuidor'),
    re_path(r'^distribuidor/(?P<pk>\d+)/$', views.ActualizarDistribuidorView.as_view(), name='actualizar_distribuidor'),

    re_path(r'^areas/$', views.ListaAreasView.as_view(), name='lista_areas'),
    re_path(r'^areas/(?P<pk>\d+)/$', views.ActualizarAreaView.as_view(), name='actualizar_area'),

    re_path(r'^grupo_bebida_alcoholica/$', views.ListaGrupoBebidaAlcoholicasView.as_view(), name='lista_grupo_bebida_alcoholicas'),
    re_path(r'^grupo_bebida_alcoholica/nuevo$', views.CrearGrupoBebidaAlcoholicaView.as_view(), name='nuevo_grupo_bebida_alcoholica'),
    re_path(r'^grupo_bebida_alcoholica/(?P<pk>\d+)/$', views.ActualizarGrupoBebidaAlcoholicaView.as_view(), name='actualizar_grupo_bebida_alcoholica'),

    re_path(r'^producto/$', views.ListaProductosView.as_view(), name='lista_productos'),
    re_path(r'^producto/nuevo$', views.CrearProductoView.as_view(), name='nuevo_producto'),
    re_path(r'^producto/(?P<pk>\d+)/$', views.ActualizarProductoView.as_view(), name='actualizar_producto'),

    re_path(r'^decreto/$', views.ListaDecretosView.as_view(), name='lista_decretos'),
    re_path(r'^decreto/nuevo$', views.CrearDecretoView.as_view(), name='nuevo_decreto'),
    re_path(r'^decreto/(?P<pk>\d+)/$', views.ActualizarDecretoView.as_view(), name='actualizar_decreto'),

    re_path(r'^normatividad/$', views.ListaNormatividadsView.as_view(), name='lista_normatividads'),
    re_path(r'^normatividad/nuevo$', views.CrearNormatividadView.as_view(), name='nuevo_normatividad'),
    re_path(r'^normatividad/(?P<pk>\d+)/$', views.ActualizarNormatividadView.as_view(), name='actualizar_normatividad'),

    re_path(r'^tipo_envase_bebida_alcoholica/$', views.ListaTipoEnvaseBebidaAlcoholicasView.as_view(), name='lista_tipo_envase_bebida_alcoholicas'),
    re_path(r'^tipo_envase_bebida_alcoholica/nuevo$', views.CrearTipoEnvaseBebidaAlcoholicaView.as_view(), name='nuevo_tipo_envase_bebida_alcoholica'),
    re_path(r'^tipo_envase_bebida_alcoholica/(?P<pk>\d+)/$', views.ActualizarTipoEnvaseBebidaAlcoholicaView.as_view(), name='actualizar_tipo_envase_bebida_alcoholica'),

    path('upgds/', views.ListaUpgdView.as_view(), name='lista_upgd'),
    path('upgds/nuevo/', views.CrearUpgdView.as_view(), name='nuevo_upgd'),
    path('upgds/<int:pk>/', views.ActualizarUpgdView.as_view(), name='actualizar_upgd'),
    
    path('eapbs/', views.ListaEapbView.as_view(), name='lista_eapb'),
    path('eapbs/nuevo/', views.CrearEapbView.as_view(), name='nuevo_eapb'),
    path('eapbs/<int:pk>/', views.ActualizarEapbView.as_view(), name='actualizar_eapb'),
    
    path('tipificaciones/', views.ListaTipificacionView.as_view(), name='lista_tipificacion'),
    path('tipificaciones/nuevo/', views.CrearTipificacionView.as_view(), name='nuevo_tipificacion'),
    path('tipificaciones/<int:pk>/', views.ActualizarTipificacionView.as_view(), name='actualizar_tipificacion'),
    
    path('ocupaciones/', views.ListaOcupacionView.as_view(), name='lista_ocupacion'),
    path('ocupaciones/nuevo/', views.CrearOcupacionView.as_view(), name='nuevo_ocupacion'),
    path('ocupaciones/<int:pk>/', views.ActualizarOcupacionView.as_view(), name='actualizar_ocupacion'),
    
    path('configuracion/', views.ConfigGeneralView.as_view(), name='config_general'),
]

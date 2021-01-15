from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group, User
from django.views import generic
from django.db.models import Q #Multiple Filters
from braces.views import LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin
from common.decorators import grupo_requerido
from alimentos.models import Solicitante as SolicitanteAlimento, Grupo, Categoria, Subcategoria
from alimentos.models import Distribuidor, Fabricante, Decreto as Normatividad
from bebidas_alcoholicas.models import Grupo as GrupoBebidaAlcoholica, Producto
from bebidas_alcoholicas.models import Decreto, TipoEnvase as TipoEnvaseBebidaAlcoholica
from equipos.models import Equipo
from trazabilidad.models import Metodo, MotivoRechazo, Departamento, Municipio, Poblado, MotivoAnalisis, Epsa
from trazabilidad.models import ObjetoPrueba, ResultadoPrueba, TipoMuestra, CategoriaAgua, TipoAgua, Temperatura, Area
from trazabilidad.models import Solicitante, DescripcionPunto, FuenteAbastecimiento, LugarPunto, CodigoPunto, Paciente
from trazabilidad.models import Eps, Institucion, ResponsableRecoleccion, LugarRecoleccion, TipoVigilancia, TipoEnvase
from trazabilidad.models import InstitucionBancoSangre, ProgramaEvaluacionExterna, TipoEventoEvaluacionExterna, Prueba
from trazabilidad.models import InstitucionEEDD, InstitucionEEID, Control, InstitucionCitohistopatologia, TipoEvento
from covid19 import models as covid_models
from .models import Empleado
from .forms import NuevaPruebaForm, NuevoMetodoForm, NuevoMotivoRechazoForm, NuevoPacienteForm, NuevoDepartamentoForm
from .forms import NuevoPobladoForm, NuevaEpsForm, NuevoMotivoAnalisisForm, NuevoObjetoPruebaForm
from .forms import NuevoTipoMuestraForm, NuevoEpsaForm, NuevoCategoriaAguaForm, NuevoTipoAguaForm, NuevoTemperaturaForm
from .forms import NuevoSolicitanteForm, NuevoDescripcionPuntoForm, NuevoFuenteAbastecimientoForm, NuevoLugarPuntoForm
from .forms import NuevoCodigoPuntoForm, NuevaInstitucionForm, NuevoResponsableRecoleccionForm, NuevoTipoVigilanciaForm
from .forms import NuevoLugarRecoleccionForm, NuevoTipoEnvaseForm, NuevoInstitucionBancoSangreForm
from .forms import NuevoInstitucionEEDDForm, NuevoInstitucionEEIDForm, NuevoTipoEventoEvaluacionExternaForm
from .forms import NuevoProgramaEvaluacionExternaForm, NuevoInstitucionCitohistopatologiaForm, NuevoControlForm
from .forms import ActualizarTipoVigilanciaForm, ActualizarTipoEnvaseForm, NuevoTipoEventoForm, ActualizarPruebaForm
from .forms import ActualizarResponsableRecoleccionForm, ActualizarLugarRecoleccionForm, ActualizarMetodoForm
from .forms import ActualizarMotivoRechazoForm, ActualizarDepartamentoForm
from .forms import ActualizarPobladoForm, ActualizarMotivoAnalisisForm, ActualizarObjetoPruebaForm
from .forms import NuevoResultadoPruebaForm, ActualizarResultadoPruebaForm, ActualizarTipoMuestraForm
from .forms import ActualizarPacienteForm, ActualizarEpsForm, ActualizarInstitucionForm, ActualizarEpsaForm
from .forms import ActualizarCategoriaAguaForm, ActualizarTipoAguaForm, ActualizarTemperaturaForm
from .forms import ActualizarSolicitanteForm, ActualizarDescripcionPuntoForm, ActualizarFuenteAbastecimientoForm
from .forms import ActualizarLugarPuntoForm, ActualizarCodigoPuntoForm, ActualizarInstitucionBancoSangreForm
from .forms import ActualizarProgramaEvaluacionExternaForm, ActualizarTipoEventoEvaluacionExternaForm
from .forms import ActualizarInstitucionEEDDForm, ActualizarInstitucionEEIDForm, ActualizarControlForm
from .forms import ActualizarInstitucionCitohistopatologiaForm, ActualizarTipoEventoForm, NuevoUsuarioForm
from .forms import NuevoEmpleadoForm, ActualizarEmpleadoForm, ActualizarUsuarioForm
from .forms import NuevoEquipoForm, ActualizarEquipoForm, NuevoSolicitanteAlimentoForm, NuevoGrupoForm
from .forms import ActualizarSolicitanteAlimentoForm, ActualizarGrupoForm, NuevoCategoriaForm, ActualizarCategoriaForm
from .forms import NuevoSubcategoriaForm, ActualizarSubcategoriaForm, NuevoFabricanteForm, ActualizarFabricanteForm
from .forms import NuevoDistribuidorForm, ActualizarDistribuidorForm, ActualizarAreaForm
from .forms import NuevoGrupoBebidaAlcoholicaForm, ActualizarGrupoBebidaAlcoholicaForm, NuevoProductoForm
from .forms import ActualizarProductoForm, NuevoDecretoForm, ActualizarDecretoForm, NuevoTipoEnvaseBebidaAlcoholicaForm
from .forms import ActualizarTipoEnvaseBebidaAlcoholicaForm, NuevoNormatividadForm, ActualizarNormatividadForm
from . import models as m
from . import forms

class ListaAreasView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Retorna una lista de Areas ingresadas en el sistema."""

    model = Area
    template_name = 'administracion/lista_areas.html'

    group_required = ['administrador', 'super usuario']


class ActualizarAreaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una Area especifica."""

    model = Area
    form_class = ActualizarAreaForm
    template_name = 'administracion/formulario_area.html'
    success_url = reverse_lazy('administracion:lista_areas')

    group_required = ['administrador', 'super usuario']


class ListaPruebasView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de pruebas ingresadas en el sistema."""

    model = Prueba
    template_name = 'administracion/lista_pruebas.html'
    group_required = ['administrador', 'super usuario']
    queryset = Prueba.objects.select_related('area', 'modificado_por').all()


class CrearPruebaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de pruebas."""

    model = Prueba
    form_class = NuevaPruebaForm
    template_name = 'administracion/formulario_prueba.html'
    success_url = reverse_lazy('administracion:lista_pruebas')

    group_required = ['administrador', 'super usuario']


class ActualizarPruebaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una prueba especifica."""

    model = Prueba
    form_class = ActualizarPruebaForm
    template_name = 'administracion/formulario_prueba.html'
    success_url = reverse_lazy('administracion:lista_pruebas')

    group_required = ['administrador', 'super usuario']


class ListaMetodosView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de los metodos ingresados en el sistema."""

    model = Metodo
    template_name = 'administracion/lista_metodos.html'

    group_required = ['administrador', 'super usuario']


class CrearMetodoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = Metodo
    form_class = NuevoMetodoForm
    template_name = 'administracion/formulario_metodo.html'
    success_url = reverse_lazy('administracion:lista_metodos')

    group_required = ['administrador', 'super usuario']


class ActualizarMetodoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = Metodo
    form_class = ActualizarMetodoForm
    template_name = 'administracion/formulario_metodo.html'
    success_url = reverse_lazy('administracion:lista_metodos')

    group_required = ['administrador', 'super usuario']


class ListaMotivoRechazosView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    model = MotivoRechazo
    template_name = 'administracion/lista_motivo_rechazos.html'

    group_required = ['administrador', 'super usuario']


class CrearMotivoRechazoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = MotivoRechazo
    form_class = NuevoMotivoRechazoForm
    template_name = 'administracion/formulario_motivo_rechazo.html'
    success_url = reverse_lazy('administracion:lista_motivo_rechazos')

    group_required = ['administrador', 'super usuario']


class ActualizarMotivoRechazoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = MotivoRechazo
    form_class = ActualizarMotivoRechazoForm
    template_name = 'administracion/formulario_motivo_rechazo.html'
    success_url = reverse_lazy('administracion:lista_motivo_rechazos')

    group_required = ['administrador', 'super usuario']


class ListaDepartamentosView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    model = Departamento
    template_name = 'administracion/lista_departamentos.html'

    group_required = ['administrador', 'super usuario']


class CrearDepartamentoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = Departamento
    form_class = NuevoDepartamentoForm
    template_name = 'administracion/formulario_departamento.html'
    success_url = reverse_lazy('administracion:lista_departamentos')

    group_required = ['administrador', 'super usuario']


class ActualizarDepartamentoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = Departamento
    form_class = ActualizarDepartamentoForm
    template_name = 'administracion/formulario_departamento.html'
    success_url = reverse_lazy('administracion:lista_departamentos')

    group_required = ['administrador', 'super usuario']


class ListaMunicipiosView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    group_required = ['administrador', 'super usuario']
    template_name = 'administracion/lista_municipios.html'
    queryset = Municipio.objects.select_related('departamento', 'modificado_por').all()

class CrearMunicipioView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = Municipio
    form_class = forms.NuevoMunicipioForm
    template_name = 'administracion/formulario_municipio.html'
    success_url = reverse_lazy('administracion:lista_municipios')

    group_required = ['administrador', 'super usuario']

class ActualizarMunicipioView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = Municipio
    form_class = forms.ActualizarMunicipioForm
    template_name = 'administracion/formulario_municipio.html'
    success_url = reverse_lazy('administracion:lista_municipios')

    group_required = ['administrador', 'super usuario']


class ListaPobladosView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    model = Poblado
    template_name = 'administracion/lista_poblados.html'

    group_required = ['administrador', 'super usuario']


class CrearPobladoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = Poblado
    form_class = NuevoPobladoForm
    template_name = 'administracion/formulario_poblado.html'
    success_url = reverse_lazy('administracion:lista_poblados')

    group_required = ['administrador', 'super usuario']


class ActualizarPobladoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = Poblado
    form_class = ActualizarPobladoForm
    template_name = 'administracion/formulario_poblado.html'
    success_url = reverse_lazy('administracion:lista_poblados')

    group_required = ['administrador', 'super usuario']


class ListaMotivoAnalisisView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    model = MotivoAnalisis
    template_name = 'administracion/lista_motivo_analisis.html'

    group_required = ['administrador', 'super usuario']


class CrearMotivoAnalisisView(LoginRequiredMixin, GroupRequiredMixin, CreateView):

    model = MotivoAnalisis
    form_class = NuevoMotivoAnalisisForm
    template_name = 'administracion/formulario_motivo_analisis.html'
    success_url = reverse_lazy('administracion:lista_motivo_analisis')

    group_required = ['administrador', 'super usuario']


class ActualizarMotivoAnalisisView(LoginRequiredMixin, GroupRequiredMixin, UpdateView):

    model = MotivoAnalisis
    form_class = ActualizarMotivoAnalisisForm
    template_name = 'administracion/formulario_motivo_analisis.html'
    success_url = reverse_lazy('administracion:lista_motivo_analisis')

    group_required = ['administrador', 'super usuario']


class ListaObjetoPruebasView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    model = ObjetoPrueba
    template_name = 'administracion/lista_objeto_pruebas.html'

    group_required = ['administrador', 'super usuario']


class CrearObjetoPruebaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = ObjetoPrueba
    form_class = NuevoObjetoPruebaForm
    template_name = 'administracion/formulario_objeto_prueba.html'
    success_url = reverse_lazy('administracion:lista_objeto_pruebas')

    group_required = ['administrador', 'super usuario']


class ActualizarObjetoPruebaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = ObjetoPrueba
    form_class = ActualizarObjetoPruebaForm
    template_name = 'administracion/formulario_objeto_prueba.html'
    success_url = reverse_lazy('administracion:lista_objeto_pruebas')

    group_required = ['administrador', 'super usuario']


class ListaResultadoPruebasView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    model = ResultadoPrueba
    queryset = ResultadoPrueba.objects.all().select_related('modificado_por')
    template_name = 'administracion/lista_resultado_pruebas.html'

    group_required = ['administrador', 'super usuario']


class CrearResultadoPruebaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = ResultadoPrueba
    form_class = NuevoResultadoPruebaForm
    template_name = 'administracion/formulario_resultado_prueba.html'
    success_url = reverse_lazy('administracion:lista_resultado_pruebas')

    group_required = ['administrador', 'super usuario']


class ActualizarResultadoPruebaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = ResultadoPrueba
    form_class = ActualizarResultadoPruebaForm
    template_name = 'administracion/formulario_resultado_prueba.html'
    success_url = reverse_lazy('administracion:lista_resultado_pruebas')

    group_required = ['administrador', 'super usuario']


class ListaTipoMuestrasView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    model = TipoMuestra
    template_name = 'administracion/lista_tipo_muestras.html'
    queryset = TipoMuestra.objects.select_related('modificado_por').prefetch_related('programas').all()

    group_required = ['administrador', 'super usuario']


class CrearTipoMuestraView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = TipoMuestra
    form_class = NuevoTipoMuestraForm
    template_name = 'administracion/formulario_tipo_muestra.html'
    success_url = reverse_lazy('administracion:lista_tipo_muestras')

    group_required = ['administrador', 'super usuario']


class ActualizarTipoMuestraView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = TipoMuestra
    form_class = ActualizarTipoMuestraForm
    template_name = 'administracion/formulario_tipo_muestra.html'
    success_url = reverse_lazy('administracion:lista_tipo_muestras')

    group_required = ['administrador', 'super usuario']


class ListaPacientesView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de Pacientes ingresadas en el sistema."""

    template_name = 'administracion/lista_pacientes.html'

    group_required = ['administrador', 'super usuario']

    def get_queryset(self):    
        if self.request.GET.get('q')==None:
            return None
        else:
            filters = Q(nombre__icontains=self.query()) | Q(apellido__icontains=self.query()) | Q(identificacion__icontains=self.query())
            return Paciente.objects.filter(filters)
    
    def query(self):
        return self.request.GET.get('q')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.query()!=None:
            context['query'] = self.query()
        return context


class CrearPacienteView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de Pacientes."""

    model = Paciente
    form_class = NuevoPacienteForm
    template_name = 'administracion/formulario_paciente.html'
    success_url = reverse_lazy('administracion:lista_pacientes')

    group_required = ['administrador', 'super usuario']


class ActualizarPacienteView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una Paciente especifica."""

    model = Paciente
    form_class = ActualizarPacienteForm
    template_name = 'administracion/formulario_paciente.html'
    success_url = reverse_lazy('administracion:lista_pacientes')

    group_required = ['administrador', 'super usuario']


class ListaEpsasView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    model = Epsa
    template_name = 'administracion/lista_epsas.html'

    group_required = ['administrador', 'super usuario']


class CrearEpsaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = Epsa
    form_class = NuevoEpsaForm
    template_name = 'administracion/formulario_epsa.html'
    success_url = reverse_lazy('administracion:lista_epsas')

    group_required = ['administrador', 'super usuario']


class ActualizarEpsaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = Epsa
    form_class = ActualizarEpsaForm
    template_name = 'administracion/formulario_epsa.html'
    success_url = reverse_lazy('administracion:lista_epsas')

    group_required = ['administrador', 'super usuario']


class ListaCategoriaAguasView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    model = CategoriaAgua
    template_name = 'administracion/lista_categoria_aguas.html'

    group_required = ['administrador', 'super usuario']


class CrearCategoriaAguaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = CategoriaAgua
    form_class = NuevoCategoriaAguaForm
    template_name = 'administracion/formulario_categoria_agua.html'
    success_url = reverse_lazy('administracion:lista_categoria_aguas')

    group_required = ['administrador', 'super usuario']


class ActualizarCategoriaAguaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = CategoriaAgua
    form_class = ActualizarCategoriaAguaForm
    template_name = 'administracion/formulario_categoria_agua.html'
    success_url = reverse_lazy('administracion:lista_categoria_aguas')

    group_required = ['administrador', 'super usuario']


class ListaTipoAguasView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    model = TipoAgua
    template_name = 'administracion/lista_tipo_aguas.html'

    group_required = ['administrador', 'super usuario']


class CrearTipoAguaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = TipoAgua
    form_class = NuevoTipoAguaForm
    template_name = 'administracion/formulario_tipo_agua.html'
    success_url = reverse_lazy('administracion:lista_tipo_aguas')

    group_required = ['administrador', 'super usuario']


class ActualizarTipoAguaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = TipoAgua
    form_class = ActualizarTipoAguaForm
    template_name = 'administracion/formulario_tipo_agua.html'
    success_url = reverse_lazy('administracion:lista_tipo_aguas')

    group_required = ['administrador', 'super usuario']


class ListaTemperaturasView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    model = Temperatura
    template_name = 'administracion/lista_temperaturas.html'

    group_required = ['administrador', 'super usuario']


class CrearTemperaturaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = Temperatura
    form_class = NuevoTemperaturaForm
    template_name = 'administracion/formulario_temperatura.html'
    success_url = reverse_lazy('administracion:lista_temperaturas')

    group_required = ['administrador', 'super usuario']


class ActualizarTemperaturaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = Temperatura
    form_class = ActualizarTemperaturaForm
    template_name = 'administracion/formulario_temperatura.html'
    success_url = reverse_lazy('administracion:lista_temperaturas')

    group_required = ['administrador', 'super usuario']


class ListaSolicitantesView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    model = Solicitante
    template_name = 'administracion/lista_solicitantes.html'

    group_required = ['administrador', 'super usuario']


class CrearSolicitanteView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = Solicitante
    form_class = NuevoSolicitanteForm
    template_name = 'administracion/formulario_solicitante.html'
    success_url = reverse_lazy('administracion:lista_solicitantes')

    group_required = ['administrador', 'super usuario']


class ActualizarSolicitanteView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = Solicitante
    form_class = ActualizarSolicitanteForm
    template_name = 'administracion/formulario_solicitante.html'
    success_url = reverse_lazy('administracion:lista_solicitantes')

    group_required = ['administrador', 'super usuario']


class ListaDescripcionPuntosView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    model = DescripcionPunto
    template_name = 'administracion/lista_descripcion_puntos.html'

    group_required = ['administrador', 'super usuario']


class CrearDescripcionPuntoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = DescripcionPunto
    form_class = NuevoDescripcionPuntoForm
    template_name = 'administracion/formulario_descripcion_punto.html'
    success_url = reverse_lazy('administracion:lista_descripcion_puntos')

    group_required = ['administrador', 'super usuario']


class ActualizarDescripcionPuntoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = DescripcionPunto
    form_class = ActualizarDescripcionPuntoForm
    template_name = 'administracion/formulario_descripcion_punto.html'
    success_url = reverse_lazy('administracion:lista_descripcion_puntos')

    group_required = ['administrador', 'super usuario']


class ListaFuenteAbastecimientosView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    model = FuenteAbastecimiento
    template_name = 'administracion/lista_fuente_abastecimientos.html'

    group_required = ['administrador', 'super usuario']


class CrearFuenteAbastecimientoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = FuenteAbastecimiento
    form_class = NuevoFuenteAbastecimientoForm
    template_name = 'administracion/formulario_fuente_abastecimiento.html'
    success_url = reverse_lazy('administracion:lista_fuente_abastecimientos')

    group_required = ['administrador', 'super usuario']


class ActualizarFuenteAbastecimientoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = FuenteAbastecimiento
    form_class = ActualizarFuenteAbastecimientoForm
    template_name = 'administracion/formulario_fuente_abastecimiento.html'
    success_url = reverse_lazy('administracion:lista_fuente_abastecimientos')

    group_required = ['administrador', 'super usuario']


class ListaLugarPuntosView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    model = LugarPunto
    template_name = 'administracion/lista_lugar_puntos.html'

    group_required = ['administrador', 'super usuario']


class CrearLugarPuntoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = LugarPunto
    form_class = NuevoLugarPuntoForm
    template_name = 'administracion/formulario_lugar_punto.html'
    success_url = reverse_lazy('administracion:lista_lugar_puntos')

    group_required = ['administrador', 'super usuario']


class ActualizarLugarPuntoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = LugarPunto
    form_class = ActualizarLugarPuntoForm
    template_name = 'administracion/formulario_lugar_punto.html'
    success_url = reverse_lazy('administracion:lista_lugar_puntos')

    group_required = ['administrador', 'super usuario']


class ListaCodigoPuntosView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    model = CodigoPunto
    queryset = (
        CodigoPunto.objects
            .all()
            .select_related(
                'lugar_toma', 'fuente_abastecimiento', 'poblado__municipio__departamento', 'modificado_por', 'descripcion'
            )
        )
    template_name = 'administracion/lista_codigo_puntos.html'

    group_required = ['administrador', 'super usuario']


class CrearCodigoPuntoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = CodigoPunto
    form_class = NuevoCodigoPuntoForm
    template_name = 'administracion/formulario_codigo_punto.html'
    success_url = reverse_lazy('administracion:lista_codigo_puntos')

    group_required = ['administrador', 'super usuario']


class ActualizarCodigoPuntoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = CodigoPunto
    form_class = ActualizarCodigoPuntoForm
    template_name = 'administracion/formulario_codigo_punto.html'
    success_url = reverse_lazy('administracion:lista_codigo_puntos')

    group_required = ['administrador', 'super usuario']


class ListaEpssView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de Epss ingresadas en el sistema."""

    model = Eps
    template_name = 'administracion/lista_epss.html'

    group_required = ['administrador', 'super usuario']


class CrearEpsView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de Epss."""

    model = Eps
    form_class = NuevaEpsForm
    template_name = 'administracion/formulario_eps.html'
    success_url = reverse_lazy('administracion:lista_epss')

    group_required = ['administrador', 'super usuario']


class ActualizarEpsView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una Eps especifica."""

    model = Eps
    form_class = ActualizarEpsForm
    template_name = 'administracion/formulario_eps.html'
    success_url = reverse_lazy('administracion:lista_epss')

    group_required = ['administrador', 'super usuario']


class ListaInstitucionsView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de Institucions ingresadas en el sistema."""

    model = Institucion
    template_name = 'administracion/lista_institucions.html'

    group_required = ['administrador', 'super usuario']


class CrearInstitucionView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de Institucions."""

    model = Institucion
    form_class = NuevaInstitucionForm
    template_name = 'administracion/formulario_institucion.html'
    success_url = reverse_lazy('administracion:lista_institucions')

    group_required = ['administrador', 'super usuario']


class ActualizarInstitucionView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una Institucion especifica."""

    model = Institucion
    form_class = ActualizarInstitucionForm
    template_name = 'administracion/formulario_institucion.html'
    success_url = reverse_lazy('administracion:lista_institucions')

    group_required = ['administrador', 'super usuario']


class ListaResponsableRecoleccionsView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de ResponsableRecoleccions ingresadas en el sistema."""

    model = ResponsableRecoleccion
    template_name = 'administracion/lista_responsable_recoleccions.html'

    group_required = ['administrador', 'super usuario']


class CrearResponsableRecoleccionView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de ResponsableRecoleccions."""

    model = ResponsableRecoleccion
    form_class = NuevoResponsableRecoleccionForm
    template_name = 'administracion/formulario_responsable_recoleccion.html'
    success_url = reverse_lazy('administracion:lista_responsable_recoleccions')

    group_required = ['administrador', 'super usuario']


class ActualizarResponsableRecoleccionView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una ResponsableRecoleccion especifica."""

    model = ResponsableRecoleccion
    form_class = ActualizarResponsableRecoleccionForm
    template_name = 'administracion/formulario_responsable_recoleccion.html'
    success_url = reverse_lazy('administracion:lista_responsable_recoleccions')

    group_required = ['administrador', 'super usuario']


class ListaLugarRecoleccionsView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de LugarRecoleccions ingresadas en el sistema."""

    model = LugarRecoleccion
    template_name = 'administracion/lista_lugar_recoleccions.html'

    group_required = ['administrador', 'super usuario']


class CrearLugarRecoleccionView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de LugarRecoleccions."""

    model = LugarRecoleccion
    form_class = NuevoLugarRecoleccionForm
    template_name = 'administracion/formulario_lugar_recoleccion.html'
    success_url = reverse_lazy('administracion:lista_lugar_recoleccions')

    group_required = ['administrador', 'super usuario']


class ActualizarLugarRecoleccionView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una LugarRecoleccion especifica."""

    model = LugarRecoleccion
    form_class = ActualizarLugarRecoleccionForm
    template_name = 'administracion/formulario_lugar_recoleccion.html'
    success_url = reverse_lazy('administracion:lista_lugar_recoleccions')

    group_required = ['administrador', 'super usuario']


class ListaTipoVigilanciasView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de TipoVigilancias ingresadas en el sistema."""

    model = TipoVigilancia
    template_name = 'administracion/lista_tipo_vigilancias.html'

    group_required = ['administrador', 'super usuario']


class CrearTipoVigilanciaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de TipoVigilancias."""

    model = TipoVigilancia
    form_class = NuevoTipoVigilanciaForm
    template_name = 'administracion/formulario_tipo_vigilancia.html'
    success_url = reverse_lazy('administracion:lista_tipo_vigilancias')

    group_required = ['administrador', 'super usuario']


class ActualizarTipoVigilanciaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una TipoVigilancia especifica."""

    model = TipoVigilancia
    form_class = ActualizarTipoVigilanciaForm
    template_name = 'administracion/formulario_tipo_vigilancia.html'
    success_url = reverse_lazy('administracion:lista_tipo_vigilancias')

    group_required = ['administrador', 'super usuario']


class ListaTipoEnvasesView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de TipoEnvases ingresadas en el sistema."""

    model = TipoEnvase
    template_name = 'administracion/lista_tipo_envases.html'

    group_required = ['administrador', 'super usuario']


class CrearTipoEnvaseView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de TipoEnvases."""

    model = TipoEnvase
    form_class = NuevoTipoEnvaseForm
    template_name = 'administracion/formulario_tipo_envase.html'
    success_url = reverse_lazy('administracion:lista_tipo_envases')

    group_required = ['administrador', 'super usuario']


class ActualizarTipoEnvaseView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una TipoEnvase especifica."""

    model = TipoEnvase
    form_class = ActualizarTipoEnvaseForm
    template_name = 'administracion/formulario_tipo_envase.html'
    success_url = reverse_lazy('administracion:lista_tipo_envases')

    group_required = ['administrador', 'super usuario']


class ListaInstitucionBancoSangresView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de InstitucionBancoSangres ingresadas en el sistema."""

    model = InstitucionBancoSangre
    template_name = 'administracion/lista_institucion_banco_sangres.html'

    group_required = ['administrador', 'super usuario']


class CrearInstitucionBancoSangreView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de InstitucionBancoSangres."""

    model = InstitucionBancoSangre
    form_class = NuevoInstitucionBancoSangreForm
    template_name = 'administracion/formulario_institucion_banco_sangre.html'
    success_url = reverse_lazy('administracion:lista_institucion_banco_sangres')

    group_required = ['administrador', 'super usuario']


class ActualizarInstitucionBancoSangreView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una InstitucionBancoSangre especifica."""

    model = InstitucionBancoSangre
    form_class = ActualizarInstitucionBancoSangreForm
    template_name = 'administracion/formulario_institucion_banco_sangre.html'
    success_url = reverse_lazy('administracion:lista_institucion_banco_sangres')

    group_required = ['administrador', 'super usuario']


class ListaProgramaEvaluacionExternasView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de ProgramaEvaluacionExternas ingresadas en el sistema."""

    model = ProgramaEvaluacionExterna
    template_name = 'administracion/lista_programa_evaluacion_externas.html'

    group_required = ['administrador', 'super usuario']


class CrearProgramaEvaluacionExternaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de ProgramaEvaluacionExternas."""

    model = ProgramaEvaluacionExterna
    form_class = NuevoProgramaEvaluacionExternaForm
    template_name = 'administracion/formulario_programa_evaluacion_externa.html'
    success_url = reverse_lazy('administracion:lista_programa_evaluacion_externas')

    group_required = ['administrador', 'super usuario']


class ActualizarProgramaEvaluacionExternaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una ProgramaEvaluacionExterna especifica."""

    model = ProgramaEvaluacionExterna
    form_class = ActualizarProgramaEvaluacionExternaForm
    template_name = 'administracion/formulario_programa_evaluacion_externa.html'
    success_url = reverse_lazy('administracion:lista_programa_evaluacion_externas')

    group_required = ['administrador', 'super usuario']


class ListaTipoEventoEvaluacionExternasView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de TipoEventos ingresadas en el sistema."""

    model = TipoEventoEvaluacionExterna
    template_name = 'administracion/lista_tipo_evento_evaluacion_externas.html'

    group_required = ['administrador', 'super usuario']


class CrearTipoEventoEvaluacionExternaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de TipoEventos."""

    model = TipoEventoEvaluacionExterna
    form_class = NuevoTipoEventoEvaluacionExternaForm
    template_name = 'administracion/formulario_tipo_evento_evaluacion_externa.html'
    success_url = reverse_lazy('administracion:lista_tipo_evento_evaluacion_externas')

    group_required = ['administrador', 'super usuario']


class ActualizarTipoEventoEvaluacionExternaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una TipoEvento especifica."""

    model = TipoEventoEvaluacionExterna
    form_class = ActualizarTipoEventoEvaluacionExternaForm
    template_name = 'administracion/formulario_tipo_evento_evaluacion_externa.html'
    success_url = reverse_lazy('administracion:lista_tipo_evento_evaluacion_externas')

    group_required = ['administrador', 'super usuario']


class ListaInstitucionEEDDsView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de InstitucionEEDDs ingresadas en el sistema."""

    model = InstitucionEEDD
    template_name = 'administracion/lista_institucion_eedds.html'

    group_required = ['administrador', 'super usuario']


class CrearInstitucionEEDDView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de InstitucionEEDDs."""

    model = InstitucionEEDD
    form_class = NuevoInstitucionEEDDForm
    template_name = 'administracion/formulario_institucion_eedd.html'
    success_url = reverse_lazy('administracion:lista_institucion_eedds')

    group_required = ['administrador', 'super usuario']


class ActualizarInstitucionEEDDView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una InstitucionEEDD especifica."""

    model = InstitucionEEDD
    form_class = ActualizarInstitucionEEDDForm
    template_name = 'administracion/formulario_institucion_eedd.html'
    success_url = reverse_lazy('administracion:lista_institucion_eedds')

    group_required = ['administrador', 'super usuario']


class ListaInstitucionEEIDsView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de InstitucionEEIDs ingresadas en el sistema."""

    model = InstitucionEEID
    template_name = 'administracion/lista_institucion_eeids.html'

    group_required = ['administrador', 'super usuario']


class CrearInstitucionEEIDView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de InstitucionEEIDs."""

    model = InstitucionEEID
    form_class = NuevoInstitucionEEIDForm
    template_name = 'administracion/formulario_institucion_eeid.html'
    success_url = reverse_lazy('administracion:lista_institucion_eeids')

    group_required = ['administrador', 'super usuario']


class ActualizarInstitucionEEIDView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una InstitucionEEID especifica."""

    model = InstitucionEEID
    form_class = ActualizarInstitucionEEIDForm
    template_name = 'administracion/formulario_institucion_eeid.html'
    success_url = reverse_lazy('administracion:lista_institucion_eeids')

    group_required = ['administrador', 'super usuario']


class ListaInstitucionCitohistopatologiasView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de InstitucionCitohistopatologias ingresadas en el sistema."""

    model = InstitucionCitohistopatologia
    template_name = 'administracion/lista_institucion_citohistopatologias.html'

    group_required = ['administrador', 'super usuario']


class CrearInstitucionCitohistopatologiaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de InstitucionCitohistopatologias."""

    model = InstitucionCitohistopatologia
    form_class = NuevoInstitucionCitohistopatologiaForm
    template_name = 'administracion/formulario_institucion_citohistopatologia.html'
    success_url = reverse_lazy('administracion:lista_institucion_citohistopatologias')

    group_required = ['administrador', 'super usuario']


class ActualizarInstitucionCitohistopatologiaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una InstitucionCitohistopatologia especifica."""

    model = InstitucionCitohistopatologia
    form_class = ActualizarInstitucionCitohistopatologiaForm
    template_name = 'administracion/formulario_institucion_citohistopatologia.html'
    success_url = reverse_lazy('administracion:lista_institucion_citohistopatologias')

    group_required = ['administrador', 'super usuario']


class ListaControlsView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de Controls ingresadas en el sistema."""

    model = Control
    template_name = 'administracion/lista_controls.html'

    group_required = ['administrador', 'super usuario']


class CrearControlView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de Controls."""

    model = Control
    form_class = NuevoControlForm
    template_name = 'administracion/formulario_control.html'
    success_url = reverse_lazy('administracion:lista_controls')

    group_required = ['administrador', 'super usuario']


class ActualizarControlView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una Control especifica."""

    model = Control
    form_class = ActualizarControlForm
    template_name = 'administracion/formulario_control.html'
    success_url = reverse_lazy('administracion:lista_controls')

    group_required = ['administrador', 'super usuario']


class ListaTipoEventosView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de TipoEventos ingresadas en el sistema."""

    model = TipoEvento
    template_name = 'administracion/lista_tipo_eventos.html'

    group_required = ['administrador', 'super usuario']


class CrearTipoEventoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de TipoEventos."""

    model = TipoEvento
    form_class = NuevoTipoEventoForm
    template_name = 'administracion/formulario_tipo_evento.html'
    success_url = reverse_lazy('administracion:lista_tipo_eventos')

    group_required = ['administrador', 'super usuario']


class ActualizarTipoEventoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una TipoEvento especifica."""

    model = TipoEvento
    form_class = ActualizarTipoEventoForm
    template_name = 'administracion/formulario_tipo_evento.html'
    success_url = reverse_lazy('administracion:lista_tipo_eventos')

    group_required = ['administrador', 'super usuario']

class ListaUsuariosView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de Usuarios ingresadas en el sistema."""

    model = User
    template_name = 'administracion/lista_usuarios.html'
    group_required = ['administrador', 'super usuario']
    queryset = User.objects.filter(is_superuser=False).select_related('empleado')

class CrearUsuarioView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    model = User
    form_class = NuevoUsuarioForm
    group_required = ['administrador', 'super usuario']
    template_name = 'administracion/formulario_usuario.html'
    success_url = reverse_lazy('administracion:lista_usuarios')

class ActualizarUsuarioView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    model = User
    form_class = ActualizarUsuarioForm
    group_required = ['administrador', 'super usuario']
    template_name = 'administracion/formulario_usuario.html'
    success_url = reverse_lazy('administracion:lista_usuarios')

class ListaEmpleadosView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de TipoEventos ingresadas en el sistema."""

    model = Empleado
    template_name = 'administracion/lista_empleados.html'
    group_required = ['administrador', 'super usuario']
    queryset = Empleado.objects.select_related('usuario').prefetch_related('areas').all()


class CrearEmpleadoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de TipoEventos."""

    model = Empleado
    form_class = NuevoEmpleadoForm
    group_required = ['administrador', 'super usuario']
    template_name = 'administracion/formulario_empleado.html'
    success_url = reverse_lazy('administracion:lista_empleados')

class ActualizarEmpleadoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una TipoEvento especifica."""

    model = Empleado
    form_class = ActualizarEmpleadoForm
    group_required = ['administrador', 'super usuario']
    template_name = 'administracion/formulario_empleado.html'
    success_url = reverse_lazy('administracion:lista_empleados')


class ListaEquiposView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de Equipos ingresadas en el sistema."""

    model = Equipo
    queryset = Equipo.objects.all().select_related('area', 'modificado_por')
    template_name = 'administracion/lista_equipos.html'

    group_required = ['administrador', 'super usuario']


class CrearEquipoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de Equipos."""

    model = Equipo
    form_class = NuevoEquipoForm
    template_name = 'administracion/formulario_equipo.html'
    success_url = reverse_lazy('administracion:lista_equipos')

    group_required = ['administrador', 'super usuario']


class ActualizarEquipoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una Equipo especifica."""

    model = Equipo
    form_class = ActualizarEquipoForm
    template_name = 'administracion/formulario_equipo.html'
    success_url = reverse_lazy('administracion:lista_equipos')

    group_required = ['administrador', 'super usuario']


class ListaSolicitanteAlimentosView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de Solicitantes ingresadas en el sistema."""

    model = SolicitanteAlimento
    template_name = 'administracion/lista_solicitante_alimentos.html'

    group_required = ['administrador', 'super usuario']


class CrearSolicitanteAlimentoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de SolicitanteAlimentos."""

    model = SolicitanteAlimento
    form_class = NuevoSolicitanteAlimentoForm
    template_name = 'administracion/formulario_solicitante_alimento.html'
    success_url = reverse_lazy('administracion:lista_solicitante_alimentos')

    group_required = ['administrador', 'super usuario']


class ActualizarSolicitanteAlimentoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una SolicitanteAlimento especifica."""

    model = SolicitanteAlimento
    form_class = ActualizarSolicitanteAlimentoForm
    template_name = 'administracion/formulario_solicitante_alimento.html'
    success_url = reverse_lazy('administracion:lista_solicitante_alimentos')

    group_required = ['administrador', 'super usuario']


class ListaGruposView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de Grupos ingresadas en el sistema."""

    model = Grupo
    template_name = 'administracion/lista_grupos.html'

    group_required = ['administrador', 'super usuario']


class CrearGrupoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de Grupos."""

    model = Grupo
    form_class = NuevoGrupoForm
    template_name = 'administracion/formulario_grupo.html'
    success_url = reverse_lazy('administracion:lista_grupos')

    group_required = ['administrador', 'super usuario']


class ActualizarGrupoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una Grupo especifica."""

    model = Grupo
    form_class = ActualizarGrupoForm
    template_name = 'administracion/formulario_grupo.html'
    success_url = reverse_lazy('administracion:lista_grupos')

    group_required = ['administrador', 'super usuario']


class ListaCategoriasView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de Categorias ingresadas en el sistema."""

    model = Categoria
    queryset = Categoria.objects.all().select_related('grupo', 'modificado_por')
    template_name = 'administracion/lista_categorias.html'

    group_required = ['administrador', 'super usuario']


class CrearCategoriaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de Categorias."""

    model = Categoria
    form_class = NuevoCategoriaForm
    template_name = 'administracion/formulario_categoria.html'
    success_url = reverse_lazy('administracion:lista_categorias')

    group_required = ['administrador', 'super usuario']


class ActualizarCategoriaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una Categoria especifica."""

    model = Categoria
    form_class = ActualizarCategoriaForm
    template_name = 'administracion/formulario_categoria.html'
    success_url = reverse_lazy('administracion:lista_categorias')

    group_required = ['administrador', 'super usuario']


class ListaSubcategoriasView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de Subcategorias ingresadas en el sistema."""

    model = Subcategoria
    queryset = Subcategoria.objects.all().select_related('categoria', 'categoria__grupo', 'modificado_por')
    template_name = 'administracion/lista_sub_categorias.html'

    group_required = ['administrador', 'super usuario']


class CrearSubcategoriaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de Subcategorias."""

    model = Subcategoria
    form_class = NuevoSubcategoriaForm
    template_name = 'administracion/formulario_sub_categoria.html'
    success_url = reverse_lazy('administracion:lista_sub_categorias')

    group_required = ['administrador', 'super usuario']


class ActualizarSubcategoriaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una Subcategoria especifica."""

    model = Subcategoria
    form_class = ActualizarSubcategoriaForm
    template_name = 'administracion/formulario_sub_categoria.html'
    success_url = reverse_lazy('administracion:lista_sub_categorias')

    group_required = ['administrador', 'super usuario']


class ListaFabricantesView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de Fabricantes ingresadas en el sistema."""

    model = Fabricante
    template_name = 'administracion/lista_fabricantes.html'

    group_required = ['administrador', 'super usuario']


class CrearFabricanteView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de Fabricantes."""

    model = Fabricante
    form_class = NuevoFabricanteForm
    template_name = 'administracion/formulario_fabricante.html'
    success_url = reverse_lazy('administracion:lista_fabricantes')

    group_required = ['administrador', 'super usuario']


class ActualizarFabricanteView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una Fabricante especifica."""

    model = Fabricante
    form_class = ActualizarFabricanteForm
    template_name = 'administracion/formulario_fabricante.html'
    success_url = reverse_lazy('administracion:lista_fabricantes')

    group_required = ['administrador', 'super usuario']


class ListaDistribuidorsView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de Distribuidors ingresadas en el sistema."""

    model = Distribuidor
    template_name = 'administracion/lista_distribuidors.html'

    group_required = ['administrador', 'super usuario']


class CrearDistribuidorView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de Distribuidors."""

    model = Distribuidor
    form_class = NuevoDistribuidorForm
    template_name = 'administracion/formulario_distribuidor.html'
    success_url = reverse_lazy('administracion:lista_distribuidors')

    group_required = ['administrador', 'super usuario']


class ActualizarDistribuidorView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una Distribuidor especifica."""

    model = Distribuidor
    form_class = ActualizarDistribuidorForm
    template_name = 'administracion/formulario_distribuidor.html'
    success_url = reverse_lazy('administracion:lista_distribuidors')

    group_required = ['administrador', 'super usuario']


class ListaGrupoBebidaAlcoholicasView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de GrupoBebidaAlcoholicas ingresadas en el sistema."""

    model = GrupoBebidaAlcoholica
    template_name = 'administracion/lista_grupo_bebida_alcoholicas.html'

    group_required = ['administrador', 'super usuario']


class CrearGrupoBebidaAlcoholicaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de GrupoBebidaAlcoholicas."""

    model = GrupoBebidaAlcoholica
    form_class = NuevoGrupoBebidaAlcoholicaForm
    template_name = 'administracion/formulario_grupo_bebida_alcoholica.html'
    success_url = reverse_lazy('administracion:lista_grupo_bebida_alcoholicas')

    group_required = ['administrador', 'super usuario']


class ActualizarGrupoBebidaAlcoholicaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una GrupoBebidaAlcoholica especifica."""

    model = GrupoBebidaAlcoholica
    form_class = ActualizarGrupoBebidaAlcoholicaForm
    template_name = 'administracion/formulario_grupo_bebida_alcoholica.html'
    success_url = reverse_lazy('administracion:lista_grupo_bebida_alcoholicas')

    group_required = ['administrador', 'super usuario']


class ListaProductosView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de Productos ingresadas en el sistema."""

    model = Producto
    template_name = 'administracion/lista_productos.html'

    group_required = ['administrador', 'super usuario']


class CrearProductoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de Productos."""

    model = Producto
    form_class = NuevoProductoForm
    template_name = 'administracion/formulario_producto.html'
    success_url = reverse_lazy('administracion:lista_productos')

    group_required = ['administrador', 'super usuario']


class ActualizarProductoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una Producto especifica."""

    model = Producto
    form_class = ActualizarProductoForm
    template_name = 'administracion/formulario_producto.html'
    success_url = reverse_lazy('administracion:lista_productos')

    group_required = ['administrador', 'super usuario']


class ListaDecretosView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de Decretos ingresadas en el sistema."""

    model = Decreto
    template_name = 'administracion/lista_decretos.html'

    group_required = ['administrador', 'super usuario']


class CrearDecretoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de Decretos."""

    model = Decreto
    form_class = NuevoDecretoForm
    template_name = 'administracion/formulario_decreto.html'
    success_url = reverse_lazy('administracion:lista_decretos')

    group_required = ['administrador', 'super usuario']


class ActualizarDecretoView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una Decreto especifica."""

    model = Decreto
    form_class = ActualizarDecretoForm
    template_name = 'administracion/formulario_decreto.html'
    success_url = reverse_lazy('administracion:lista_decretos')

    group_required = ['administrador', 'super usuario']


class ListaTipoEnvaseBebidaAlcoholicasView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de TipoEnvaseBebidaAlcoholicas ingresadas en el sistema."""

    model = TipoEnvaseBebidaAlcoholica
    template_name = 'administracion/lista_tipo_envase_bebida_alcoholicas.html'

    group_required = ['administrador', 'super usuario']


class CrearTipoEnvaseBebidaAlcoholicaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de TipoEnvaseBebidaAlcoholicas."""

    model = TipoEnvaseBebidaAlcoholica
    form_class = NuevoTipoEnvaseBebidaAlcoholicaForm
    template_name = 'administracion/formulario_tipo_envase_bebida_alcoholica.html'
    success_url = reverse_lazy('administracion:lista_tipo_envase_bebida_alcoholicas')

    group_required = ['administrador', 'super usuario']


class ActualizarTipoEnvaseBebidaAlcoholicaView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una TipoEnvaseBebidaAlcoholica especifica."""

    model = TipoEnvaseBebidaAlcoholica
    form_class = ActualizarTipoEnvaseBebidaAlcoholicaForm
    template_name = 'administracion/formulario_tipo_envase_bebida_alcoholica.html'
    success_url = reverse_lazy('administracion:lista_tipo_envase_bebida_alcoholicas')

    group_required = ['administrador', 'super usuario']


class ListaNormatividadsView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """Devuelve una lista de Normatividads ingresadas en el sistema."""

    model = Normatividad
    template_name = 'administracion/lista_normatividads.html'

    group_required = ['administrador', 'super usuario']


class CrearNormatividadView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):
    """Muestra el formulario de creación de Normatividads."""

    model = Normatividad
    form_class = NuevoNormatividadForm
    template_name = 'administracion/formulario_normatividad.html'
    success_url = reverse_lazy('administracion:lista_normatividads')

    group_required = ['administrador', 'super usuario']


class ActualizarNormatividadView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):
    """Muestra el formulario para actualizar una Normatividad especifica."""

    model = Normatividad
    form_class = ActualizarNormatividadForm
    template_name = 'administracion/formulario_normatividad.html'
    success_url = reverse_lazy('administracion:lista_normatividads')

    group_required = ['administrador', 'super usuario']


class ListaUpgdView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    template_name = 'administracion/lista_upgd.html'
    group_required = ['administrador', 'super usuario']
    queryset = covid_models.Upgd.objects.select_related('modificado_por').all()

class CrearUpgdView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = covid_models.Upgd
    form_class = forms.NuevoUpgdForm
    template_name = 'administracion/formulario_upgd.html'
    success_url = reverse_lazy('administracion:lista_upgd')

    group_required = ['administrador', 'super usuario']

class ActualizarUpgdView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = covid_models.Upgd
    form_class = forms.ActualizarUpgdForm
    template_name = 'administracion/formulario_upgd.html'
    success_url = reverse_lazy('administracion:lista_upgd')

    group_required = ['administrador', 'super usuario']


class ListaEapbView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    template_name = 'administracion/lista_eapb.html'
    group_required = ['administrador', 'super usuario']
    queryset = covid_models.Eapb.objects.select_related('modificado_por').all()

class CrearEapbView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = covid_models.Eapb
    form_class = forms.NuevoEapbForm
    template_name = 'administracion/formulario_eapb.html'
    success_url = reverse_lazy('administracion:lista_eapb')

    group_required = ['administrador', 'super usuario']

class ActualizarEapbView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = covid_models.Eapb
    form_class = forms.ActualizarEapbForm
    template_name = 'administracion/formulario_eapb.html'
    success_url = reverse_lazy('administracion:lista_eapb')

    group_required = ['administrador', 'super usuario']


class ListaTipificacionView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    template_name = 'administracion/lista_tipificacion.html'
    group_required = ['administrador', 'super usuario']
    queryset = covid_models.Tipificacion.objects.select_related('modificado_por').all()

class CrearTipificacionView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = covid_models.Tipificacion
    form_class = forms.NuevoTipificacionForm
    template_name = 'administracion/formulario_tipificacion.html'
    success_url = reverse_lazy('administracion:lista_tipificacion')

    group_required = ['administrador', 'super usuario']

class ActualizarTipificacionView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = covid_models.Tipificacion
    form_class = forms.ActualizarTipificacionForm
    template_name = 'administracion/formulario_tipificacion.html'
    success_url = reverse_lazy('administracion:lista_tipificacion')

    group_required = ['administrador', 'super usuario']


class ListaOcupacionView(LoginRequiredMixin, GroupRequiredMixin, ListView):

    template_name = 'administracion/lista_ocupacion.html'
    group_required = ['administrador', 'super usuario']
    queryset = covid_models.Ocupacion.objects.all()

class CrearOcupacionView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, CreateView):

    model = covid_models.Ocupacion
    form_class = forms.NuevoOcupacionForm
    template_name = 'administracion/formulario_ocupacion.html'
    success_url = reverse_lazy('administracion:lista_ocupacion')

    group_required = ['administrador', 'super usuario']

class ActualizarOcupacionView(LoginRequiredMixin, GroupRequiredMixin, UserFormKwargsMixin, UpdateView):

    model = covid_models.Ocupacion
    form_class = forms.ActualizarOcupacionForm
    template_name = 'administracion/formulario_ocupacion.html'
    success_url = reverse_lazy('administracion:lista_ocupacion')

    group_required = ['administrador', 'super usuario']


class ConfigGeneralView(LoginRequiredMixin, GroupRequiredMixin, generic.FormView):

    form_class = forms.ConfigGeneralForm
    template_name = 'administracion/config_general.html'
    success_url = reverse_lazy('administracion:config_general')

    group_required = ['administrador', 'super usuario']

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

import datetime

from django.http.response import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.db.models import Count, Q, Case, When, Value, F, Prefetch, Exists, OuterRef
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.generics import RetrieveAPIView, ListAPIView
from django.forms.models import modelformset_factory
from django.template.loader import render_to_string
from django.contrib.auth.models import Group
from django.db.models.query import Prefetch
from django.template import RequestContext
from rest_framework import permissions
from datetime import timedelta, date
from django.contrib import messages
from django.core import serializers
from django.db import transaction
from django.utils import timezone
from django.views import generic
from django.urls import reverse
from weasyprint import HTML

from common.decorators import grupo_requerido
from administracion.models import Empleado
from .funciones import organiza_areas
from .forms import MulticonsultaForm, RecepcionForm, PacienteForm, InstitucionForm, MuestraClinicaForm
from .forms import EstadoIngresoForm, InformeForm, MuestraEntomologiaForm
from .forms import ResponsableRecoleccionForm, LugarRecoleccionForm, InstitucionCitohistopatologiaForm, BuscadorForm
from .forms import MuestraCitohistopatologiaForm, MuestraBancoSangreForm, InstitucionBancoSangreForm, MuestraEEDDForm
from .forms import InstitucionEEDDForm, InstitucionEEIDForm, MuestraEEIDForm, EstadoIngresoAnalistaForm, ProgramaForm
from .forms import ObservacionSemaforoForm, ResultadoPruebaAnalisisForm, ComentarioRecepcionistaForm, fechaRangoForm
from .forms import ActualizarRecepcionForm, MuestraForm, UsuarioForm, MotivoRechazoForm
from .forms import FormularioAgregarPruebas, RegistroTemperaturaAreaForm, AreaTemperaturaForm
from .models import Prueba, Paciente, Municipio, Institucion, Recepcion, PruebasRealizadas, Agua, Epsa, Poblado, Reporte
from .models import Muestra, Programa, CodigoPunto, Area, RegistroTemperaturaArea
from .serializers import PacienteSerializer, CodigoPuntoSerializer, EpsaSerializer, MunicipioSerializer
from .serializers import PobladoSerializer, PruebaSerializer, AreaSerializer
from bebidas_alcoholicas.forms import MuestraDecretoForm
from .resources import Excel
from . import forms as f
from . import services
from . import models
from . import enums


@login_required
def home(request):
    """Página principal de la aplicación."""

    return render(request, 'trazabilidad/home.html')

@login_required
@permission_required('administracion.can_see_ingresos_recepcionados')
def codigos_muestra_ingreso(request, id):
    """Muestra los codigos de barra para cada muestra según el ingreso."""

    ingreso = Recepcion.objects.prefetch_related('muestras').get(id=id)
    ingreso.crear_codigos_muestra()


    muestra = ingreso.muestras.first()
    pruebas_realizadas = PruebasRealizadas.objects.filter(muestra=muestra).order_by('prueba__area')


    i = 1
    pruebas_total = ""
    for p in pruebas_realizadas:
        if i == 1:
            pruebas_total = pruebas_total + p.prueba.nombre
            i = i + 1
        else:
            pruebas_total = pruebas_total + ', ' + p.prueba.nombre

    return render(request, 'trazabilidad/codigos_muestra.html', {'ingreso': ingreso, 'pruebas_total': pruebas_total})


@login_required
@permission_required('administracion.can_see_ingresos_recepcionados')
def ingresos_recepcionados(request):
    """Permite ver la solicitudes de procesamiento recepcionadas."""

    return render(request, 'trazabilidad/ingresos.html')

@login_required
@permission_required('administracion.can_see_ingresos_recepcionados')
def comentario_recepcionista_view(request, id):
    ingreso = get_object_or_404(models.Ingreso, pk=id)
    form = ComentarioRecepcionistaForm()

    if request.method == 'POST':
        form = ComentarioRecepcionistaForm(instance=ingreso, data=request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'ok': True, 'ingreso': ingreso.id})


    return render(request, 'trazabilidad/form_comentario_recepcionista.html', {
        'form': form,
        'ingreso': ingreso,
    })


@login_required
@permission_required('administracion.can_see_analisis')
def pruebas_analizar(request, id):
    """Permite al analista ver las pruebas que va analizar."""

    ingreso = Recepcion.objects.prefetch_related(
        Prefetch(
            'muestras__pruebasrealizadas_set',
            queryset=PruebasRealizadas.objects.order_by('prueba__area__nombre', 'prueba')
        )
    ).get(id=id)

    form_observacion = ObservacionSemaforoForm()
    return render(request, 'trazabilidad/_pruebas_analizar.html', {'ingreso': ingreso, 'form_observacion': form_observacion})


@login_required
@permission_required('administracion.can_see_analisis')
def detalle_ingreso(request, id):
    """Permite al analista ver el detalle del ingreso."""

    templates = {
        enums.ProgramaEnum.EEID.value: 'trazabilidad/_informacion_ingreso_eeid.html',
        enums.ProgramaEnum.EEDD.value: 'trazabilidad/_informacion_ingreso_eedd.html',
        enums.ProgramaEnum.AGUAS.value: 'trazabilidad/_informacion_ingreso_aguas.html',
        enums.ProgramaEnum.CLINICO.value: 'trazabilidad/_informacion_ingreso_clinico.html',
        enums.ProgramaEnum.COVID19.value: 'trazabilidad/_informacion_ingreso_covid19.html',
        enums.ProgramaEnum.ALIMENTOS.value: 'trazabilidad/_informacion_ingreso_alimentos.html',
        enums.ProgramaEnum.ENTOMOLOGIA.value: 'trazabilidad/_informacion_ingreso_entomologia.html',
        enums.ProgramaEnum.BANCO_SANGRE.value: 'trazabilidad/_informacion_ingreso_banco_sangre.html',
        enums.ProgramaEnum.CITOHISTOPATOLOGIA.value: 'trazabilidad/_informacion_ingreso_citohistopatologia.html',
        enums.ProgramaEnum.BEBIDAS_ALCOHOLICAS.value: 'trazabilidad/_informacion_ingreso_bebidas_alcoholicas.html',
    }

    ingreso = get_object_or_404(Recepcion, pk=id)
    return render(request, 'trazabilidad/_informacion_ingreso.html', {
        'ingreso': ingreso,
        'template_detalle_programa': templates.get(ingreso.programa.codigo, None)
    })


@login_required
@permission_required('administracion.can_see_analisis')
def analisis(request):
    """Permite al analista ingresar la información del analisis."""

    form_estado = EstadoIngresoAnalistaForm()
    return render(request, 'trazabilidad/analisis.html', { 'form_estado': form_estado })

@transaction.atomic
@login_required
@permission_required('administracion.can_see_analisis')
def ingresar_estado_analista(request, id):
    """Permite a un analista aceptar o rechazar una muestra."""

    ingreso = Recepcion.objects.get(pk=id)
    form = EstadoIngresoAnalistaForm(instance=ingreso, data=request.POST)

    if not form.is_valid():
        return render(request, 'trazabilidad/_form_estado_analisis.html', {'form': form})
    
    nuevo = form.save(commit=False)
    nuevo.fecha_estado_analista = timezone.now()
    nuevo.save()

    form.save_m2m()
    return JsonResponse({ 'ok': True, 'aceptado': nuevo.aceptado_analista })


@transaction.atomic
@login_required
@permission_required('administracion.can_see_analisis')
def actualizar_estado(request, id):
    """Permite actualizar el estado de una prueba que se esta realizando a una muestra."""

    prueba = PruebasRealizadas.objects.get(id=id)
    ingreso = prueba.muestra.registro_recepcion

    if request.method == 'GET':
        prueba.actualizar_estado()
        return JsonResponse({ 'ok': True, 'ingreso': ingreso.id })
    
    form_resultado = ResultadoPruebaAnalisisForm(instance=prueba, data=request.POST)

    form_observacion = None
    if prueba.color_semaforo == 'rojo':
        form_observacion = ObservacionSemaforoForm(instance=prueba, data=request.POST)
    
    if form_resultado.is_valid() and (
        form_observacion is None or (
            form_observacion and form_observacion.is_valid()
        )
    ):
        form_resultado.save()
        if form_observacion:
            form_observacion.save()
        
        return JsonResponse({ 'ok': True, 'ingreso': ingreso.id, 'prueba': prueba.id })
        
    return render(request, 'trazabilidad/_form_resultados_prueba.html', {
        'prueba': prueba,
        'ingreso': ingreso,
        'prueba_actualizada': True,
        'form_observacion': form_observacion,
        'form_resultado_actual': form_resultado,
    })

@transaction.atomic
@login_required
@permission_required('administracion.can_see_analisis')
def actualizar_pruebas_muestra(request, id_muestra):
    """Actualiza todas las pruebas dada una muestra."""

    muestra = get_object_or_404(Muestra, id=id_muestra)
    ingreso = muestra.registro_recepcion
    if not ingreso.is_programa_ambientes:
        raise Http404

    for prueba in muestra.pruebasrealizadas_set.all():
        if prueba.estado not in [PruebasRealizadas.ANALISIS, PruebasRealizadas.RESULTADO]:
            prueba.actualizar_estado()
        
    return JsonResponse({ 'ok': True, 'ingreso': ingreso.id })

@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def nueva_muestra_clinica(request):
    """Permite el ingreso de nuevas muestras clinicas."""

    clinicac = True
    if request.method == 'POST':
        confirmar = True
        if 'radicado' in request.POST:
            confirmar = False

        try:
            paciente = Paciente.objects.get(identificacion=int(request.POST['paciente-identificacion']))
            form_paciente = PacienteForm(instance=paciente, data=request.POST, prefix='paciente')
        except:
            form_paciente = PacienteForm(data=request.POST, prefix='paciente')

        form_ingreso = RecepcionForm(user=request.user, data=request.POST, prefix='recepcion')
        form_muestra_clinica = MuestraClinicaForm(confirmar=confirmar, data=request.POST, prefix='clinica')
        form_institucion = InstitucionForm(data=request.POST, prefix='institucion')

        if form_ingreso.is_valid() and form_paciente.is_valid():
            if form_institucion.is_valid() and form_muestra_clinica.is_valid():
                ingreso = form_ingreso.save(commit=False)
                ingreso.recepcionista = request.user
                ingreso.programa = Programa.objects.clinico()
                ingreso.save()

                paciente = form_paciente.save(commit=False)
                paciente.modificado_por = request.user
                paciente.save()
                institucion = form_institucion.save(commit=False)
                institucion.modificado_por = request.user
                institucion.save()

                muestra = form_muestra_clinica.save(commit=False)
                muestra.registro_recepcion = ingreso
                muestra.paciente = paciente

                if institucion.pk is not None:
                    muestra.institucion = institucion
                muestra.save()
                muestra.tipo_muestras.set(form_muestra_clinica.cleaned_data.get('tipo_muestras'))

                for prueba in form_muestra_clinica.cleaned_data['pruebas']:
                    PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)

                return redirect(reverse('trazabilidad:estado_muestra_clinica', args=(ingreso.id,)))
    else:
        form_ingreso = RecepcionForm(user=request.user, prefix='recepcion')
        form_paciente = PacienteForm(prefix='paciente')
        form_institucion = InstitucionForm(prefix='institucion')
        form_muestra_clinica = MuestraClinicaForm(prefix='clinica')

    data = {'form_ingreso': form_ingreso, 'form_paciente': form_paciente, 'form_institucion': form_institucion,
            'form_muestra': form_muestra_clinica, 'muestra_nueva': True, 'clinicac': clinicac}

    return render(request, 'trazabilidad/nueva_muestra_clinica.html', data)

@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def actualizar_muestra_clinica(request, id):
    """Permite actualizar una muestra clinica."""
    clinicac = True
    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()

    if request.method == 'POST':
        confirmar = True
        if 'radicado' in request.POST:
            confirmar = False

        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, data=request.POST, prefix='recepcion')
        form_paciente = PacienteForm(instance=muestra.paciente, data=request.POST, prefix='paciente')
        form_institucion = InstitucionForm(instance=muestra.institucion, data=request.POST, prefix='institucion')
        form_muestra_clinica = MuestraClinicaForm(instance=muestra, confirmar=confirmar, data=request.POST,
                                                  prefix='clinica')

        if form_ingreso.is_valid() and form_paciente.is_valid():
            if form_institucion.is_valid() and form_muestra_clinica.is_valid():
                form_ingreso.save()

                paciente = form_paciente.save(commit=False)
                paciente.modificado_por = request.user
                paciente.save()
                institucion = form_institucion.save()

                muestra = form_muestra_clinica.save(commit=False)
                muestra.paciente = paciente
                muestra.institucion = institucion
                muestra.save()
                muestra.tipo_muestras.set(form_muestra_clinica.cleaned_data.get('tipo_muestras'))

                muestra.pruebas.clear()
                for prueba in form_muestra_clinica.cleaned_data['pruebas']:
                    PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)

                return redirect(reverse('trazabilidad:ingresos'))

    else:
        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, prefix='recepcion')
        form_paciente = PacienteForm(instance=muestra.paciente, prefix='paciente')
        form_institucion = InstitucionForm(instance=muestra.institucion, prefix='institucion')
        form_muestra_clinica = MuestraClinicaForm(instance=muestra, prefix='clinica')

    data = {'form_ingreso': form_ingreso, 'form_paciente': form_paciente, 'form_institucion': form_institucion,
            'form_muestra': form_muestra_clinica, 'muestra_nueva': False, 'clinicac': clinicac}
    return render(request, 'trazabilidad/nueva_muestra_clinica.html', data)

@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def estado_muestra_clinica(request, id):
    """Permite definir el estado de la recepción de una muestra clinica. La muestra puede ser aceptada o rechazada."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra_clinica = ingreso.muestras.first()

    if request.method == 'POST':
        form = EstadoIngresoForm(instance=ingreso, data=request.POST)

        if form.is_valid():
            if 'aceptado' in request.POST:
                estado = Recepcion.ACEPTADO
            else:
                estado = Recepcion.RECHAZADO

            ingreso = form.save()

            return redirect(reverse('trazabilidad:radicado_muestra_clinica', args=(id,)))
    else:
        form = EstadoIngresoForm(instance=ingreso)

    data = {'form': form, 'ingreso': ingreso, 'muestra_clinica': muestra_clinica, 'imprimir': False}
    return render(request, 'trazabilidad/estado_muestra_clinica.html', data)

@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def radicado_muestra_clinica(request, id):
    """Muestra el radicado."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra_clinica = ingreso.muestras.first()

    data = {'ingreso': ingreso, 'muestra_clinica': muestra_clinica, 'imprimir': True}
    return render(request, 'trazabilidad/estado_muestra_clinica.html', data)


@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_ambientes')
def nueva_muestra_agua(request):
    """Permite ingresar una muestra de agua."""

    MuestraAguaFormSet = modelformset_factory(
        models.Agua,
        # extra=0,
        # min_num=1,
        # validate_min=True,
        form=f.MuestraAguaForm,
        formset=f.MuestraAguaFormSet,
    )

    if request.method == 'POST':
        form_ingreso = f.RecepcionForm(user=request.user, data=request.POST, prefix='recepcion')
        form_informacion = f.InformacionAguaForm(data=request.POST, prefix='general')
        formset_muestra_agua = MuestraAguaFormSet(queryset=Agua.objects.none(), data=request.POST)

        if form_ingreso.is_valid() and form_informacion.is_valid() and formset_muestra_agua.is_valid():
            ingreso = form_ingreso.save(commit=False)
            ingreso.recepcionista = request.user
            ingreso.programa = Programa.objects.aguas()
            ingreso.save()

            general = form_informacion.save(request.user)
            formset_muestra_agua.save(user=request.user, ingreso=ingreso, info=general, ingreso_nuevo=True)

            return redirect(reverse('trazabilidad:estado_muestra_agua', args=(ingreso.id,)))
    else:
        form_ingreso = f.RecepcionForm(user=request.user, prefix='recepcion')
        form_informacion = f.InformacionAguaForm(prefix='general')
        formset_muestra_agua = MuestraAguaFormSet(queryset=Agua.objects.none())

    return render(request, 'trazabilidad/form_muestra_agua.html', {
        'muestra_nueva': True,
        'form_ingreso': form_ingreso,
        'form_informacion': form_informacion,
        'formset_muestra_agua': formset_muestra_agua,
    })

@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_ambientes')
def actualizar_muestra_agua(request, id):
    """Permite actualizar una muestra de agua."""

    ingreso = get_object_or_404(models.Recepcion, pk=id)
    muestras = ingreso.muestras.all()
    general = muestras.first().informacion_general

    MuestraAguaFormSet = modelformset_factory(
        models.Agua,
        extra=0,
        min_num=1,
        can_delete=True,
        form=f.MuestraAguaForm,
        formset=f.MuestraAguaFormSet,
    )

    if request.method == 'POST':
        form_ingreso = f.ActualizarRecepcionForm(user=request.user, instance=ingreso, data=request.POST, prefix='recepcion')
        form_informacion = f.InformacionAguaForm(instance=general, data=request.POST, prefix='general')
        formset_muestra_agua = MuestraAguaFormSet(queryset=Agua.objects.filter(id__in=muestras), data=request.POST)

        if form_ingreso.is_valid() and form_informacion.is_valid() and formset_muestra_agua.is_valid():
            ingreso = form_ingreso.save()
            general = form_informacion.save(request.user)
            formset_muestra_agua.save(user=request.user, ingreso=ingreso, info=general, ingreso_nuevo=True)

            return redirect(reverse('trazabilidad:ingresos'))
    else:
        form_ingreso = f.ActualizarRecepcionForm(user=request.user, instance=ingreso, prefix='recepcion')
        form_informacion = f.InformacionAguaForm(instance=general, prefix='general')
        formset_muestra_agua = MuestraAguaFormSet(queryset=models.Agua.objects.filter(id__in=muestras))

    return render(request, 'trazabilidad/form_muestra_agua.html', {
        'muestra_nueva': False,
        'form_ingreso': form_ingreso,
        'form_informacion': form_informacion,
        'formset_muestra_agua': formset_muestra_agua,
    })

@login_required
@permission_required('administracion.can_ingresar_muestras_programas_ambientes')
def estado_muestra_agua(request, id):
    """Permite definir el estado de la recepción de una muestra de agua. La muestra puede ser aceptada o rechazada."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()
    poblado = muestra.informacion_general.poblado

    if request.method == 'POST':
        form = EstadoIngresoForm(instance=ingreso, data=request.POST)

        if form.is_valid():
            if 'aceptado' in request.POST:
                estado = Recepcion.ACEPTADO
            else:
                estado = Recepcion.RECHAZADO

            ingreso = form.save()

            return redirect(reverse('trazabilidad:radicado_muestra_agua', args=(id,)))
    else:
        form = EstadoIngresoForm(instance=ingreso)

    data = {'form': form, 'ingreso': ingreso, 'poblado': poblado, 'imprimir': False}
    return render(request, 'trazabilidad/estado_muestra_agua.html', data)

@login_required
@permission_required('administracion.can_ingresar_muestras_programas_ambientes')
def radicado_muestra_agua(request, id):
    """Muestra el radicado."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()
    poblado = muestra.informacion_general.poblado

    data = {'ingreso': ingreso, 'poblado': poblado, 'imprimir': True}
    return render(request, 'trazabilidad/estado_muestra_agua.html', data)


@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_ambientes')
def nueva_muestra_entomologia(request):
    """Permite agregar una muestra de entomologia."""

    if request.method == 'POST':
        confirmar = True
        if 'radicado' in request.POST:
            confirmar = False

        form_ingreso = RecepcionForm(user=request.user, data=request.POST, prefix='recepcion')
        form_responsable = ResponsableRecoleccionForm(data=request.POST, prefix='responsable')
        form_lugar_recoleccion = LugarRecoleccionForm(data=request.POST, prefix='lugar')
        form_muestra_entomologia = MuestraEntomologiaForm(confirmar=confirmar, data=request.POST, prefix='entomologia')

        if form_ingreso.is_valid() and form_responsable.is_valid() and form_lugar_recoleccion.is_valid():
            if form_muestra_entomologia.is_valid():
                ingreso = form_ingreso.save(commit=False)
                ingreso.recepcionista = request.user
                ingreso.programa = Programa.objects.entomologia()
                ingreso.save()

                responsable = form_responsable.save(commit=False)
                responsable.modificado_por = request.user
                responsable.save()

                lugar = form_lugar_recoleccion.save(commit=False)
                lugar.modificado_por = request.user
                lugar.save()

                muestra = form_muestra_entomologia.save(commit=False)
                muestra.registro_recepcion = ingreso
                muestra.responsable_recoleccion = responsable
                muestra.lugar_recoleccion = lugar
                muestra.save()

                for prueba in form_muestra_entomologia.cleaned_data['pruebas']:
                    PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)

                return redirect(reverse('trazabilidad:estado_muestra_entomologia', args=(ingreso.id,)))
    else:
        form_ingreso = RecepcionForm(user=request.user, prefix='recepcion')
        form_responsable = ResponsableRecoleccionForm(prefix='responsable')
        form_lugar_recoleccion = LugarRecoleccionForm(prefix='lugar')
        form_muestra_entomologia = MuestraEntomologiaForm(prefix='entomologia')

    data = {'form_ingreso': form_ingreso, 'form_muestra': form_muestra_entomologia,
            'form_responsable': form_responsable, 'form_lugar': form_lugar_recoleccion, 'muestra_nueva': True}
    return render(request, 'trazabilidad/nueva_muestra_entomologia.html', data)

@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_ambientes')
def actualizar_muestra_entomologia(request, id):
    """Permite actualizar una muestra de entomologia."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()

    if request.method == 'POST':
        confirmar = True
        if 'radicado' in request.POST:
            confirmar = False

        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, data=request.POST, prefix='recepcion')
        form_responsable = ResponsableRecoleccionForm(instance=muestra.responsable_recoleccion, data=request.POST,
                                                      prefix='responsable')
        form_lugar_recoleccion = LugarRecoleccionForm(instance=muestra.lugar_recoleccion, data=request.POST,
                                                      prefix='lugar')
        form_muestra_entomologia = MuestraEntomologiaForm(instance=muestra, confirmar=confirmar, data=request.POST,
                                                          prefix='entomologia')

        if form_ingreso.is_valid() and form_responsable.is_valid() and form_lugar_recoleccion.is_valid():
            if form_muestra_entomologia.is_valid():
                form_ingreso.save()

                responsable = form_responsable.save()
                lugar = form_lugar_recoleccion.save()

                muestra = form_muestra_entomologia.save(commit=False)
                muestra.responsable_recoleccion = responsable
                muestra.lugar_recoleccion = lugar
                muestra.save()

                muestra.pruebas.clear()
                for prueba in form_muestra_entomologia.cleaned_data['pruebas']:
                    PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)

                return redirect(reverse('trazabilidad:ingresos'))
    else:
        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, prefix='recepcion')
        form_responsable = ResponsableRecoleccionForm(instance=muestra.responsable_recoleccion, prefix='responsable')
        form_lugar_recoleccion = LugarRecoleccionForm(instance=muestra.lugar_recoleccion, prefix='lugar')
        form_muestra_entomologia = MuestraEntomologiaForm(instance=muestra, prefix='entomologia')

    data = {'form_ingreso': form_ingreso, 'form_muestra': form_muestra_entomologia,
            'form_responsable': form_responsable, 'form_lugar': form_lugar_recoleccion, 'muestra_nueva': False}
    return render(request, 'trazabilidad/nueva_muestra_entomologia.html', data)

@login_required
@permission_required('administracion.can_ingresar_muestras_programas_ambientes')
def estado_muestra_entomologia(request, id):
    """Permite definir el estado de la recepción de una muestra de entomologia. La muestra puede ser aceptada
    o rechazada."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()

    if request.method == 'POST':
        form = EstadoIngresoForm(instance=ingreso, data=request.POST)

        if form.is_valid():
            if 'aceptado' in request.POST:
                estado = Recepcion.ACEPTADO
            else:
                estado = Recepcion.RECHAZADO

            ingreso = form.save()

            return redirect(reverse('trazabilidad:radicado_muestra_entomologia', args=(id,)))
    else:
        form = EstadoIngresoForm(instance=ingreso)

    data = {'form': form, 'ingreso': ingreso, 'muestra_entomologia': muestra, 'imprimir': False}
    return render(request, 'trazabilidad/estado_muestra_entomologia.html', data)

@login_required
@permission_required('administracion.can_ingresar_muestras_programas_ambientes')
def radicado_muestra_entomologia(request, id):
    """Muestra el radicado."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()

    data = {'ingreso': ingreso, 'muestra_entomologia': muestra, 'imprimir': True}
    return render(request, 'trazabilidad/estado_muestra_entomologia.html', data)


@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def nueva_muestra_citohistopatologia(request):
    """Permite agregar una muestra de citohistopatologia."""

    if request.method == 'POST':
        confirmar = True
        if 'radicado' in request.POST:
            confirmar = False

        try:
            paciente = Paciente.objects.get(identificacion=int(request.POST['paciente-identificacion']))
            form_paciente = PacienteForm(instance=paciente, data=request.POST, prefix='paciente')
        except:
            form_paciente = PacienteForm(data=request.POST, prefix='paciente')

        form_ingreso = RecepcionForm(user=request.user, data=request.POST, prefix='recepcion')
        form_institucion = InstitucionCitohistopatologiaForm(data=request.POST, prefix='institucion')
        form_muestra_citohistopatologia = MuestraCitohistopatologiaForm(confirmar=confirmar, data=request.POST,
                                                                        prefix='citohistopatologia')

        if form_ingreso.is_valid() and form_paciente.is_valid() and form_institucion.is_valid():
            if form_muestra_citohistopatologia.is_valid():
                ingreso = form_ingreso.save(commit=False)
                ingreso.recepcionista = request.user
                ingreso.programa = Programa.objects.citohistopatologia()
                ingreso.save()

                paciente = form_paciente.save(commit=False)
                paciente.modificado_por = request.user
                paciente.save()

                institucion = form_institucion.save(commit=False)
                institucion.modificado_por = request.user
                institucion.save()

                muestra = form_muestra_citohistopatologia.save(commit=False)
                muestra.registro_recepcion = ingreso
                muestra.paciente = paciente
                muestra.institucion = institucion
                muestra.save()

                for prueba in form_muestra_citohistopatologia.cleaned_data['pruebas']:
                    PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)

                return redirect(reverse('trazabilidad:estado_muestra_citohistopatologia', args=(ingreso.id,)))
    else:
        form_ingreso = RecepcionForm(user=request.user, prefix='recepcion')
        form_paciente = PacienteForm(prefix='paciente')
        form_institucion = InstitucionCitohistopatologiaForm(prefix='institucion')
        form_muestra_citohistopatologia = MuestraCitohistopatologiaForm(prefix='citohistopatologia')

    data = {'form_ingreso': form_ingreso, 'form_muestra': form_muestra_citohistopatologia,
            'form_paciente': form_paciente, 'form_institucion': form_institucion, 'muestra_nueva': True}
    return render(request, 'trazabilidad/nueva_muestra_citohistopatologia.html', data)

@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def actualizar_muestra_citohistopatologia(request, id):
    """Permite actualizar una muestra de citohistopatologia."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()

    if request.method == 'POST':
        confirmar = True
        if 'radicado' in request.POST:
            confirmar = False

        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, data=request.POST, prefix='recepcion')
        form_paciente = PacienteForm(instance=muestra.paciente, data=request.POST, prefix='paciente')
        form_institucion = InstitucionCitohistopatologiaForm(instance=muestra.institucion, data=request.POST,
                                                             prefix='institucion')
        form_muestra_citohistopatologia = MuestraCitohistopatologiaForm(instance=muestra, confirmar=confirmar,
                                                                        data=request.POST, prefix='citohistopatologia')

        if form_ingreso.is_valid() and form_paciente.is_valid() and form_institucion.is_valid():
            if form_muestra_citohistopatologia.is_valid():
                form_ingreso.save()
                paciente = form_paciente.save()
                institucion = form_institucion.save()

                muestra = form_muestra_citohistopatologia.save(commit=False)
                muestra.paciente = paciente
                muestra.institucion = institucion
                muestra.save()

                muestra.pruebas.clear()
                for prueba in form_muestra_citohistopatologia.cleaned_data['pruebas']:
                    PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)

                return redirect(reverse('trazabilidad:ingresos'))
    else:
        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, prefix='recepcion')
        form_paciente = PacienteForm(instance=muestra.paciente, prefix='paciente')
        form_institucion = InstitucionCitohistopatologiaForm(instance=muestra.institucion, prefix='institucion')
        form_muestra_citohistopatologia = MuestraCitohistopatologiaForm(instance=muestra, prefix='citohistopatologia')

    data = {'form_ingreso': form_ingreso, 'form_muestra': form_muestra_citohistopatologia,
            'form_paciente': form_paciente, 'form_institucion': form_institucion, 'muestra_nueva': False}
    return render(request, 'trazabilidad/nueva_muestra_citohistopatologia.html', data)

@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def estado_muestra_citohistopatologia(request, id):
    """Permite definir el estado de la recepción de una muestra de citohistopatologia. La muestra puede ser aceptada
    o rechazada."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()

    if request.method == 'POST':
        form = EstadoIngresoForm(instance=ingreso, data=request.POST)

        if form.is_valid():
            if 'aceptado' in request.POST:
                estado = Recepcion.ACEPTADO
            else:
                estado = Recepcion.RECHAZADO

            ingreso = form.save()

            return redirect(reverse('trazabilidad:radicado_muestra_citohistopatologia', args=(id,)))
    else:
        form = EstadoIngresoForm(instance=ingreso)

    data = {'form': form, 'ingreso': ingreso, 'muestra': muestra, 'imprimir': False}
    return render(request, 'trazabilidad/estado_muestra_citohistopatologia.html', data)


@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def radicado_muestra_citohistopatologia(request, id):
    """Muestra el radicado."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()

    data = {'ingreso': ingreso, 'muestra': muestra, 'imprimir': True}
    return render(request, 'trazabilidad/estado_muestra_citohistopatologia.html', data)

@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def nueva_muestra_banco_sangre(request):
    """Permite agregar una muestra de banco de sangre."""

    if request.method == 'POST':
        confirmar = True
        if 'radicado' in request.POST:
            confirmar = False

        try:
            paciente = Paciente.objects.get(identificacion=int(request.POST['paciente-identificacion']))
            form_paciente = PacienteForm(instance=paciente, data=request.POST, prefix='paciente')
        except:
            form_paciente = PacienteForm(data=request.POST, prefix='paciente')

        form_ingreso = RecepcionForm(user=request.user, data=request.POST, prefix='recepcion')
        form_institucion = InstitucionBancoSangreForm(data=request.POST, prefix='institucion')
        form_muestra_banco_sangre = MuestraBancoSangreForm(confirmar=confirmar, data=request.POST,
                                                           prefix='banco_sangre')

        if form_ingreso.is_valid() and form_paciente.is_valid() and form_institucion.is_valid():
            if form_muestra_banco_sangre.is_valid():
                ingreso = form_ingreso.save(commit=False)
                ingreso.recepcionista = request.user
                ingreso.programa = Programa.objects.banco_sangre()
                ingreso.save()

                paciente = form_paciente.save(commit=False)
                paciente.modificado_por = request.user
                paciente.save()

                institucion = form_institucion.save(commit=False)
                institucion.modificado_por = request.user
                institucion.save()

                muestra = form_muestra_banco_sangre.save(commit=False)
                muestra.registro_recepcion = ingreso
                muestra.paciente = paciente
                muestra.institucion = institucion
                muestra.save()

                for prueba in form_muestra_banco_sangre.cleaned_data['pruebas']:
                    PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)

                return redirect(reverse('trazabilidad:estado_muestra_banco_sangre', args=(ingreso.id,)))
    else:
        form_ingreso = RecepcionForm(user=request.user, prefix='recepcion')
        form_paciente = PacienteForm(prefix='paciente')
        form_institucion = InstitucionBancoSangreForm(prefix='institucion')
        form_muestra_banco_sangre = MuestraBancoSangreForm(prefix='banco_sangre')

    data = {'form_ingreso': form_ingreso, 'form_muestra': form_muestra_banco_sangre,
            'form_paciente': form_paciente, 'form_institucion': form_institucion, 'muestra_nueva': True}
    return render(request, 'trazabilidad/nueva_muestra_banco_sangre.html', data)

@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def actualizar_muestra_banco_sangre(request, id):
    """Permite actualizar una muestra de banco de sangre."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()

    if request.method == 'POST':
        confirmar = True
        if 'radicado' in request.POST:
            confirmar = False

        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, data=request.POST, prefix='recepcion')
        form_paciente = PacienteForm(instance=muestra.paciente, data=request.POST, prefix='paciente')
        form_institucion = InstitucionBancoSangreForm(instance=muestra.institucion, data=request.POST,
                                                      prefix='institucion')
        form_muestra_banco_sangre = MuestraBancoSangreForm(instance=muestra, confirmar=confirmar, data=request.POST,
                                                           prefix='banco_sangre')

        if form_ingreso.is_valid() and form_paciente.is_valid() and form_institucion.is_valid():
            if form_muestra_banco_sangre.is_valid():
                form_ingreso.save()
                paciente = form_paciente.save()
                institucion = form_institucion.save()

                muestra = form_muestra_banco_sangre.save(commit=False)
                muestra.paciente = paciente
                muestra.institucion = institucion
                muestra.save()

                muestra.pruebas.clear()
                for prueba in form_muestra_banco_sangre.cleaned_data['pruebas']:
                    PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)

                return redirect(reverse('trazabilidad:ingresos'))
    else:
        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, prefix='recepcion')
        form_paciente = PacienteForm(instance=muestra.paciente, prefix='paciente')
        form_institucion = InstitucionBancoSangreForm(instance=muestra.institucion, prefix='institucion')
        form_muestra_banco_sangre = MuestraBancoSangreForm(instance=muestra, prefix='banco_sangre')

    data = {'form_ingreso': form_ingreso, 'form_muestra': form_muestra_banco_sangre,
            'form_paciente': form_paciente, 'form_institucion': form_institucion, 'muestra_nueva': False}
    return render(request, 'trazabilidad/nueva_muestra_banco_sangre.html', data)

@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def estado_muestra_banco_sangre(request, id):
    """Permite definir el estado de la recepción de una muestra de banco de sangre. La muestra puede ser aceptada
    o rechazada."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()

    if request.method == 'POST':
        form = EstadoIngresoForm(instance=ingreso, data=request.POST)

        if form.is_valid():
            if 'aceptado' in request.POST:
                estado = Recepcion.ACEPTADO
            else:
                estado = Recepcion.RECHAZADO

            ingreso = form.save()

            return redirect(reverse('trazabilidad:radicado_muestra_banco_sangre', args=(id,)))
    else:
        form = EstadoIngresoForm(instance=ingreso)

    data = {'form': form, 'ingreso': ingreso, 'muestra': muestra, 'imprimir': False}
    return render(request, 'trazabilidad/estado_muestra_banco_sangre.html', data)


@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def radicado_muestra_banco_sangre(request, id):
    """Muestra el radicado."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()

    data = {'ingreso': ingreso, 'muestra': muestra, 'imprimir': True}
    return render(request, 'trazabilidad/estado_muestra_banco_sangre.html', data)


@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def nueva_muestra_eedd(request):
    """Permite agregar una muestra de evaluación externa de desempeño directo."""

    if request.method == 'POST':
        confirmar = True
        if 'radicado' in request.POST:
            confirmar = False

        form_ingreso = RecepcionForm(user=request.user, data=request.POST, prefix='recepcion')
        form_institucion = InstitucionEEDDForm(data=request.POST, prefix='institucion')
        form_muestra = MuestraEEDDForm(confirmar=confirmar, data=request.POST, prefix='eedd')

        if form_ingreso.is_valid() and form_institucion.is_valid():
            if form_muestra.is_valid():
                ingreso = form_ingreso.save(commit=False)
                ingreso.recepcionista = request.user
                ingreso.programa = Programa.objects.eedd()
                ingreso.save()

                institucion = form_institucion.save(commit=False)
                institucion.modificado_por = request.user
                institucion.save()

                muestra = form_muestra.save(commit=False)
                muestra.registro_recepcion = ingreso
                muestra.institucion = institucion
                muestra.save()

                for prueba in form_muestra.cleaned_data['pruebas']:
                    PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)

                return redirect(reverse('trazabilidad:estado_muestra_eedd', args=(ingreso.id,)))
    else:
        form_muestra = MuestraEEDDForm(prefix='eedd')
        form_ingreso = RecepcionForm(user=request.user, prefix='recepcion')
        form_institucion = InstitucionEEDDForm(prefix='institucion')

    data = {'form_ingreso': form_ingreso, 'form_muestra': form_muestra, 'form_institucion': form_institucion,
            'muestra_nueva': True}
    return render(request, 'trazabilidad/nueva_muestra_eedd.html', data)

@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def actualizar_muestra_eedd(request, id):
    """Permite actualizar una muestra de evaluación externa de desempeño directo."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()

    if request.method == 'POST':
        confirmar = True
        if 'radicado' in request.POST:
            confirmar = False

        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, data=request.POST, prefix='recepcion')
        form_institucion = InstitucionEEDDForm(instance=muestra.institucion, data=request.POST,
                                               prefix='institucion')
        form_muestra = MuestraEEDDForm(instance=muestra, confirmar=confirmar, data=request.POST,
                                       prefix='eedd')

        if form_ingreso.is_valid() and form_institucion.is_valid():
            if form_muestra.is_valid():
                form_ingreso.save()
                institucion = form_institucion.save()

                muestra = form_muestra.save(commit=False)
                muestra.institucion = institucion
                muestra.save()

                muestra.pruebas.clear()
                for prueba in form_muestra.cleaned_data['pruebas']:
                    PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)

                return redirect(reverse('trazabilidad:ingresos'))
    else:
        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, prefix='recepcion')
        form_institucion = InstitucionEEDDForm(instance=muestra.institucion, prefix='institucion')
        form_muestra = MuestraEEDDForm(instance=muestra, prefix='eedd')

    data = {'form_ingreso': form_ingreso, 'form_muestra': form_muestra, 'form_institucion': form_institucion,
            'muestra_nueva': False}
    return render(request, 'trazabilidad/nueva_muestra_eedd.html', data)

@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def estado_muestra_eedd(request, id):
    """Permite definir el estado de la recepción de una muestra de evaluación externa de desempeño directo. La muestra
     puede ser aceptada o rechazada."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()

    if request.method == 'POST':
        form = EstadoIngresoForm(instance=ingreso, data=request.POST)

        if form.is_valid():
            if 'aceptado' in request.POST:
                estado = Recepcion.ACEPTADO
            else:
                estado = Recepcion.RECHAZADO

            ingreso = form.save()

            return redirect(reverse('trazabilidad:radicado_muestra_eedd', args=(id,)))
    else:
        form = EstadoIngresoForm(instance=ingreso)

    data = {'form': form, 'ingreso': ingreso, 'muestra': muestra, 'imprimir': False}
    return render(request, 'trazabilidad/estado_muestra_eedd.html', data)

@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def radicado_muestra_eedd(request, id):
    """Muestra el radicado."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()

    data = {'ingreso': ingreso, 'muestra': muestra, 'imprimir': True}
    return render(request, 'trazabilidad/estado_muestra_eedd.html', data)


@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def nueva_muestra_eeid(request):
    """Permite agregar una muestra de evaluación externa de desempeño indirecto."""

    if request.method == 'POST':
        confirmar = True
        if 'radicado' in request.POST:
            confirmar = False

        form_ingreso = RecepcionForm(user=request.user, data=request.POST, prefix='recepcion')
        form_institucion = InstitucionEEIDForm(data=request.POST, prefix='institucion')
        form_muestra = MuestraEEIDForm(confirmar=confirmar, data=request.POST, prefix='eeid')

        if form_ingreso.is_valid() and form_institucion.is_valid():
            if form_muestra.is_valid():
                ingreso = form_ingreso.save(commit=False)
                ingreso.recepcionista = request.user
                ingreso.programa = Programa.objects.eeid()
                ingreso.save()

                institucion = form_institucion.save(commit=False)
                institucion.modificado_por = request.user
                institucion.save()

                muestra = form_muestra.save(commit=False)
                muestra.registro_recepcion = ingreso
                muestra.institucion = institucion
                muestra.save()

                for prueba in form_muestra.cleaned_data['pruebas']:
                    PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)

                return redirect(reverse('trazabilidad:estado_muestra_eeid', args=(ingreso.id,)))
    else:
        form_muestra = MuestraEEIDForm(prefix='eeid')
        form_ingreso = RecepcionForm(user=request.user, prefix='recepcion')
        form_institucion = InstitucionEEIDForm(prefix='institucion')

    data = {'form_ingreso': form_ingreso, 'form_muestra': form_muestra, 'form_institucion': form_institucion,
            'muestra_nueva': True}
    return render(request, 'trazabilidad/nueva_muestra_eeid.html', data)

@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def actualizar_muestra_eeid(request, id):
    """Permite actualizar una muestra de evaluación externa de desempeño indirecto."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()

    if request.method == 'POST':
        confirmar = True
        if 'radicado' in request.POST:
            confirmar = False

        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, data=request.POST, prefix='recepcion')
        form_institucion = InstitucionEEIDForm(instance=muestra.institucion, data=request.POST,
                                               prefix='institucion')
        form_muestra = MuestraEEIDForm(instance=muestra, confirmar=confirmar, data=request.POST,
                                       prefix='eedd')

        if form_ingreso.is_valid() and form_institucion.is_valid():
            if form_muestra.is_valid():
                form_ingreso.save()
                institucion = form_institucion.save()

                muestra = form_muestra.save(commit=False)
                muestra.institucion = institucion
                muestra.save()

                muestra.pruebas.clear()
                for prueba in form_muestra.cleaned_data['pruebas']:
                    PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)

                return redirect(reverse('trazabilidad:ingresos'))
    else:
        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, prefix='recepcion')
        form_institucion = InstitucionEEIDForm(instance=muestra.institucion, prefix='institucion')
        form_muestra = MuestraEEIDForm(instance=muestra, prefix='eedd')

    data = {'form_ingreso': form_ingreso, 'form_muestra': form_muestra, 'form_institucion': form_institucion,
            'muestra_nueva': False}
    return render(request, 'trazabilidad/nueva_muestra_eeid.html', data)

@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def estado_muestra_eeid(request, id):
    """Permite definir el estado de la recepción de una muestra de evaluación externa de desempeño indirecto. La muestra
     puede ser aceptada o rechazada."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()

    if request.method == 'POST':
        form = EstadoIngresoForm(instance=ingreso, data=request.POST)

        if form.is_valid():
            if 'aceptado' in request.POST:
                estado = Recepcion.ACEPTADO
            else:
                estado = Recepcion.RECHAZADO

            ingreso = form.save()

            return redirect(reverse('trazabilidad:radicado_muestra_eeid', args=(id,)))
    else:
        form = EstadoIngresoForm(instance=ingreso)

    data = {'form': form, 'ingreso': ingreso, 'muestra': muestra, 'imprimir': False}
    return render(request, 'trazabilidad/estado_muestra_eeid.html', data)

@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def radicado_muestra_eeid(request, id):
    """Muestra el radicado."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()

    data = {'ingreso': ingreso, 'muestra': muestra, 'imprimir': True}
    return render(request, 'trazabilidad/estado_muestra_eeid.html', data)


@login_required
def get_municipios_hermanos_json(request, id_municipio):
    """Devuelve los municipios que pertenecen al mismo departamento del municipio especificado en formato JSON."""

    municipio = Municipio.objects.get(pk=id_municipio)
    municipios = Municipio.objects.filter(departamento=municipio.departamento)
    json_municipios = serializers.serialize('json', municipios)
    return HttpResponse(json_municipios, content_type='application/json')

# Json views


class DetallePacienteView(RetrieveAPIView):
    """Devuelve un paciente en formato JSON según su identificación."""

    lookup_url_kwarg = 'id'
    lookup_field = 'identificacion'
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [permissions.IsAuthenticated]


class DetalleCodigoPuntoView(RetrieveAPIView):
    """Devuelve la información del un punto de recolección de muestras de agua en formato JSON según el id del codigo
    del punto."""

    queryset = CodigoPunto.objects.all()
    serializer_class = CodigoPuntoSerializer
    permission_classes = [permissions.IsAuthenticated]


class PobladoDetalleEpsaView(RetrieveAPIView):
    """Devuelve una epsa en formato JSON según el poblado."""

    lookup_url_kwarg = 'pk'
    lookup_field = 'poblados'
    queryset = Epsa.objects.all()
    serializer_class = EpsaSerializer
    permission_classes = [permissions.IsAuthenticated]


class ListaMunicipiosDepartamentoView(ListAPIView):
    """Devuelve los municipios de un departamento en formato JSON."""

    serializer_class = MunicipioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retorna los municipios del departamento especificado en la URL."""

        departamento = self.kwargs['pk']
        return Municipio.objects.filter(departamento=departamento)


class ListaPobladosMunicipioView(ListAPIView):
    """Devuelve los poblados de un municipio en formato JSON."""

    serializer_class = PobladoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retorna los poblados del municipio especificado en la URL."""

        municipio = self.kwargs['pk']
        return Poblado.objects.filter(municipio=municipio)


class ListaCodigosPuntoPobladoView(ListAPIView):
    """Devuelve los codigos de punto de recolección de muestras de agua en formato JSON según el poblado."""

    serializer_class = CodigoPuntoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retorna los codigos de punto del poblado especificado en la URL."""

        poblado = self.kwargs['pk']
        return CodigoPunto.objects.filter(poblado=poblado)


class ListaPruebasAreaView(ListAPIView):
    """Devuelve las pruebas de un área en formato JSON."""

    serializer_class = PruebaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retorna las pruebas del área especificada en la URL."""

        area = self.kwargs['pk']
        return Prueba.objects.filter(area=area).activos()


class ListaPruebasProgramaView(ListAPIView):
    """Devuelve las pruebas de un programa en formato JSON."""

    serializer_class = PruebaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retorna las pruebas del programa especificado en la URL."""

        programa = self.kwargs['pk']
        return Prueba.objects.filter(area__programa=programa)


class ListaProgramaAreasView(ListAPIView):
    """Devuelve las pruebas de un programa en formato JSON."""

    serializer_class = AreaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retorna las pruebas del programa especificado en la URL."""

        programa = self.kwargs['pk']
        return Area.objects.filter(programa=programa)

@transaction.atomic
@login_required
@permission_required('trazabilidad.can_generar_informe')
def informe_nuevo(request, id_recepcion):
    """Permite la creación de Informes a partir de la tabla de Analisis."""
    exito = request.session.pop('ok', False)
    ingreso = get_object_or_404(Recepcion, pk=id_recepcion)
    informe = ingreso.informe
    confirmar = bool(informe)
    confirmado = informe and informe.confirmado
    programa = ingreso.programa
    MuestraFormSet = modelformset_factory(Muestra, form=MuestraForm, extra=0)
    en_curso = ingreso.muestras.non_polymorphic().all().prefetch_related(Prefetch('pruebasrealizadas_set', queryset=PruebasRealizadas.objects.order_by('prueba__area', 'prueba')))
    if request.method == 'POST':
        formset_muestra = MuestraFormSet(queryset=en_curso, data=request.POST)
        form_informe = InformeForm(ingreso=ingreso, user=request.user, data=request.POST)
        if form_informe.is_valid() and formset_muestra.is_valid():
            informe = form_informe.save()
            formset_muestra.save()
            if informe.confirmado:
                url = 'trazabilidad:informe_documento'
            else:
                request.session['ok'] = True
                url = 'trazabilidad:informe_nuevo'
            return redirect(reverse(url, kwargs={'id_recepcion': ingreso.id}))
    else:
        form_informe = InformeForm(ingreso=ingreso, user=request.user)
        formset_muestra = MuestraFormSet(queryset=en_curso)

    return render(request, 'trazabilidad/nuevo_informe.html', {
        'exito': exito,
        'recepcion': ingreso,
        'programa': programa,
        'confirmar': confirmar,
        'confirmado': confirmado,
        'form_informe': form_informe,
        'formset_muestra': formset_muestra,
    })


@login_required
@permission_required('trazabilidad.can_see_informe_resultados')
def informe_documento(request, id_recepcion):
    """Muestra el documento del reporte final."""

    query = (
        Recepcion.objects
            .prefetch_related('reportes')
            .select_related('programa', 'analista__empleado', 'responsable_tecnico__empleado')
            .all()
    )
    ingreso = get_object_or_404(query, pk=id_recepcion)
    
    data = services.data_informe_resultados(ingreso)
    if request.method == 'POST' and 'imprimir' in request.POST:
        http_response = HttpResponse(content_type='application/pdf')
        http_response['Content-Disposition'] = f'attachment; filename={ingreso.radicado}.pdf'
        
        services.generate_results_pdf(request, data, target=http_response)
        return http_response

    return render(request, 'trazabilidad/reporte.html', data)


@login_required
@permission_required('trazabilidad.can_see_informe_resultados')
def informe_documento_prueba(request, id_muestra, id_prueba):
    muestra = get_object_or_404(Muestra, id=id_muestra)
    prueba_realizada = get_object_or_404(PruebasRealizadas, muestra=muestra, id=id_prueba)
    ingreso = muestra.registro_recepcion
    informe = ingreso.informe

    programa = ingreso.programa.nombre
    fecha_impresion = timezone.now()
    data = {
        'ingreso': ingreso,
        'muestra': muestra,
        'informe': informe,
        'programa': programa,
        'imprimir': False,
        'fecha_impresion': fecha_impresion,
        'prueba_realizada': prueba_realizada,
    }

    if request.method == 'POST':
        if 'imprimir' in request.POST:
            ruta = "static/css/%s.css"
            to_html = render_to_string('trazabilidad/reporte_parcial.html', context=data, request=request)
            http_response = HttpResponse(content_type='application/pdf')
            http_response['Content-Disposition'] = f'attachment; filename={ingreso.radicado}-parcial.pdf'
            HTML(string=to_html).write_pdf(http_response, stylesheets=[ruta % 'estilos', ruta % 'bootstrap.min', ruta % '_informe_nuevo_grande'])
            return http_response
    return render(request, 'trazabilidad/reporte_parcial.html', data)

# Informes Gerenciales

@grupo_requerido('administrador', 'coordinador', 'consultas generales')
def tipo_resultado(request):
    """Reportes por Tipo de Resultados."""
    sw = False
    titulo = "ESTADISTICO DE PRUEBAS POR TIPO DE RESULTADOS"
    enlace = "/reportes/tipo_resultado/"
    if request.method == 'POST':
        fi = request.POST['fechai']
        ff = request.POST['fechaf']
        form = fechaRangoForm(request.POST)
        form_programa = ProgramaForm(request.POST)
        if form.is_valid() and form_programa.is_valid():
            sw = True
            fi_format = datetime.datetime.strptime(fi, '%Y-%m-%d').date()
            ff_format = datetime.datetime.strptime(ff, '%Y-%m-%d').date()
            ff_format = ff_format + timedelta(days=1)
            t_prueba = request.POST['prueba']
            pruebas = PruebasRealizadas.objects.filter(
                fecha_pre_analisis__range=(fi_format, ff_format),
                prueba=t_prueba, estado=PruebasRealizadas.RESULTADO
            ).exclude(resultados=None)
            conteo_resultados = pruebas.values('resultados__nombre').annotate(Count('resultados'))
            total = 0
            acumulado = 0
            lista = []
            grafico = [['Resultado', 'Frecuencia']]
            for p in conteo_resultados:
                total = total + p['resultados__count']
            for p in conteo_resultados:
                detalle = pruebas.filter(resultados__nombre=p['resultados__nombre'])
                porcentaje = (p['resultados__count'] / total) * 100
                lista.append(
                    {'resultado': p['resultados__nombre'],
                     'frecuencia': p['resultados__count'],
                     'porcentaje': porcentaje,
                     'acumulado': acumulado, 'detalle': detalle}
                )
                grafico.append([p['resultados__nombre'], p['resultados__count']])

            newlist = sorted(lista, key=lambda k: k['frecuencia'], reverse=True)
            lista = newlist
            for p in lista:
                porcentaje = p['porcentaje']
                acumulado = acumulado + porcentaje
                p['acumulado'] = acumulado

            if 'excel' in request.POST:
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=reporte.xlsx'
                excel = Excel(data=lista, titulo=titulo, function=tipo_resultado)
                # excel.draw_chart()
                response.write(excel.write())
                return response

            data = {
                'form': form,
                'form_programa': form_programa,
                'lista': lista,
                'grafico': grafico, 'sw': sw,
                'total': total, 'titulo': titulo,
                'enlace': enlace
            }
            return render(request, 'trazabilidad/informe_tipo_resultado.html', data)
    else:
        form = fechaRangoForm()
        form_programa = ProgramaForm()

    data = {'form': form, 'form_programa': form_programa, 'titulo': titulo, 'enlace': enlace}
    return render(request, 'trazabilidad/informe_tipo_resultado.html', data)


@login_required
def get_programaspruebas_json(request, id_programa):
    """Devuelve los municipios de un departamento en formato JSON."""

    programa = Programa.objects.get(pk=id_programa)
    pruebas = Prueba.objects.filter(area__programa=programa)
    json_municipios = serializers.serialize('json', pruebas)
    return HttpResponse(json_municipios, content_type='application/json')


@grupo_requerido('administrador', 'coordinador', 'consultas generales')
def motivo_rechazo(request):
    """Reportes por Motivo de Rechazo."""
    sw = False
    titulo = "ESTADISTICO DE PRUEBAS POR MOTIVO DE RECHAZO"
    enlace = "/reportes/motivo_rechazo/"
    if request.method == 'POST':
        fi = request.POST['fechai']
        ff = request.POST['fechaf']
        form = fechaRangoForm(request.POST)
        form_programa = MotivoRechazoForm(request.POST)
        if form.is_valid() and form_programa.is_valid():
            sw = True
            fi_format = datetime.datetime.strptime(fi, '%Y-%m-%d').date()
            ff_format = datetime.datetime.strptime(ff, '%Y-%m-%d').date()
            ff_format = ff_format + timedelta(days=1)
            t_prueba = request.POST['prueba']
            programa = form_programa.cleaned_data['programa']
            municipio = form_programa.cleaned_data['municipio']

            query = None
            #  Resutados por Recepcionista
            muestras = Muestra.objects.filter(
                registro_recepcion__fecha_radicado__range=(fi_format, ff_format),
                registro_recepcion__estado=Recepcion.RECHAZADO, pruebas=t_prueba
            )

            if programa.codigo == 'clinica':
                query = (Q(clinica__municipio=municipio))
            if programa.codigo == 'aguas':
                query = (Q(agua__codigo_punto__poblado__municipio=municipio))
            if programa.codigo == 'citohistopatologia':
                query = (Q(citohistopatologia__institucion__municipio=municipio))
            if programa.codigo == 'banco_sangre':
                query = (Q(bancosangre__institucion__municipio=municipio))
            if programa.codigo == 'entomologia':
                query = (Q(entomologia__lugar_recoleccion__municipio=municipio))
            if programa.codigo == 'eedd':
                query = (Q(eedd__institucion__municipio=municipio))
            if programa.codigo == 'eeid':
                query = (Q(eeid__institucion__municipio=municipio))

            try:
                muestras = muestras.filter(query)
            except TypeError:
                pass

            conteo_resultados = muestras.values(
                'registro_recepcion__motivo_rechazo__motivo'
            ).order_by('registro_recepcion__motivo_rechazo').annotate(Count('registro_recepcion__motivo_rechazo'))
            total = 0
            acumulado = 0
            lista = []
            grafico = [['Resultado', 'Frecuencia']]
            for p in conteo_resultados:
                total = total + p['registro_recepcion__motivo_rechazo__count']
            for p in conteo_resultados:
                detalle = muestras.filter(
                    registro_recepcion__motivo_rechazo__motivo=p['registro_recepcion__motivo_rechazo__motivo']
                )
                porcentaje = (p['registro_recepcion__motivo_rechazo__count'] / total) * 100
                acumulado = acumulado + porcentaje
                lista.append(
                    {'resultado': p['registro_recepcion__motivo_rechazo__motivo'],
                     'frecuencia': p['registro_recepcion__motivo_rechazo__count'],
                     'porcentaje': porcentaje, 'acumulado': acumulado, 'detalle': detalle}
                )
                grafico.append(
                    [p['registro_recepcion__motivo_rechazo__motivo'],
                     p['registro_recepcion__motivo_rechazo__count']]
                )

            # Resutados por Analista
            muestras_a = Muestra.objects.filter(
                registro_recepcion__fecha_estado_analista__range=(fi_format, ff_format),
                registro_recepcion__estado_analista=Recepcion.RECHAZADO, pruebas=t_prueba
            )
            try:
                muestras_a = muestras_a.filter(query)
            except TypeError:
                pass

            conteo_resultados_a = muestras_a.values(
                'registro_recepcion__motivo_rechazo_analista__motivo'
            ).order_by(
                'registro_recepcion__motivo_rechazo_analista'
            ).annotate(Count('registro_recepcion__motivo_rechazo_analista'))
            total_a = 0
            acumulado = 0
            lista_a = []
            grafico_a = [['Resultado', 'Frecuencia']]
            for p in conteo_resultados_a:
                total_a = total_a + p['registro_recepcion__motivo_rechazo_analista__count']
            for p in conteo_resultados_a:
                detalle = muestras_a.filter(
                    registro_recepcion__motivo_rechazo_analista__motivo=p['registro_recepcion__motivo_rechazo_analista__motivo']
                )
                porcentaje = (p['registro_recepcion__motivo_rechazo_analista__count'] / total_a) * 100
                acumulado = acumulado + porcentaje
                lista_a.append(
                    {'resultado': p['registro_recepcion__motivo_rechazo_analista__motivo'],
                     'frecuencia': p['registro_recepcion__motivo_rechazo_analista__count'],
                     'porcentaje': porcentaje, 'acumulado': acumulado, 'detalle': detalle}
                )
                grafico_a.append(
                    [p['registro_recepcion__motivo_rechazo_analista__motivo'],
                     p['registro_recepcion__motivo_rechazo_analista__count']]
                )

            if 'excel' in request.POST:
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=reporte.xlsx'
                orden = ['MOTIVO RECHAZO', 'FRECUENCIA', 'PORCENTAJE', 'ACUMULADO']
                excel = Excel(titulo=titulo, function=motivo_rechazo, order=orden)
                excel.generar_tabla(data=lista)
                excel.generar_tabla(data=lista_a, _titulo=titulo + ' ANALISTA')
                excel = excel.write()
                response.write(excel)
                return response

            data = {
                'form': form,
                'form_programa': form_programa,
                'lista': lista,
                'grafico': grafico, 'sw': sw,
                'total': total, 'lista_a': lista_a,
                'grafico_a': grafico_a, 'total_a': total_a,
                'titulo': titulo, 'enlace': enlace
            }
            return render(request, 'trazabilidad/informe_motivo_rechazo.html', data)
    else:
        form = fechaRangoForm()
        form_programa = MotivoRechazoForm()

    data = {'form': form, 'form_programa': form_programa, 'titulo': titulo, 'enlace': enlace}
    return render(request, 'trazabilidad/informe_motivo_rechazo.html', data)


@grupo_requerido('administrador', 'coordinador', 'consultas generales')
def muestras_rechazadas(request):
    """Reportes por Muestras Rechazadas."""
    sw = False
    titulo = "ESTADISTICO DE PRUEBAS POR MUESTRAS RECHAZADAS"
    enlace = "/reportes/muestras_rechazadas/"
    if request.method == 'POST':
        fi = request.POST['fechai']
        ff = request.POST['fechaf']
        form = fechaRangoForm(request.POST)
        form_programa = ProgramaForm(request.POST)
        if form.is_valid() and form_programa.is_valid():
            sw = True
            fi_format = datetime.datetime.strptime(fi, '%Y-%m-%d').date()
            ff_format = datetime.datetime.strptime(ff, '%Y-%m-%d').date()
            ff_format = ff_format + timedelta(days=1)
            t_prueba = request.POST['prueba']
            # Aceptadas
            muestras = Muestra.objects.filter(
                registro_recepcion__fecha_radicado__range=(fi_format, ff_format),
                registro_recepcion__estado=Recepcion.ACEPTADO, pruebas=t_prueba
            )
            d_aceptadas = muestras
            r_aceptadas = muestras.values(
                'registro_recepcion__estado'
            ).order_by('registro_recepcion__estado').annotate(Count('registro_recepcion__estado'))
            lista = []
            grafico = [['Resultado', 'Frecuencia']]
            total = 0
            acumulado = 0
            for p in r_aceptadas:
                total = total + p['registro_recepcion__estado__count']
            for p in r_aceptadas:
                porcentaje = 0
                lista.append(
                    {'resultado': 'Aceptadas',
                     'frecuencia': p['registro_recepcion__estado__count'],
                     'porcentaje': porcentaje,
                     'acumulado': acumulado,
                     'detalle': d_aceptadas}
                )
                grafico.append([p['registro_recepcion__estado'], p['registro_recepcion__estado__count']])

            # Resutados por Recepcionista
            muestras = Muestra.objects.filter(
                registro_recepcion__fecha_radicado__range=(fi_format, ff_format),
                registro_recepcion__estado=Recepcion.RECHAZADO, pruebas=t_prueba
            )
            r_rechazadas = muestras.values(
                'registro_recepcion__recepcionista__username').order_by(
                    'registro_recepcion__recepcionista__username'
            ).annotate(Count('registro_recepcion__recepcionista'))

            for p in r_rechazadas:
                total = total + p['registro_recepcion__recepcionista__count']

            for p in r_rechazadas:
                detalle = muestras.filter(
                    registro_recepcion__recepcionista__username=p['registro_recepcion__recepcionista__username']
                )
                porcentaje = 0
                lista.append(
                    {'resultado': p['registro_recepcion__recepcionista__username'],
                     'frecuencia': p['registro_recepcion__recepcionista__count'],
                     'porcentaje': porcentaje, 'acumulado': acumulado, 'detalle': detalle}
                )
                grafico.append(
                    [p['registro_recepcion__recepcionista__username'], p['registro_recepcion__recepcionista__count']]
                )

            # Resutados por Analista
            muestras = Muestra.objects.filter(
                registro_recepcion__fecha_estado_analista__range=(fi_format, ff_format),
                registro_recepcion__estado_analista=Recepcion.RECHAZADO, pruebas=t_prueba
            )
            r_rechazo_analista = muestras.values(
                'registro_recepcion__estado_analista'
            ).order_by('registro_recepcion__estado_analista').annotate(Count('registro_recepcion__estado_analista'))
            d_rechazo_analista = muestras
            for p in r_rechazo_analista:
                total = total + p['registro_recepcion__estado_analista__count']
            for p in r_rechazo_analista:
                porcentaje = 0
                lista.append(
                    {'resultado': 'Rech. Analista',
                     'frecuencia': p['registro_recepcion__estado_analista__count'], 'porcentaje': porcentaje,
                     'acumulado': acumulado, 'detalle': d_rechazo_analista}
                )
                grafico.append(
                    [p['registro_recepcion__estado_analista'], p['registro_recepcion__estado_analista__count']]
                )

            for p in lista:
                porcentaje = (p['frecuencia'] / total) * 100
                acumulado = acumulado + porcentaje
                p['porcentaje'] = porcentaje
                p['acumulado'] = acumulado

            if 'excel' in request.POST:
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=reporte.xlsx'
                order = ['MUESTRAS', 'FRECUENCIA', 'PORCENTAJE', 'ACUMULADO']
                excel = Excel(data=lista, titulo=titulo, function=muestras_rechazadas, order=order).write()
                response.write(excel)
                return response

            data = {
                'form': form,
                'form_programa': form_programa,
                'lista': lista, 'grafico': grafico,
                'sw': sw, 'total': total,
                'titulo': titulo, 'enlace': enlace
            }
            return render(request, 'trazabilidad/informe_muestras_rechazadas.html', data)
    else:
        form = fechaRangoForm()
        form_programa = ProgramaForm()

    data = {'form': form, 'form_programa': form_programa, 'titulo': titulo, 'enlace': enlace}
    return render(request, 'trazabilidad/informe_muestras_rechazadas.html', data)


@grupo_requerido('administrador', 'coordinador', 'consultas generales')
def cumplimiento_productividad(request):
    """Reportes por Cumplimiento y Productividad."""

    sw = False
    titulo = "ESTADISTICO DE CUMPLIMIENTO Y PRODUCTIVIDAD"
    enlace = "/reportes/cumplimiento_productividad/"
    if request.method == 'POST':
        fi = request.POST['fechai']
        ff = request.POST['fechaf']
        form = fechaRangoForm(request.POST)
        form_programa = ProgramaForm(request.POST)
        form_usuario = UsuarioForm(request.POST)
        if form.is_valid() and form_programa.is_valid() and form_usuario.is_valid():
            sw = True
            fi_format = datetime.datetime.strptime(fi, '%Y-%m-%d').date()
            ff_format = datetime.datetime.strptime(ff, '%Y-%m-%d').date()
            ff_format = ff_format + timedelta(days=1)
            t_prueba = request.POST['prueba']
            # pruebas = PruebasRealizadas.objects.filter(ultima_modificacion__range=(fi_format,ff_format), prueba = t_prueba, estado=PruebasRealizadas.RESULTADO).exclude(resultado = None)
            usuario = request.POST['usuario']
            pruebas = PruebasRealizadas.objects.filter(
                ultima_modificacion__range=(fi_format, ff_format),
                prueba=t_prueba,
                estado=PruebasRealizadas.RESULTADO,
                muestra__registro_recepcion__analista=usuario
            ).exclude(resultados=None)
            lista = []
            verde = []
            amarillo = []
            rojo = []
            grafico = [['Resultado', 'Frecuencia']]
            v_total = 0
            a_total = 0
            r_total = 0
            total = 0
            for p in pruebas:
                if p.color_semaforo == 'verde':
                    v_total = v_total + 1
                    verde.append(
                        {'radicado': p.muestra.registro_recepcion.radicado,
                         'recepcion': p.muestra.registro_recepcion.fecha_recepcion,
                         'solicitante': p.muestra.registro_recepcion.solicitante}
                    )
                elif p.color_semaforo == 'amarillo':
                    a_total = a_total + 1
                    amarillo.append(
                        {'radicado': p.muestra.registro_recepcion.radicado,
                         'recepcion': p.muestra.registro_recepcion.fecha_recepcion,
                         'solicitante': p.muestra.registro_recepcion.solicitante}
                    )
                else:
                    r_total = r_total + 1
                    rojo.append(
                        {'radicado': p.muestra.registro_recepcion.radicado,
                         'recepcion': p.muestra.registro_recepcion.fecha_recepcion,
                         'solicitante': p.muestra.registro_recepcion.solicitante}
                    )

            total = v_total + a_total + r_total
            try:
                acumulado = (v_total / total) * 100
            except ZeroDivisionError:
                messages.error(request,"El usuario que ha escogido no tiene ninguna prueba o no hay pruebas dentro del rango de fechas escogido... Intente nuevamente")
                return render(request, 'trazabilidad/informe_cumplimiento_productividad.html', {'form': form, 'form_programa': form_programa, 'form_usuario': form_usuario})
            if v_total != 0:
                lista.append(
                    {'resultado': 'Verde',
                     'frecuencia': v_total,
                     'porcentaje': (v_total / total) * 100,
                     'acumulado': acumulado, 'detalle': verde}
                )
                grafico.append(['Verde', v_total])
            acumulado = acumulado + (a_total / total) * 100
            if a_total != 0:
                lista.append(
                    {'resultado': 'Amarillo',
                     'frecuencia': a_total,
                     'porcentaje': (a_total / total) * 100,
                     'acumulado': acumulado,
                     'detalle': amarillo}
                )
                grafico.append(['Amarillo', a_total])
            acumulado = acumulado + (r_total / total) * 100
            if r_total != 0:
                lista.append(
                    {'resultado': 'Rojo',
                     'frecuencia': r_total,
                     'porcentaje': (r_total / total) * 100,
                     'acumulado': acumulado, 'detalle': rojo}
                )
                grafico.append(['Rojo', r_total])

            if 'excel' in request.POST:
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=reporte.xlsx'
                excel = Excel(data=lista, titulo=titulo, function=cumplimiento_productividad).write()
                response.write(excel)
                return response

            data = {'form': form, 'form_programa': form_programa, 'form_usuario': form_usuario, 'lista': lista, 'grafico': grafico, 'sw': sw, 'total': total, 'titulo': titulo, 'enlace': enlace, 'v_total': v_total, 'a_total': a_total, 'r_total': r_total}
            return render(request, 'trazabilidad/informe_cumplimiento_productividad.html', data)
    else:
        form = fechaRangoForm()
        form_programa = ProgramaForm()
        form_usuario = UsuarioForm()

    data = {'form': form, 'form_programa': form_programa, 'form_usuario': form_usuario, 'titulo': titulo, 'enlace': enlace}
    return render(request, 'trazabilidad/informe_cumplimiento_productividad.html', data)


@grupo_requerido('administrador', 'coordinador', 'consultas generales')
def solicitudes_recepcionadas(request):
    """Reportes por Solicitudes Recepcionadas."""
    sw = False
    titulo = "ESTADISTICO DE PRUEBAS POR SOLICITUDES RECEPCIONADAS"
    enlace = "/reportes/solicitudes_recepcionadas/"
    if request.method == 'POST':
        fi = request.POST['fechai']
        ff = request.POST['fechaf']
        form = fechaRangoForm(request.POST)
        if form.is_valid():
            sw = True
            fi_format = datetime.datetime.strptime(fi, '%Y-%m-%d').date()
            ff_format = datetime.datetime.strptime(ff, '%Y-%m-%d').date()
            ff_format = ff_format + timedelta(days=1)
            recibidas = Recepcion.objects.filter(
                fecha_recepcion__range=(fi_format, ff_format),
                confirmada=True
            ).order_by('-id')
            lista, total = organiza_areas(recibidas)
            acumulado = 0
            grafico = [['Resultado', 'Porcentaje', {'role': 'annotation'}]]
            for p in lista:
                p['porcentaje'] = (p['frecuencia'] / total) * 100
                acumulado = acumulado + p['porcentaje']
                p['acumulado'] = acumulado
                grafico.append([p['resultado'].upper(), p['porcentaje'], p['frecuencia']])

            if 'excel' in request.POST:
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=reporte.xlsx'
                schema = ['radicado', 'recepcion', 'solicitante', 'corresponde']
                order = ['AREA', 'FRECUENCIA', 'PORCENTAJE', 'ACUMULADO']
                config = {
                    'function': solicitudes_recepcionadas,
                    'schema': schema,
                    'order': order,
                    'type': 'column',
                    'data': lista
                }
                excel = Excel(titulo=titulo, **config).write()
                response.write(excel)
                return response

            data = {
                'form': form, 'lista': lista, 'grafico': grafico,
                'sw': sw, 'total': total, 'titulo': titulo, 'enlace': enlace
            }
            return render(request, 'trazabilidad/informe_solicitudes_recepcionadas.html', data)
    else:
        form = fechaRangoForm()

    data = {'form': form, 'titulo': titulo, 'enlace': enlace}
    return render(request, 'trazabilidad/informe_solicitudes_recepcionadas.html', data)


@grupo_requerido('administrador', 'coordinador', 'consultas generales')
def pendiente_aceptacion(request):
    """Reportes por Solicitudes Pendientes por aceptacion del analista."""
    sw = False
    titulo = "ESTADISTICO DE INGRESOS PENDIENTES POR ACEPTACION DEL ANALISTA"
    enlace = "/reportes/pendiente_aceptacion/"
    if request.method == 'POST':
        fi = request.POST['fechai']
        ff = request.POST['fechaf']
        form = fechaRangoForm(request.POST)
        # form_usuario = UsuarioForm(request.POST)
        if form.is_valid():
            sw = True
            fi_format = datetime.datetime.strptime(fi, '%Y-%m-%d').date()
            ff_format = datetime.datetime.strptime(ff, '%Y-%m-%d').date()
            ff_format = ff_format + timedelta(days=1)
            recibidas = Recepcion.objects.filter(
                fecha_recepcion__range=(fi_format, ff_format),
                confirmada=True, estado_analista=""
            ).order_by('-id')
            lista, total = organiza_areas(recibidas)
            acumulado = 0
            grafico = [['Resultado', 'Porcentaje', {'role': 'annotation'}]]
            for p in lista:
                p['porcentaje'] = (p['frecuencia'] / total) * 100
                acumulado = acumulado + p['porcentaje']
                p['acumulado'] = acumulado
                grafico.append([p['resultado'].upper(), p['porcentaje'], p['frecuencia']])

            if 'excel' in request.POST:
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=reporte.xlsx'
                schema = ['radicado', 'recepcion', 'solicitante', 'corresponde']
                order = ['AREA', 'FRECUENCIA', 'PORCENTAJE', 'ACUMULADO']
                config = {
                    'function': pendiente_aceptacion,
                    'schema': schema,
                    'order': order,
                    'type': 'column',
                    'data': lista
                }
                excel = Excel(titulo=titulo, **config).write()
                response.write(excel)
                return response

            data = {'form': form, 'lista': lista, 'grafico': grafico, 'sw': sw, 'total': total, 'titulo': titulo, 'enlace': enlace}
            return render(request, 'trazabilidad/informe_solicitudes_recepcionadas.html', data)
    else:
        form = fechaRangoForm()

    data = {'form': form, 'titulo': titulo, 'enlace': enlace}
    return render(request, 'trazabilidad/informe_solicitudes_recepcionadas.html', data)


@grupo_requerido('administrador', 'coordinador', 'consultas generales')
def informes_resultados(request):
    """Reportes por Solicitudes con Informes de Resultados."""
    sw = False
    titulo = "ESTADISTICO DE INFORMES DE RESULTADOS EMITIDOS"
    enlace = "/reportes/informes_resultados/"
    if request.method == 'POST':
        fi = request.POST['fechai']
        ff = request.POST['fechaf']
        form = fechaRangoForm(request.POST)
        form_usuario = UsuarioForm(request.POST)
        if form.is_valid() and form_usuario.is_valid():
            usuario = request.POST['usuario']
            sw = True
            fi_format = datetime.datetime.strptime(fi, '%Y-%m-%d').date()
            ff_format = datetime.datetime.strptime(ff, '%Y-%m-%d').date()
            ff_format = ff_format + timedelta(days=1)
            lista_id = Reporte.objects.filter(
                registro_recepcion__fecha_recepcion__range=(fi_format, ff_format),
                registro_recepcion__analista=usuario, confirmado=True
            ).values_list('registro_recepcion', flat=True)
            recibidas = Recepcion.objects.filter(id__in=lista_id).order_by('-id')
            lista, total = organiza_areas(recibidas)
            acumulado = 0
            grafico = [['Resultado', 'Porcentaje', {'role': 'annotation'}]]
            for p in lista:
                p['porcentaje'] = (p['frecuencia'] / total) * 100
                acumulado = acumulado + p['porcentaje']
                p['acumulado'] = acumulado
                grafico.append([p['resultado'].upper(), p['porcentaje'], p['frecuencia']])

            if 'excel' in request.POST:
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=reporte.xlsx'
                schema = ['radicado', 'recepcion', 'solicitante', 'corresponde']
                order = ['AREA', 'FRECUENCIA', 'PORCENTAJE', 'ACUMULADO']
                config = {
                    'function': informes_resultados,
                    'schema': schema,
                    'order': order,
                    'type': 'column',
                    'data': lista
                }
                excel = Excel(titulo=titulo, **config).write()
                response.write(excel)
                return response

            data = {'form': form, 'form_usuario': form_usuario, 'lista': lista, 'grafico': grafico, 'sw': sw, 'total': total, 'titulo': titulo, 'enlace': enlace}
            return render(request, 'trazabilidad/informe_solicitudes_recepcionadas.html', data)
    else:
        form = fechaRangoForm()
        form_usuario = UsuarioForm()

    data = {'form': form, 'form_usuario': form_usuario, 'titulo': titulo, 'enlace': enlace}
    return render(request, 'trazabilidad/informe_solicitudes_recepcionadas.html', data)


@grupo_requerido('administrador', 'coordinador', 'consultas generales')
def ingreso_parcial(request):
    """Reportes por Solicitudes por Ingreso Parcial."""
    sw = False
    titulo = "ESTADISTICO DE INGRESOS PARCIALES"
    enlace = "/reportes/ingreso_parcial/"
    if request.method == 'POST':
        fi = request.POST['fechai']
        ff = request.POST['fechaf']
        form = fechaRangoForm(request.POST)
        if form.is_valid():
            sw = True
            fi_format = datetime.datetime.strptime(fi, '%Y-%m-%d').date()
            ff_format = datetime.datetime.strptime(ff, '%Y-%m-%d').date()
            ff_format = ff_format + timedelta(days=1)
            recibidas = Recepcion.objects.filter(
                fecha_recepcion__range=(fi_format, ff_format),
                confirmada=False
            ).order_by('-id')
            usuario_recibidas = recibidas.values(
                'recepcionista__username'
            ).order_by('recepcionista__username').annotate(Count('recepcionista'))
            total = 0
            acumulado = 0
            lista = []
            ingresos_parciales = True
            grafico = [['Resultado', 'Porcentaje', {'role': 'annotation'}]]
            for p in usuario_recibidas:
                total = total + p['recepcionista__count']

            for p in usuario_recibidas:
                detalle = recibidas.filter(recepcionista__username=p['recepcionista__username'])
                porcentaje = (p['recepcionista__count'] / total) * 100
                acumulado = acumulado + porcentaje
                lista.append(
                    {'resultado': p['recepcionista__username'],
                     'frecuencia': p['recepcionista__count'],
                     'porcentaje': porcentaje,
                     'acumulado': acumulado,
                     'detalle': detalle}
                )
                grafico.append(
                    [p['recepcionista__username'].upper(), porcentaje, p['recepcionista__count']]
                )

            if 'excel' in request.POST:
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=reporte.xlsx'
                order = ['RECEPCIONISTA', 'FRECUENCIA', 'PORCENTAJE', 'ACUMULADO']
                config = {
                    'function': ingreso_parcial,
                    'order': order,
                    'type': 'column',
                    'data': lista,
                    'titulo': titulo
                }
                excel = Excel(**config).write()
                response.write(excel)
                return response

            data = {'form': form, 'lista': lista, 'grafico': grafico, 'sw': sw, 'total': total, 'titulo': titulo, 'enlace': enlace, 'ingresos_parciales': ingresos_parciales}
            return render(request, 'trazabilidad/informe_solicitudes_recepcionadas.html', data)
    else:
        form = fechaRangoForm()

    data = {'form': form, 'titulo': titulo, 'enlace': enlace}
    return render(request, 'trazabilidad/informe_solicitudes_recepcionadas.html', data)


@grupo_requerido('administrador', 'coordinador', 'consultas generales')
def productividad_recepcion(request):
    total = 0
    sw = False
    info = grafico = []
    titulo = 'ESTADÍSTICO DE PRODUCTIVIDAD INGRESOS CONFIRMADOS RECEPCIONADOS'
    if request.method == 'POST':
        form = f.ProductividadRecepcionForm(request.POST)
        if form.is_valid():
            sw = True
            info, total, grafico = form.report_data()

            if 'excel' in request.POST:
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=reporte productividad ingresos recepcionados.xlsx'
                excel = Excel(
                    data=info,
                    titulo=titulo,
                    function=productividad_recepcion,
                    order=['RECEPCIONISTA', 'FRECUENCIA', 'PORCENTAJE', 'ACUMULADO'],
                ).write()
                response.write(excel)
                return response
    else:
        form = f.ProductividadRecepcionForm()

    return render(request, 'trazabilidad/informe_productividad_recepcion.html', {
        'sw': sw,
        'form': form,
        'info': info,
        'total': total,
        'titulo': titulo,
        'grafico': grafico,
    })

# Informes Comparativos
@grupo_requerido('administrador', 'coordinador', 'consultas generales')
def multiconsulta(request):
    titulo = "Multiconsulta"
    if request.method == 'POST':
        form = MulticonsultaForm(request.POST or None)
        if form.is_valid():
            sw = True
            prueba = form.cleaned_data['prueba']
            municipio = form.cleaned_data['municipio']
            resultado = form.cleaned_data['resultado']
            sexo = form.cleaned_data['sexo']
            fechai = form.cleaned_data['fechai']
            fechaf = form.cleaned_data['fechaf']
            fechaf = fechaf + timedelta(days=1)
            edad1 = form.cleaned_data['edad1']
            edad2 = form.cleaned_data['edad2']
            embarazada = form.cleaned_data['embarazada']
            if edad1 is None:
                edad1 = 0
            if edad2 is None:
                edad2 = 100
            paciente = Paciente.objects.filter(edad__range=(edad1, edad2))
            pruebasR = PruebasRealizadas.objects.filter(
                fecha_pre_analisis__range=(fechai, fechaf),
                prueba=prueba, estado=PruebasRealizadas.RESULTADO, muestra__clinica__municipio=municipio,
                muestra__clinica__paciente=paciente, resultados=resultado
            ).exclude(resultados=None)
            if sexo != 'A':
                pruebasR = pruebasR.filter(muestra__clinica__paciente__sexo=sexo)
            # print(embarazada)
            if embarazada == 'True':
                pruebasR = pruebasR.filter(muestra__clinica__embarazada=True)

            conteo_resultados = pruebasR.values(
                'muestra__clinica__municipio__nombre'
            ).annotate(Count('muestra__clinica__municipio'))
            total = 0
            acumulado = 0
            lista = []
            grafico = [['Resultado', 'Frecuencia']]
            #conteo_resultados = pruebas.values('resultado__nombre').annotate(Count('resultado'))
            for p in conteo_resultados:
                total = total + p['muestra__clinica__municipio__count']
            for p in conteo_resultados:
                detalle = pruebasR.filter(muestra__clinica__municipio__nombre=p['muestra__clinica__municipio__nombre'])
                porcentaje = (p['muestra__clinica__municipio__count'] / total) * 100
                lista.append(
                    {'resultado': p['muestra__clinica__municipio__nombre'],
                     'frecuencia': p['muestra__clinica__municipio__count'],
                     'porcentaje': porcentaje, 'acumulado': acumulado, 'detalle': detalle}
                )
                grafico.append([p['muestra__clinica__municipio__nombre'], p['muestra__clinica__municipio__count']])

            newlist = sorted(lista, key=lambda k: k['frecuencia'], reverse=True)
            lista = newlist
            for p in lista:
                porcentaje = p['porcentaje']
                acumulado = acumulado + porcentaje
                p['acumulado'] = acumulado

            if 'excel' in request.POST:
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=reporte.xlsx'
                excel = Excel(data=lista, titulo=titulo, function=multiconsulta).write()
                response.write(excel)
                return response

            data = {'form': form, 'titulo': titulo, 'grafico': grafico, 'sw': sw, 'lista': lista, 'total': total, 'embarazada': embarazada}

        else:
            data = {'form': form, 'titulo': titulo}

    else:
        form = MulticonsultaForm()
        data = {'form': form, 'titulo': titulo}

    return render(request, 'trazabilidad/grafico.html', data)


@grupo_requerido('administrador', 'coordinador', 'consultas generales')
def produccion_area(request):
    """Reportes por Solicitudes por Ingreso Parcial."""
    sw = False
    titulo = "ESTADISTICO DE PRODUCCION POR AREA"
    enlace = "/reportes/produccion_area/"
    from calendar import monthrange
    if request.method == 'POST':
        fi = request.POST['fechai']
        ff = request.POST['fechaf']
        form = fechaRangoForm(request.POST)
        if form.is_valid():
            sw = True
            fi_format = datetime.datetime.strptime(fi, '%Y-%m-%d').date()
            ff_format = datetime.datetime.strptime(ff, '%Y-%m-%d').date()
            ff_format = ff_format + timedelta(days=1)
            # recibidas = Recepcion.objects.filter(fecha_recepcion__range=(fi_format,ff_format), confirmada=False).order_by('-id')
            # usuario_recibidas = recibidas.values('recepcionista__username').order_by('recepcionista__username').annotate(Count('recepcionista'))
            lista = []
            grafico = []
            total = 0
            di = fi_format
            d2 = ff_format
            while True:
                if di < d2:
                    if di.month == d2.month:
                        # Aqui se hace la ultima consulta
                        recibidas = Recepcion.objects.filter(
                            fecha_recepcion__range=(di, d2), confirmada=True
                        ).order_by('-id')
                        lista, total = organiza_areas(recibidas)
                        break
                    else:
                        mday = monthrange(di.year, di.month)[1]
                        df = date(di.year, di.month, mday)
                        df.strftime("%Y-%m-%d")
                        df = df + timedelta(days=1)
                        # Aqui se hace la consulta
                        recibidas = Recepcion.objects.filter(
                            fecha_recepcion__range=(di, df), confirmada=True
                        ).order_by('-id')
                        lista, total = organiza_areas(recibidas)
                        di = df
                else:
                    break

            data = {'form': form, 'lista': lista, 'grafico': grafico, 'sw': sw, 'total': total, 'titulo': titulo}
            return render(request, 'trazabilidad/informe_solicitudes_recepcionadas.html', data)
    else:
        form = fechaRangoForm()

    data = {'form': form, 'titulo': titulo, 'enlace': enlace}
    return render(request, 'trazabilidad/informe_solicitudes_recepcionadas.html', data)


# Buscador

@login_required
@permission_required('administracion.can_buscar_ingresos')
def buscar_radicado(request):
    """Permite buscar un radicado."""

    mostrar_paciente = False
    lista = []

    if request.method == 'POST':
        form = BuscadorForm(data=request.POST)

        if form.is_valid():
            fi = form.cleaned_data.get('fecha_inicial')
            ff = form.cleaned_data.get('fecha_final')
            t_orden = form.cleaned_data.get('busqueda')
            tipo = form.cleaned_data['tipo']

            user = request.user
            ingresos = (
                models.Ingreso.objects
                    .confirmados()
                    .select_related('programa')
                    .aceptados_recepcionista()
                    .no_rechazados_analista()
            )

            # Cuando NO es super usuario ni administrador se filtra dependiendo del area a la que pertenezca el usuario
            if not user.has_perm('administracion.can_see_ingresos_todos_programas'):
                try:
                    ingresos = ingresos.by_areas(user.empleado.areas.all())
                except (Empleado.DoesNotExist, AttributeError) as e:
                    print(e)
                    messages.warning(request, 'No tiene un área asignada. Por favor contacte al administrador del sistema.')
                    ingresos = ingresos.none()

            lista = None
            if fi is not None and ff is not None:
                ingresos = ingresos.filter(fecha_recepcion__range=(fi, ff))
            else:
                if tipo == BuscadorForm.RADICADO:
                    query = (
                        Q(indice_radicado__icontains=t_orden) |
                        Q(programa__nombre__icontains=t_orden) |
                        Q(programa__codigo__icontains=t_orden) |
                        Q(muestras__pruebas__area__nombre__icontains=t_orden) |
                        Q(muestras__pruebas__area__programa__nombre__icontains=t_orden) |
                        Q(muestras__clinica__institucion__nombre__icontains=t_orden) |
                        Q(muestras__clinica__institucion__municipio__nombre__icontains=t_orden) |
                        Q(muestras__clinica__institucion__municipio__departamento__nombre__icontains=t_orden) |
                        Q(muestras__entomologia__lugar_recoleccion__nombre__icontains=t_orden) |
                        Q(muestras__entomologia__lugar_recoleccion__municipio__nombre__icontains=t_orden) |
                        Q(muestras__entomologia__lugar_recoleccion__municipio__departamento__nombre__icontains=t_orden) |
                        Q(muestras__citohistopatologia__institucion__nombre__icontains=t_orden) |
                        Q(muestras__citohistopatologia__institucion__municipio__nombre__icontains=t_orden) |
                        Q(muestras__citohistopatologia__institucion__municipio__departamento__nombre__icontains=t_orden) |
                        Q(muestras__bancosangre__institucion__nombre__icontains=t_orden) |
                        Q(muestras__bancosangre__institucion__municipio__nombre__icontains=t_orden) |
                        Q(muestras__bancosangre__institucion__municipio__departamento__nombre__icontains=t_orden) |
                        Q(muestras__eedd__institucion__nombre__icontains=t_orden) |
                        Q(muestras__eedd__institucion__municipio__nombre__icontains=t_orden) |
                        Q(muestras__eedd__institucion__municipio__departamento__nombre__icontains=t_orden) |
                        Q(muestras__eeid__institucion__nombre__icontains=t_orden) |
                        Q(muestras__eeid__institucion__municipio__nombre__icontains=t_orden) |
                        Q(muestras__eeid__institucion__municipio__departamento__nombre__icontains=t_orden) |
                        Q(muestras__agua__informacion_general__solicitante__nombre__icontains=t_orden)
                    )

                    ingresos = ingresos.filter(query).distinct()
                else:
                    query = (
                        Q(muestras__clinica__paciente__nombre__icontains=t_orden) |
                        Q(muestras__clinica__paciente__apellido__icontains=t_orden) |
                        Q(muestras__clinica__paciente__identificacion__icontains=t_orden) |
                        Q(muestras__citohistopatologia__paciente__nombre__icontains=t_orden) |
                        Q(muestras__citohistopatologia__paciente__apellido__icontains=t_orden) |
                        Q(muestras__citohistopatologia__paciente__identificacion__icontains=t_orden) |
                        Q(muestras__bancosangre__paciente__nombre__icontains=t_orden) |
                        Q(muestras__bancosangre__paciente__apellido__icontains=t_orden) |
                        Q(muestras__bancosangre__paciente__identificacion__icontains=t_orden) |
                        Q(muestras__clinica__institucion__nombre__icontains=t_orden) |
                        Q(muestras__clinica__institucion__municipio__nombre__icontains=t_orden) |
                        Q(muestras__clinica__institucion__municipio__departamento__nombre__icontains=t_orden) |
                        Q(muestras__pruebas__area__nombre__icontains=t_orden) |
                        Q(muestras__pruebas__area__programa__nombre__icontains=t_orden) |
                        Q(muestras__entomologia__lugar_recoleccion__nombre__icontains=t_orden) |
                        Q(muestras__entomologia__lugar_recoleccion__municipio__nombre__icontains=t_orden) |
                        Q(muestras__entomologia__lugar_recoleccion__municipio__departamento__nombre__icontains=t_orden) |
                        Q(muestras__citohistopatologia__institucion__nombre__icontains=t_orden) |
                        Q(muestras__citohistopatologia__institucion__municipio__nombre__icontains=t_orden) |
                        Q(muestras__citohistopatologia__institucion__municipio__departamento__nombre__icontains=t_orden) |
                        Q(muestras__bancosangre__institucion__nombre__icontains=t_orden) |
                        Q(muestras__bancosangre__institucion__municipio__nombre__icontains=t_orden) |
                        Q(muestras__bancosangre__institucion__municipio__departamento__nombre__icontains=t_orden) |
                        Q(muestras__eedd__institucion__nombre__icontains=t_orden) |
                        Q(muestras__eedd__institucion__municipio__nombre__icontains=t_orden) |
                        Q(muestras__eedd__institucion__municipio__departamento__nombre__icontains=t_orden) |
                        Q(muestras__eeid__institucion__nombre__icontains=t_orden) |
                        Q(muestras__eeid__institucion__municipio__nombre__icontains=t_orden) |
                        Q(muestras__eeid__institucion__municipio__departamento__nombre__icontains=t_orden) |
                        Q(muestras__agua__informacion_general__solicitante__nombre__icontains=t_orden) |
                        Q(muestras__muestra346__informacion_general__info_paciente__paciente__nombre__icontains=t_orden) |
                        Q(muestras__muestra348__informacion_general__info_paciente__paciente__nombre__icontains=t_orden) |
                        Q(muestras__muestra346__informacion_general__info_paciente__paciente__apellido__icontains=t_orden) |
                        Q(muestras__muestra348__informacion_general__info_paciente__paciente__apellido__icontains=t_orden) |
                        Q(muestras__muestra346__informacion_general__info_paciente__paciente__identificacion__icontains=t_orden) |
                        Q(muestras__muestra348__informacion_general__info_paciente__paciente__identificacion__icontains=t_orden)
                    )

                    ingresos = ingresos.filter(query).distinct()
                    mostrar_paciente = True

            lista = ingresos
    else:
        lista = None
        form = BuscadorForm()

    return render(request, 'trazabilidad/buscador.html', {
        'form': form,
        'lista': lista,
        'mostrar_paciente': mostrar_paciente,
    })


@transaction.atomic
@login_required
@permission_required('administracion.can_devolver_ingreso_analisis')
def devolver_ingreso(request, id):
    """Muestra todas las pruebas realizadas en el ingreso especificado y permite devolver una prueba especifica que
    se encuentre terminada(estado ANALISIS)."""

    prefetch = Prefetch('muestras__pruebasrealizadas_set',
                        queryset=PruebasRealizadas.objects.order_by('prueba__area', 'prueba'))
    ingreso = Recepcion.objects.prefetch_related(prefetch).get(id=id)

    if request.method == 'POST':
        prueba = PruebasRealizadas.objects.get(id=request.POST['devolver_prueba'])
        prueba.estado = PruebasRealizadas.ANALISIS
        prueba.save()

        ingreso = prueba.muestra.registro_recepcion
        ingreso.reportes.all().delete()

        return redirect(reverse('trazabilidad:devolver_ingreso', args=(ingreso.id,)) + '#anchor-{0}'.format(prueba.id))

    data = {'ingreso': ingreso}
    return render(request, 'trazabilidad/devolver_ingreso.html', data)


@grupo_requerido('administrador', 'lider area')
def agregar_quitar_pruebas(request, id):
    """Permite agregar o quitar pruebas de un ingreso del programa clinico"""

    ingreso = get_object_or_404(Recepcion, pk=id)
    # muestra = ingreso.muestras.non_polymorphic().first()
    # pruebas = muestra.pruebasrealizadas_set.all()

    if request.method == 'POST':
        if 'eliminar_prueba' in request.POST:
            prueba_eliminar = PruebasRealizadas.objects.get(id=request.POST['eliminar_prueba'])
            prueba_eliminar.delete()

        if 'agregar' in request.POST:
            form = FormularioAgregarPruebas(data=request.POST, ingreso=ingreso)

            if form.is_valid():
                pruebas = form.cleaned_data['pruebas']
                muestra = form.cleaned_data['muestra']
                for prueba in pruebas:
                    PruebasRealizadas.objects.create(prueba=prueba, muestra=muestra)
                ingreso.reportes.update(confirmado=False)

        return HttpResponseRedirect('')

    else:
        form = FormularioAgregarPruebas(ingreso=ingreso)

    data = {'form': form, 'ingreso': ingreso}
    return render(request, 'trazabilidad/agregar_quitar_pruebas.html', data)


@grupo_requerido('biofisico', 'analista')
def control_temperatura_area(request):
    """Muestra las temperaturas registradas de las areas"""

    user = request.user
    area = None
    registros = []
    grafico = []
    celsius = False

    if request.method == 'POST':
        form = AreaTemperaturaForm(data=request.POST)

        if form.is_valid():
            area = form.cleaned_data['area']
            fecha_inicial = form.cleaned_data['fecha_inicial']
            fecha_final = form.cleaned_data['fecha_final']
            unidad = form.cleaned_data['unidad']
            registros = RegistroTemperaturaArea.objects.filter(
                fecha_registro__range=(fecha_inicial, fecha_final + datetime.timedelta(days=1)), area=area
            )

            try:
                from equipos.utils import convertidor_unidad_temperatura
            except:
                pass

            temperatura_maxima = convertidor_unidad_temperatura(
                area.temperatura_maxima, RegistroTemperaturaArea.CENTIGRADOS, unidad
            )
            temperatura_minima = convertidor_unidad_temperatura(
                area.temperatura_minima, RegistroTemperaturaArea.CENTIGRADOS, unidad
            )

            if unidad == RegistroTemperaturaArea.FARHENHEIT:
                grafico = [['Fecha', 'Temperatura Minima(°F)', 'Temperatura Registrada(°F)', 'Temperatura Maxima(°F)']]
            else:
                celsius = True
                grafico = [['Fecha', 'Temperatura Minima(°C)', 'Temperatura Registrada(°C)', 'Temperatura Maxima(°C)']]
            grafico_2 = [['Fecha', 'Humedad Minima (%)', 'Humedad Registrada (%)', 'Humedad Maxima (%)']]

            for registro in reversed(registros):
                temperatura = convertidor_unidad_temperatura(registro.temperatura, registro.unidad, unidad)
                humedad = registro.humedad
                fecha = timezone.localtime(registro.fecha_registro)

                grafico.append([fecha.strftime("%Y-%m-%d %H:%M"), temperatura_minima, temperatura, temperatura_maxima])
                grafico_2.append([fecha.strftime("%Y-%m-%d %H:%M"), float(area.humedad_minima), float(humedad), float(area.humedad_maxima)])

        data = {'registros': registros, 'form': form, 'celsius': celsius, 'area': area, 'grafico': grafico, 'grafico_2': grafico_2}

    else:
        form = AreaTemperaturaForm()
        data = {'form': form, 'area': area}

    return render(request, 'trazabilidad/control_temperatura_area.html', data)


@grupo_requerido('biofisico', 'analista')
def registro_temperatura_area(request, id_area):
    """Permite ingresar la temperatura de el area especificada"""

    area = get_object_or_404(Area, id=id_area)

    if request.method == 'POST':
        form = RegistroTemperaturaAreaForm(data=request.POST, area=area)

        if form.is_valid():
            registro = form.save(commit=False)
            registro.registrado_por = request.user
            registro.area = area
            registro.save()
            return redirect(reverse('trazabilidad:control_temperatura_area'))
    else:
        form = RegistroTemperaturaAreaForm(initial={'fecha_registro': timezone.now()}, area=area)

    data = {'form': form, 'area': area}
    return render(request, 'trazabilidad/registro_temperatura_area.html', data)

class AprobacionInformeResultadosView(LoginRequiredMixin, PermissionRequiredMixin, generic.TemplateView):
    
    permission_required = ['administracion.can_aprobar_informes']
    template_name = 'trazabilidad/aprobacion_informe_resultados.html'

    def get_context_data(self, **kwargs):
        kwargs.update({'ingresos': self.ingresos()})
        return super().get_context_data(**kwargs)
    
    def ingresos(self):
        query = models.PruebasRealizadas.objects.filter(muestra__registro_recepcion=OuterRef('pk')).positivos()
        return (
            models.Ingreso.objects
                .confirmados()
                .con_informe_confirmado()
                .select_related('programa')
                .con_informe_no_aprobado()
                .annotate(is_positivo=Exists(query))
        )

class DetalleAreaView(RetrieveAPIView):
    """Retorna un area en formato JSON segun su id."""

    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [permissions.IsAuthenticated]


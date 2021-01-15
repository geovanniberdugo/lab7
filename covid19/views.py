from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.forms.models import modelformset_factory
from django.views.generic import FormView
from django.http import HttpResponse
from django.utils import timezone
from django.db import transaction
from contextlib import suppress
from django.urls import reverse

from trazabilidad.forms import RecepcionForm, EstadoIngresoForm, ActualizarRecepcionForm
from trazabilidad.models import Programa, Recepcion, Paciente
from common.decorators import grupo_requerido
from trazabilidad import enums
from . import services as s
from . import models as m
from . import forms as f

@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def nueva_muestra_346(request):
    """Permite el ingreso de nuevas muestras de acuerdo a Formulario-346."""

    MuestraFormSet = modelformset_factory(
        m.Muestra346,
        # extra=0,
        # min_num=1,
        # validate_min=True,
        form=f.Muestra346Form,
        formset=f.Muestra346FormSet,
    )

    if request.method == 'POST':
        paciente = Paciente.objects.by_identificacion(request.POST['paciente-identificacion']).first()
        form_paciente = f.PacienteForm(instance=paciente, data=request.POST, prefix='paciente')
        form_info_paciente = f.InfoPacienteForm(data=request.POST, prefix='info_paciente')
        form_ingreso = RecepcionForm(user=request.user, data=request.POST, prefix='recepcion')
        form_info = f.InfoGeneral346Form(data=request.POST, prefix='general')
        formset_muestra = MuestraFormSet(queryset=m.Muestra346.objects.none(), data=request.POST)

        if (
            form_info.is_valid() and
            form_ingreso.is_valid() and 
            form_paciente.is_valid() and
            form_info_paciente.is_valid() and
            formset_muestra.is_valid()
        ):
            ingreso = form_ingreso.save(commit=False)
            ingreso.recepcionista = request.user
            ingreso.programa = Programa.objects.covid19()
            ingreso.save()

            paciente = form_paciente.save(request.user)
            info_paciente = form_info_paciente.save(request.user, paciente)
            info_general = form_info.save(info_paciente)

            formset_muestra.save(user=request.user, ingreso=ingreso, info=info_general, ingreso_nuevo=True)

            return redirect(reverse('covid19:estado_muestra', args=(ingreso.id,)))
    else:
        form_ingreso = RecepcionForm(user=request.user, prefix='recepcion')
        form_paciente = f.PacienteForm(prefix='paciente')
        form_info = f.InfoGeneral346Form(prefix='general')
        form_info_paciente = f.InfoPacienteForm(prefix='info_paciente')
        formset_muestra = MuestraFormSet(queryset=m.Muestra346.objects.none())

    return render(request, 'covid19/form_muestra_346.html', {
        'muestra_nueva': True,
        'form_info': form_info,
        'form_ingreso': form_ingreso,
        'form_paciente': form_paciente,
        'formset_muestra': formset_muestra,
        'form_info_paciente': form_info_paciente,
    })

@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def actualizar_muestra_346(request, id):
    ingreso = get_object_or_404(Recepcion, pk=id)
    muestras = ingreso.muestras.all()
    general = muestras.first().informacion_general
    info_paciente = general.info_paciente
    paciente = info_paciente.paciente

    MuestraFormSet = modelformset_factory(
        m.Muestra346,
        extra=0,
        min_num=1,
        validate_min=True,
        form=f.Muestra346Form,
        formset=f.Muestra346FormSet,
    )

    if request.method == 'POST':
        paciente = Paciente.objects.by_identificacion(request.POST['paciente-identificacion']).first()
        form_paciente = f.PacienteForm(instance=paciente, data=request.POST, prefix='paciente')
        form_info_paciente = f.InfoPacienteForm(instance=info_paciente, data=request.POST, prefix='info_paciente')
        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, data=request.POST, prefix='recepcion')
        form_info = f.InfoGeneral346Form(instance=general, data=request.POST, prefix='general')
        formset_muestra = MuestraFormSet(queryset=m.Muestra346.objects.filter(id__in=muestras), data=request.POST)

        if (
            form_info.is_valid() and
            form_ingreso.is_valid() and 
            form_paciente.is_valid() and
            form_info_paciente.is_valid() and
            formset_muestra.is_valid()
        ):
            ingreso = form_ingreso.save()
            paciente = form_paciente.save(request.user)
            info_paciente = form_info_paciente.save(request.user, paciente)
            info_general = form_info.save(info_paciente)

            formset_muestra.save(user=request.user, ingreso=ingreso, info=info_general, ingreso_nuevo=False)
            return redirect(reverse('trazabilidad:ingresos'))
    else:
        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, prefix='recepcion')
        form_paciente = f.PacienteForm(instance=paciente, prefix='paciente')
        form_info = f.InfoGeneral346Form(instance=general, prefix='general')
        form_info_paciente = f.InfoPacienteForm(instance=info_paciente, prefix='info_paciente')
        formset_muestra = MuestraFormSet(queryset=m.Muestra346.objects.filter(id__in=muestras))

    return render(request, 'covid19/form_muestra_346.html', {
        'muestra_nueva': False,
        'form_info': form_info,
        'form_ingreso': form_ingreso,
        'form_paciente': form_paciente,
        'formset_muestra': formset_muestra,
        'form_info_paciente': form_info_paciente,
    })


@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def nueva_muestra_348(request):
    """Permite el ingreso de nuevas muestras de acuerdo a Formulario-348."""

    MuestraFormSet = modelformset_factory(
        m.Muestra348,
        # extra=0,
        # min_num=1,
        # validate_min=True,
        form=f.Muestra348Form,
        formset=f.Muestra348FormSet,
    )

    if request.method == 'POST':
        paciente = Paciente.objects.by_identificacion(request.POST['paciente-identificacion']).first()
        form_paciente = f.PacienteForm(instance=paciente, data=request.POST, prefix='paciente')
        form_info_paciente = f.InfoPacienteForm(data=request.POST, prefix='info_paciente')
        form_ingreso = RecepcionForm(user=request.user, data=request.POST, prefix='recepcion')
        form_info = f.InfoGeneral348Form(data=request.POST, prefix='general')
        formset_muestra = MuestraFormSet(queryset=m.Muestra348.objects.none(), data=request.POST)
 
        if (
            form_info.is_valid() and
            form_ingreso.is_valid() and 
            form_paciente.is_valid() and
            form_info_paciente.is_valid() and
            formset_muestra.is_valid()
        ):
            ingreso = form_ingreso.save(commit=False)
            ingreso.recepcionista = request.user
            ingreso.programa = Programa.objects.covid19()
            ingreso.save()

            paciente = form_paciente.save(request.user)
            info_paciente = form_info_paciente.save(request.user, paciente)
            info_general = form_info.save(info_paciente)

            formset_muestra.save(user=request.user, ingreso=ingreso, info=info_general, ingreso_nuevo=True)

            return redirect(reverse('covid19:estado_muestra', args=(ingreso.id,)))
    else:

        form_ingreso = RecepcionForm(user=request.user, prefix='recepcion')
        form_paciente = f.PacienteForm(prefix='paciente')
        form_info = f.InfoGeneral348Form(prefix='general')
        form_info_paciente = f.InfoPacienteForm(prefix='info_paciente')
        formset_muestra = MuestraFormSet(queryset=m.Muestra348.objects.none())

    return render(request, 'covid19/form_muestra_348.html', {
        'muestra_nueva': True,
        'form_info': form_info,
        'form_ingreso': form_ingreso,
        'form_paciente': form_paciente,
        'formset_muestra': formset_muestra,
        'form_info_paciente': form_info_paciente,
    })

@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def actualizar_muestra_348(request, id):
    ingreso = get_object_or_404(Recepcion, pk=id)
    muestras = ingreso.muestras.all()
    general = muestras.first().informacion_general
    info_paciente = general.info_paciente
    paciente = info_paciente.paciente

    MuestraFormSet = modelformset_factory(
        m.Muestra348,
        extra=0,
        min_num=1,
        validate_min=True,
        form=f.Muestra348Form,
        formset=f.Muestra348FormSet,
    )

    if request.method == 'POST':
        paciente = Paciente.objects.by_identificacion(request.POST['paciente-identificacion']).first()
        form_paciente = f.PacienteForm(instance=paciente, data=request.POST, prefix='paciente')
        form_info_paciente = f.InfoPacienteForm(instance=info_paciente, data=request.POST, prefix='info_paciente')
        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, data=request.POST, prefix='recepcion')
        form_info = f.InfoGeneral348Form(instance=general, data=request.POST, prefix='general')
        formset_muestra = MuestraFormSet(queryset=m.Muestra348.objects.filter(id__in=muestras), data=request.POST)

        if (
            form_info.is_valid() and
            form_ingreso.is_valid() and 
            form_paciente.is_valid() and
            form_info_paciente.is_valid() and
            formset_muestra.is_valid()
        ):
            ingreso = form_ingreso.save()
            paciente = form_paciente.save(request.user)
            info_paciente = form_info_paciente.save(request.user, paciente)
            info_general = form_info.save(info_paciente)

            formset_muestra.save(user=request.user, ingreso=ingreso, info=info_general, ingreso_nuevo=False)
            return redirect(reverse('trazabilidad:ingresos'))
    else:
        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, prefix='recepcion')
        form_paciente = f.PacienteForm(instance=paciente, prefix='paciente')
        form_info = f.InfoGeneral348Form(instance=general, prefix='general')
        form_info_paciente = f.InfoPacienteForm(instance=info_paciente, prefix='info_paciente')
        formset_muestra = MuestraFormSet(queryset=m.Muestra348.objects.filter(id__in=muestras))

    return render(request, 'covid19/form_muestra_348.html', {
        'muestra_nueva': False,
        'form_info': form_info,
        'form_ingreso': form_ingreso,
        'form_paciente': form_paciente,
        'formset_muestra': formset_muestra,
        'form_info_paciente': form_info_paciente,
    })

@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def actualizar_muestra(request, id):
    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()

    url = 'covid19:actualizar_muestra_346'
    if muestra.tipo == enums.TipoMuestraEnum.COVID348.value:
        url = 'covid19:actualizar_muestra_348'

    return redirect(reverse(url, args=(ingreso.id,)))

@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def estado_muestra(request, id):
    """Permite definir el estado de la recepción de una muestra de Covid (346 o 348). La muestra puede ser aceptada o rechazada."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra_clinica = ingreso.muestras.first()

    if request.method == 'POST':
        form = EstadoIngresoForm(instance=ingreso, data=request.POST)
        if form.is_valid():
            ingreso = form.save()
            return redirect(reverse('covid19:radicado_muestra', args=(id,)))
    else:
        form = EstadoIngresoForm(instance=ingreso)

    return render(request, 'covid19/estado_muestra.html', {
        'form': form,
        'imprimir': False,
        'ingreso': ingreso,
        'muestra_clinica': muestra_clinica,
    })

@login_required
@permission_required('administracion.can_ingresar_muestras_programas_clinicos')
def radicado_muestra(request, id):
    """Muestra el radicado de una muestra covid."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra_clinica = ingreso.muestras.first()

    return render(request, 'covid19/estado_muestra.html', {
        'imprimir': True,
        'ingreso': ingreso,
        'muestra_clinica': muestra_clinica,
    })

class EnvioMasivoResultadosMailView(LoginRequiredMixin, PermissionRequiredMixin, FormView):

    form_class = f.EnvioMasivoResultadosForm
    template_name = 'covid19/envio_masivo_resultados_mail.html'
    permission_required = ['administracion.can_mail_resultados_covid']

    def form_valid(self, form):
        return self.render_to_response(self.get_context_data(form=form, ingresos=form.resultados()))

class ConsultaResultadosView(LoginRequiredMixin, PermissionRequiredMixin, FormView):

    form_class = f.ConsultaResultadosForm
    template_name = 'covid19/consulta_resultados.html'
    permission_required = ['administracion.can_consultar_resultados_covid']

    def form_valid(self, form):
        return self.render_to_response(self.get_context_data(form=form, ingresos=form.resultados()))

class ExportacionExcelFichaView(LoginRequiredMixin, PermissionRequiredMixin, FormView):

    form_class = f.ExportacionExcelFichaForm
    template_name = 'covid19/ficha_excel.html'
    permission_required = ['administracion.can_exportar_ficha_excel']

    def form_valid(self, form):
        data, nombre = form.data_exportar()

        response = HttpResponse(data.export('xlsx'), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename={nombre}.xlsx'
        return response

class ImpresionLoteFichasView(LoginRequiredMixin, PermissionRequiredMixin, FormView):

    form_class = f.ImpresionLoteFichaForm
    template_name = 'covid19/impresion_lote_ficha.html'
    permission_required = ['administracion.can_imprimir_lote_fichas_covid']

    def form_valid(self, form):
        zip_, name = form.generar_zip(self.request)
        
        response = HttpResponse(zip_.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={name}.zip'
        return response


@login_required
def ficha_view(request, id):
    """Muestra el documento del reporte final."""

    query = (
        Recepcion.objects
            .select_related('programa')
            # .prefetch_related('muestras__informacion_general')
            .all()
            .prefetch_related(
                'muestras__informacion_general__upgd',
                'muestras__informacion_general__causa_muerte',
                'muestras__informacion_general__municipio_upgd',
                'muestras__informacion_general__municipio_residencia',
                'muestras__informacion_general__info_paciente__paciente',
            )
    )
    ingreso = get_object_or_404(query, pk=id)

    data = s.data_ficha(ingreso)

    return render(request, 'covid19/ficha_covid.html', data)

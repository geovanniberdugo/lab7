# Django imports
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.forms.models import modelformset_factory
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.urls import reverse

# Locale imports
from .models import BebidaAlcoholica, Producto
from .forms import MuestraBebidaAlcoholicaForm, MuestraBebidaAlcoholicaFormSet, InformacionBebidaAlcoholicaForm
from .forms import MuestraDecretoForm
from .serializers import ProductoSerializer
from common.decorators import grupo_requerido
from trazabilidad.forms import RecepcionForm, ActualizarRecepcionForm, EstadoIngresoForm
from trazabilidad.models import Programa, Recepcion

# Third Apps
from rest_framework.generics import ListAPIView
from rest_framework import permissions


@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_ambientes')
def nueva_muestra(request):
    """Permite ingresar una nueva muestra de bebidas alcoholicas."""

    MuestraFormSet = modelformset_factory(
        BebidaAlcoholica, formset=MuestraBebidaAlcoholicaFormSet,
        form=MuestraBebidaAlcoholicaForm, min_num=1,
        extra=0, validate_min=True
    )

    if request.method == "POST":
        form_ingreso = RecepcionForm(user=request.user, data=request.POST, prefix='recepcion')
        form_informacion = InformacionBebidaAlcoholicaForm(data=request.POST, prefix='general', usuario=request.user)
        formset_muestra = MuestraFormSet(
            queryset=BebidaAlcoholica.objects.none(), data=request.POST,
            usuario=request.user, nueva=True
        )

        if form_ingreso.is_valid() and form_informacion.is_valid():
            if formset_muestra.is_valid():
                ingreso = form_ingreso.save(commit=False)
                ingreso.recepcionista = request.user
                ingreso.programa = Programa.objects.bebidas_alcoholicas()
                ingreso.save()

                general = form_informacion.save()
                formset_muestra.save(ingreso=ingreso, general=general)

                return redirect(reverse('bebidas_alcoholicas:estado_muestra', args=(ingreso.id, )))
    else:
        form_ingreso = RecepcionForm(user=request.user, prefix='recepcion')
        form_informacion = InformacionBebidaAlcoholicaForm(prefix='general', usuario=request.user)
        formset_muestra = MuestraFormSet(queryset=BebidaAlcoholica.objects.none())

    data = {
        'form_ingreso': form_ingreso, 'muestra_nueva': True,
        'form_informacion': form_informacion, 'formset_muestra': formset_muestra
    }

    return render(request, 'bebidas_alcoholicas/nueva_muestra.html', data)


@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_ambientes')
def actualizar_muestra(request, id):
    """Permite actualizar una muestra de bebidas alcoholicas."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestras = ingreso.muestras.all()
    general = muestras.first().informacion_general

    MuestraFormSet = modelformset_factory(
        BebidaAlcoholica, formset=MuestraBebidaAlcoholicaFormSet,
        form=MuestraBebidaAlcoholicaForm, min_num=1, extra=0,
        validate_min=True, can_delete=True
    )

    if request.method == 'POST':
        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, data=request.POST, prefix='recepcion')
        form_informacion = InformacionBebidaAlcoholicaForm(instance=general, data=request.POST, prefix='general', usuario=request.user)
        formset_muestra = MuestraFormSet(
            queryset=BebidaAlcoholica.objects.filter(id__in=muestras),
            data=request.POST, usuario=request.user, nueva=False
        )

        if form_ingreso.is_valid() and form_informacion.is_valid():
            if formset_muestra.is_valid():
                ingreso = form_ingreso.save()
                general = form_informacion.save()
                formset_muestra.save(ingreso=ingreso, general=general)

                return redirect(reverse('trazabilidad:ingresos'))
    else:
        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, prefix='recepcion')
        form_informacion = InformacionBebidaAlcoholicaForm(instance=general, prefix='general', usuario=request.user)
        formset_muestra = MuestraFormSet(queryset=BebidaAlcoholica.objects.filter(id__in=muestras))

    data = {
        'form_ingreso': form_ingreso, 'muestra_nueva': False, 'form_informacion': form_informacion,
        'formset_muestra': formset_muestra
    }

    return render(request, 'bebidas_alcoholicas/nueva_muestra.html', data)


@login_required
@permission_required('administracion.can_ingresar_muestras_programas_ambientes')
def estado_muestra(request, id):
    """
    Permite definir el estado de la recepción de una muestra de bebidas alcoholicas.
    La muestra puede ser aceptada o rechazada.
    """

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()
    general = muestra.informacion_general

    if request.method == 'POST':
        form = EstadoIngresoForm(instance=ingreso, data=request.POST)

        if form.is_valid():
            igreso = form.save()

            return redirect(reverse('bebidas_alcoholicas:radicado_muestra', args=(id, )))
    else:
        form = EstadoIngresoForm(instance=ingreso)

    data = {
        'form': form, 'ingreso': ingreso, 'general': general, 'imprimir': False
    }
    return render(request, 'bebidas_alcoholicas/estado_muestra.html', data)


@login_required
@permission_required('administracion.can_ingresar_muestras_programas_ambientes')
def radicado_muestra(request, id):
    """Muestra el radicado."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()
    general = muestra.informacion_general

    data = {'ingreso': ingreso, 'general': general, 'imprimir': True}
    return render(request, 'bebidas_alcoholicas/estado_muestra.html', data)


@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_ambientes')
def decreto_muestras(request, id):
    """Vista para añadir los decretos a las muestras de bebidas alcoholicas."""

    muestra = get_object_or_404(BebidaAlcoholica, pk=id)
    if request.method == 'POST':
        form = MuestraDecretoForm(instance=muestra, data=request.POST)

        if form.is_valid():
            muestra = form.save()

        return JsonResponse({ 'ok': True, 'ingreso': muestra.registro_recepcion_id })


class ListaProductosGrupoView(ListAPIView):
    """Retorna los productos de un grupo especifico en formato JSON."""

    serializer_class = ProductoSerializer
    permission_class = [permissions.IsAuthenticated]

    def get_queryset(self):
        grupo = self.kwargs.get('pk')
        return Producto.objects.activos().filter(grupo_id=grupo)

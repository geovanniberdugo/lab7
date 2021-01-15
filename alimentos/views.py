from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.forms.models import modelformset_factory
from django.http import HttpResponse, JsonResponse
from rest_framework.generics import ListAPIView
from rest_framework import permissions
from django.db import transaction
from django.urls import reverse

from common.decorators import grupo_requerido
from trazabilidad.models import Recepcion
from trazabilidad.forms import RecepcionForm, Programa, EstadoIngresoForm, ActualizarRecepcionForm
from .forms import InformacionAlimentoForm, MuestraAlimentoForm, MuestraAlimentoFormSet, MuestraDecretoForm
from .serializers import SubcategoriaSerializer, CategoriaSerializer
from .models import Alimento, Subcategoria, Categoria


@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_ambientes')
def nueva_muestra(request):
    """Permite ingresar una muestra de alimento."""

    MuestraFormSet = modelformset_factory(Alimento, formset=MuestraAlimentoFormSet, form=MuestraAlimentoForm,
                                          min_num=1, extra=0, validate_min=True)

    if request.method == 'POST':
        form_ingreso = RecepcionForm(user=request.user, data=request.POST, prefix='recepcion')
        form_informacion = InformacionAlimentoForm(data=request.POST, prefix='general')
        formset_muestra = MuestraFormSet(queryset=Alimento.objects.none(), data=request.POST,
                                         usuario=request.user, nueva=True)

        if form_ingreso.is_valid() and form_informacion.is_valid():
            if formset_muestra.is_valid():
                ingreso = form_ingreso.save(commit=False)
                ingreso.recepcionista = request.user
                ingreso.programa = Programa.objects.alimentos()
                ingreso.save()

                general = form_informacion.save()
                formset_muestra.save(ingreso=ingreso, general=general)
                return redirect(reverse('alimentos:estado_muestra', args=(ingreso.id,)))
    else:
        form_ingreso = RecepcionForm(user=request.user, prefix='recepcion')
        form_informacion = InformacionAlimentoForm(prefix='general')
        formset_muestra = MuestraFormSet(queryset=Alimento.objects.none())

    data = {'form_ingreso': form_ingreso, 'muestra_nueva': True,
            'form_informacion': form_informacion, 'formset_muestra': formset_muestra}
    return render(request, 'alimentos/nueva_muestra.html', data)

@transaction.atomic
@login_required
@permission_required('administracion.can_ingresar_muestras_programas_ambientes')
def actualizar_muestra(request, id):
    """Permite actualizar una muestra de alimento."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestras = ingreso.muestras.all()
    general = muestras.first().informacion_general

    MuestraFormSet = modelformset_factory(Alimento, formset=MuestraAlimentoFormSet, form=MuestraAlimentoForm,
                                          min_num=1, extra=0, validate_min=True, can_delete=True)

    if request.method == 'POST':
        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, data=request.POST, prefix='recepcion')
        form_informacion = InformacionAlimentoForm(instance=general, data=request.POST, prefix='general')
        formset_muestra = MuestraFormSet(queryset=Alimento.objects.filter(id__in=muestras),
                                         data=request.POST, usuario=request.user, nueva=False)

        if form_ingreso.is_valid() and form_informacion.is_valid():
            if formset_muestra.is_valid():
                ingreso = form_ingreso.save()
                general = form_informacion.save()
                formset_muestra.save(ingreso=ingreso, general=general)

                return redirect(reverse('trazabilidad:ingresos'))
    else:
        form_ingreso = ActualizarRecepcionForm(user=request.user, instance=ingreso, prefix='recepcion')
        form_informacion = InformacionAlimentoForm(instance=general, prefix='general')
        formset_muestra = MuestraFormSet(queryset=Alimento.objects.filter(id__in=muestras))

    data = {'form_ingreso': form_ingreso, 'muestra_nueva': False,
            'form_informacion': form_informacion, 'formset_muestra': formset_muestra}
    return render(request, 'alimentos/nueva_muestra.html', data)

@login_required
@permission_required('administracion.can_ingresar_muestras_programas_ambientes')
def estado_muestra(request, id):
    """Permite definir el estado de la recepción de una muestra de alimento. La muestra puede ser aceptada
    o rechazada."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()
    general = muestra.informacion_general

    if request.method == 'POST':
        form = EstadoIngresoForm(instance=ingreso, data=request.POST)

        if form.is_valid():
            ingreso = form.save()

            return redirect(reverse('alimentos:radicado_muestra', args=(id,)))
    else:
        form = EstadoIngresoForm(instance=ingreso)

    data = {'form': form, 'ingreso': ingreso, 'general': general, 'imprimir': False}
    return render(request, 'alimentos/estado_muestra.html', data)

@login_required
@permission_required('administracion.can_ingresar_muestras_programas_ambientes')
def radicado_muestra(request, id):
    """Muestra el radicado."""

    ingreso = get_object_or_404(Recepcion, pk=id)
    muestra = ingreso.muestras.first()
    general = muestra.informacion_general

    data = {'ingreso': ingreso, 'general': general, 'imprimir': True}
    return render(request, 'alimentos/estado_muestra.html', data)

@transaction.atomic
def decreto_muestras(request, id):
    """Vista para agregar las pruebas de una muestra, de acuerdo a un decreto."""

    muestra = get_object_or_404(Alimento, pk=id)

    if request.method == 'POST':
        form = MuestraDecretoForm(instance=muestra, data=request.POST)

        if form.is_valid():
            muestra = form.save()
        
        return JsonResponse({ 'ok': True, 'ingreso': muestra.registro_recepcion_id })

# Json views


class ListaTiposAlimentoGrupoView(ListAPIView):
    """Devuelve los tipos de alimento de un grupo especifico en formato JSON."""

    serializer_class = SubcategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retorna los tipos de alimento del grupo especificado en la URL."""

        grupo = self.kwargs['pk']
        return Subcategoria.objects.activos().filter(categoria__grupo=grupo)


class ListaCategoriasGrupoView(ListAPIView):
    """
    Retorna las categorias de acuerdo a un grupo de alimentos especifico en formato Json
    """

    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retorna las categorias de alimentos de acuerdo a un grupo especificado en la URL."""
        grupo = self.kwargs['pk']
        return Categoria.objects.filter(grupo__id=grupo)


class ListaSubCategoriasCategoriaView(ListAPIView):
    """
    Retorna las subcategorias de acuerdo a una categoria especifico en formato Json
    """

    serializer_class = SubcategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retorna las subcategorias de alimentos de acuerdo a una categoria en la URL."""
        categoria = self.kwargs['pk']
        return Subcategoria.objects.activos().filter(categoria__id=categoria)

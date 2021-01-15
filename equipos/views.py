from django.urls import reverse
from datetime import timedelta
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from rest_framework import permissions
from rest_framework.generics import RetrieveAPIView, ListAPIView
from common.decorators import grupo_requerido
from administracion.models import Empleado
from .forms import EquiposAreaForm, EquiposForm, RegistroTemperaturaForm
from .serializers import EquipoSerializer
from .models import Equipo, RegistroTemperatura
from .utils import convertidor_unidad_temperatura


@grupo_requerido('analista', 'biofisico')
def control_temperatura(request):
    """Muestra las temperaturas registradas de los equipos usados en el laboratorio."""

    usuario = request.user
    registros = []
    equipo = None
    grafico = []
    celsius = False

    if request.method == 'POST':
        # Si es solo analista
        if usuario.groups.count() == 1 and usuario.groups.filter(name__iexact='analista').exists():
            form = EquiposForm(usuario=usuario, data=request.POST)
        else:
            form = EquiposAreaForm(data=request.POST)

        if form.is_valid():
            equipo = form.cleaned_data['equipos']
            fechai = form.cleaned_data['fecha_inicial']
            fechaf = form.cleaned_data['fecha_final']+timedelta(days=1)
            temp_max = form.cleaned_data['temperatura_maxima']
            temp_min = form.cleaned_data['temperatura_minima']
            unidad_seleccionada = form.cleaned_data['unidad']

            registros = RegistroTemperatura.objects.filter(fecha_registro__range=(fechai, fechaf), equipo=equipo)

            temp_max = convertidor_unidad_temperatura(temp_max, RegistroTemperatura.CENTIGRADOS, unidad_seleccionada)
            temp_min = convertidor_unidad_temperatura(temp_min, RegistroTemperatura.CENTIGRADOS, unidad_seleccionada)

            if unidad_seleccionada == RegistroTemperatura.FARHENHEIT:
                grafico = [['Fecha', 'Temperatura Minima(°F)', 'Temperatura Registrada(°F)', 'Temperatura Maxima(°F)']]
            else:
                celsius = True
                grafico = [['Fecha', 'Temperatura Minima(°C)', 'Temperatura Registrada(°C)', 'Temperatura Maxima(°C)']]

            for registro in reversed(registros):
                temperatura = convertidor_unidad_temperatura(registro.temperatura, registro.unidad, unidad_seleccionada)
                fecha = timezone.localtime(registro.fecha_registro)

                grafico.append([fecha.strftime("%Y-%m-%d %H:%M"), temp_min, temperatura, temp_max])

        data = {'registros': registros, 'form': form, 'celsius': celsius, 'equipo': equipo, 'grafico': grafico}

    else:
        # Si es solo analista
        if usuario.groups.count() == 1 and usuario.groups.filter(name__iexact='analista').exists():
            form = EquiposForm(usuario=usuario)
            try:
                usuario.empleado
            except Empleado.DoesNotExist:
                messages.warning(request, 'No tiene un área asignada. Por favor contacte al administrador del sistema.')
        else:
            form = EquiposAreaForm()

        data = {'form': form, 'equipo': equipo}

    return render(request, 'equipos/control_temperatura.html', data)


@grupo_requerido('analista', 'biofisico')
def registro_temperatura(request, equipo):
    """Permite ingresar la temperatura del equipo especificado usado en el laboratorio."""

    equipo = get_object_or_404(Equipo, pk=equipo)

    if request.method == 'POST':
        form = RegistroTemperaturaForm(data=request.POST, equipo=equipo)

        if form.is_valid():
            registro = form.save(commit=False)
            registro.registrado_por = request.user
            registro.equipo = equipo
            registro.save()
            return redirect(reverse('equipos:control_temperatura'))
    else:
        form = RegistroTemperaturaForm(initial={'fecha_registro': timezone.now()}, equipo=equipo)

    data = {'form': form, 'equipo': equipo}
    return render(request, 'equipos/registro_temperatura.html', data)


class DetalleEquipoView(RetrieveAPIView):
    """Devuelve un equipo en formato JSON según su id."""

    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer
    permission_classes = [permissions.IsAuthenticated]


class ListaEquiposAreaView(ListAPIView):
    """Devuelve los equipos de un área especificada en formato JSON."""

    serializer_class = EquipoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retorna los equipos del área especificada en la URL."""

        area = self.kwargs['pk']
        return Equipo.objects.filter(area=area, estado=Equipo.ACTIVO)

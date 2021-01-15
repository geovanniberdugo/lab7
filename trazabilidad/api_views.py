from rest_framework import permissions, pagination, response, generics, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib import messages

from administracion.models import Empleado
from . import serializers as se
from trazabilidad import enums
from . import models as m

class DataTablePagination(pagination.LimitOffsetPagination):

    default_limit = 10
    offset_query_param = 'start'

    def get_paginated_response(self, data):
        return response.Response({
            'data': data,
            'recordsTotal': self.count,
            'recordsFiltered': self.count,
        })

class DataTableSearchFilter(filters.SearchFilter):
    search_param = 'search[value]'

class IngresosPendientesAPIView(generics.ListAPIView):

    search_fields = ['indice_radicado']
    pagination_class = DataTablePagination
    filter_backends = [DataTableSearchFilter]
    serializer_class = se.RecepcionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        ingresos_covid = m.Recepcion.objects.by_programa_covid()
        ingresos_no_covid = m.Recepcion.objects.confirmados().exclude_programa_covid()
        ingresos = (ingresos_covid | ingresos_no_covid).aceptados_recepcionista().estado_analista_sin_llenar()

        if not user.has_perm('administracion.can_analizar_todos_programas'):
            try:
                ingresos = ingresos.by_areas(user.empleado.areas.all())
            except Empleado.DoesNotExist:
                messages.warning(request, 'No tiene un área asignada. Por favor contacte al administrador del sistema.')
                ingresos = ingresos.none()

        return ingresos.prefetch_related('muestras').select_related('programa')

class IngresosEnCursoAPIView(generics.ListAPIView):

    search_fields = ['indice_radicado']
    pagination_class = DataTablePagination
    filter_backends = [DataTableSearchFilter]
    serializer_class = se.RecepcionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        ingresos_covid = m.Recepcion.objects.by_programa_covid()
        ingresos_no_covid = m.Recepcion.objects.confirmados().exclude_programa_covid()
        ingresos = (ingresos_covid | ingresos_no_covid).aceptados_recepcionista().aceptados_analista()

        if not user.has_perm('administracion.can_analizar_todos_programas'):
            try:
                ingresos = ingresos.by_areas(user.empleado.areas.all())
            except Empleado.DoesNotExist:
                messages.warning(request, 'No tiene un área asignada. Por favor contacte al administrador del sistema.')
                ingresos = ingresos.none()

        # Ingresos sin reporte confirmado
        ingresos_reporte_confirmados = m.Reporte.objects.confirmados().values_list('registro_recepcion', flat=True)
        return ingresos.exclude(id__in=ingresos_reporte_confirmados).select_related('programa')

class IngresosConResultadoAPIView(generics.ListAPIView):

    search_fields = ['indice_radicado']
    pagination_class = DataTablePagination
    filter_backends = [DataTableSearchFilter]
    serializer_class = se.RecepcionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        ingresos_covid = m.Recepcion.objects.by_programa_covid()
        ingresos_no_covid = m.Recepcion.objects.confirmados().exclude_programa_covid()
        ingresos = (ingresos_covid | ingresos_no_covid).aceptados_recepcionista().aceptados_analista()

        # Cuando NO es super usuario se filtra dependiendo del area a la que pertenezca el usuario
        if not user.has_perm('administracion.can_analizar_todos_programas'):
            try:
                ingresos = ingresos.by_areas(user.empleado.areas.all())
            except Empleado.DoesNotExist:
                messages.warning(request, 'No tiene un área asignada. Por favor contacte al administrador del sistema.')
                ingresos = ingresos.none()

        ingresos_reporte_confirmados = m.Reporte.objects.confirmados().values_list('registro_recepcion', flat=True)
        return ingresos.filter(id__in=ingresos_reporte_confirmados).ultimos_treinta_dias()

class IngresosRecepcionadosParcialesAPIView(generics.ListAPIView):
    
    search_fields = ['indice_radicado']
    pagination_class = DataTablePagination
    filter_backends = [DataTableSearchFilter]
    serializer_class = se.RecepcionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        ingresos = m.Ingreso.objects.select_related('programa').all()

        if not user.has_perm('administracion.can_ingresar_muestras_programas_clinicos'):
            ingresos = ingresos.exclude_programa_clinicos()

        if not user.has_perm('administracion.can_ingresar_muestras_programas_ambientes'):
            ingresos = ingresos.exclude_programa_ambientes()

        return ingresos.parciales()

class IngresosRecepcionadosEnCursoAPIView(generics.ListAPIView):
    
    search_fields = ['indice_radicado']
    pagination_class = DataTablePagination
    filter_backends = [DataTableSearchFilter]
    serializer_class = se.RecepcionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        ingresos = m.Ingreso.objects.select_related('programa').all()

        if not user.has_perm('administracion.can_ingresar_muestras_programas_clinicos'):
            ingresos = ingresos.exclude_programa_clinicos()

        if not user.has_perm('administracion.can_ingresar_muestras_programas_ambientes'):
            ingresos = ingresos.exclude_programa_ambientes()

        return ingresos.confirmados().no_rechazados_recepcionista()

class IngresosRecepcionadosRechazadosRecepcionAPIView(generics.ListAPIView):
    
    search_fields = ['indice_radicado']
    pagination_class = DataTablePagination
    filter_backends = [DataTableSearchFilter]
    serializer_class = se.RecepcionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        ingresos = m.Ingreso.objects.select_related('programa').all()

        if not user.has_perm('administracion.can_ingresar_muestras_programas_clinicos'):
            ingresos = ingresos.exclude_programa_clinicos()

        if not user.has_perm('administracion.can_ingresar_muestras_programas_ambientes'):
            ingresos = ingresos.exclude_programa_ambientes()

        return ingresos.rechazados_recepcionista()

class IngresosRecepcionadosRechazadosAnalistaAPIView(generics.ListAPIView):
    
    search_fields = ['indice_radicado']
    pagination_class = DataTablePagination
    filter_backends = [DataTableSearchFilter]
    serializer_class = se.RecepcionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        ingresos = m.Ingreso.objects.select_related('programa').all()

        if not user.has_perm('administracion.can_ingresar_muestras_programas_clinicos'):
            ingresos = ingresos.exclude_programa_clinicos()

        if not user.has_perm('administracion.can_ingresar_muestras_programas_ambientes'):
            ingresos = ingresos.exclude_programa_ambientes()

        return ingresos.rechazados_analista().prefetch_related('motivo_rechazo_analista')

class IngresosRecepcionadosResultadoAPIView(generics.ListAPIView):
    
    search_fields = ['indice_radicado']
    pagination_class = DataTablePagination
    filter_backends = [DataTableSearchFilter]
    serializer_class = se.RecepcionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        ingresos = m.Ingreso.objects.select_related('programa').all()

        if not user.has_perm('administracion.can_ingresar_muestras_programas_clinicos'):
            ingresos = ingresos.exclude_programa_clinicos()

        if not user.has_perm('administracion.can_ingresar_muestras_programas_ambientes'):
            ingresos = ingresos.exclude_programa_ambientes()

        ingresos_reporte_confirmados = m.Reporte.objects.confirmados().values_list('registro_recepcion', flat=True)
        return ingresos.filter(id__in=ingresos_reporte_confirmados).ultimos_treinta_dias()

class AprobarInformeResultadosAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        serializer = se.AprobarInformeResultadosSerializer(data=request.data)
        if serializer.is_valid():
            serializer.aprove()
            return Response({'ok': True}, status=200)

        return Response(serializer.errors, status=400)

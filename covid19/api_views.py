from rest_framework import permissions, filters, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from trazabilidad.models import Paciente
from . import serializers as se
from . import models as m

class DetalleInfoPacienteView(generics.ListAPIView):
    """Devuelve un paciente en formato JSON según su identificación."""

    search_fields = ['=identificacion']
    serializer_class = se.PacienteSerializer
    filter_backends = [filters.SearchFilter]
    queryset = Paciente.objects.prefetch_related('infos_covid19').all().order_by('id')

class Cie10ListView(generics.ListAPIView):
    """Devuelve codigos cie10 en formato JSON según su codigo o descripción."""

    queryset = se.CIE10.objects.all()
    serializer_class = se.Cie10Serializer
    search_fields = ['code', 'description']
    filter_backends = [filters.SearchFilter]

class UpgdListView(generics.ListAPIView):
    """Devuelve codigos upgd en formato JSON según su nombre."""

    search_fields = ['nombre']
    queryset = m.Upgd.objects.all()
    serializer_class = se.UpgdSerializer
    filter_backends = [filters.SearchFilter]
    permission_classes = [permissions.IsAuthenticated]

class SendResultsEmailView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        serializer = se.SendResultsEmailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.send(request)
            return Response({ 'ok': True }, status=200)

        return Response(serializer.errors, status=400)

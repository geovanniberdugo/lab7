from django.contrib.sites.models import Site


def site(request):
    sites = Site.objects.get_current()
    return {'sitio': sites, 'dominio': sites.domain, 'nombre': sites.name}

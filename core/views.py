from django.shortcuts import render
from .models import Seccion, Capitulo, Arancel

def buscador_aranceles(request):
    capitulo = request.GET.get('capitulo')
    partida = request.GET.get('partida')
    subpartida = request.GET.get('subpartida')
    tarifa = request.GET.get('tarifa')

    aranceles = Arancel.objects.all()

    if capitulo:
        aranceles = aranceles.filter(capitulo=capitulo)
    if partida:
        aranceles = aranceles.filter(partida=partida)
    if subpartida:
        aranceles = aranceles.filter(subpartida=subpartida)
    if tarifa:
        aranceles = aranceles.filter(tarifa=tarifa)

    capitulos = Arancel.objects.values_list('capitulo', flat=True).distinct()
    partidas = aranceles.values_list('partida', flat=True).distinct()
    subpartidas = aranceles.values_list('subpartida', flat=True).distinct()
    tarifas = aranceles.values_list('tarifa', flat=True).distinct()

    secciones = Seccion.objects.all()

    return render(request, 'core/Buscadoraduanas.html', {
        'aranceles': aranceles,
        'capitulos': capitulos,
        'partidas': partidas,
        'subpartidas': subpartidas,
        'tarifas': tarifas,
        'filtro': {
            'capitulo': capitulo,
            'partida': partida,
            'subpartida': subpartida,
            'tarifa': tarifa,
        },
        'secciones': secciones,
    })

def busqueda_view(request):
    secciones = Seccion.objects.all().order_by('titulo')
    capitulos = Capitulo.objects.all().order_by('titulo')
    aranceles = Arancel.objects.all().order_by('capituloaranc__titulo', 'codigo')
    return render(request, 'core/Buscadoraduanas.html', {
        'secciones': secciones,
        'capitulos': capitulos,
        'aranceles': aranceles,
    })



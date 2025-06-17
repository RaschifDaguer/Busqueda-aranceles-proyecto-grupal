from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import LoginForm, DespachanteForm, ArancelForm
from .models import Seccion, Capitulo, Arancel, HistorialBusqueda, CustomUser
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST, require_GET
from django.template.loader import render_to_string

def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'gerente':
            return redirect('aranceles')
        elif request.user.role == 'despachante':
            return redirect('busqueda')
    error = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].strip()
            credencial = form.cleaned_data['credencial'].strip()
            try:
                user = CustomUser.objects.get(username=username, credencial=credencial)
            except CustomUser.DoesNotExist:
                user = None
            if user is not None and user.is_active:
                # Refuerza el rol y permisos para gerentes
                if user.role == 'gerente' and not user.is_staff:
                    user.is_staff = True
                    user.save()
                login(request, user)
                if user.role == 'gerente':
                    return redirect('aranceles')
                elif user.role == 'despachante':
                    return redirect('busqueda')
                else:
                    error = 'Usuario sin rol asignado. Contacte al administrador.'
            else:
                error = 'Credenciales incorrectas, usuario inactivo o sin permisos.'
        else:
            error = 'Formulario inválido. Revisa los datos ingresados.'
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form, 'error': error})

def logout_view(request):
    # Solo cierra la sesión del usuario, no destruye toda la sesión
    logout(request)
    # Redirige al login y evita caché
    response = redirect('login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

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

def gerente_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'gerente':
            if request.user.role == 'despachante':
                return redirect('busqueda')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def despachante_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'despachante':
            if request.user.role == 'gerente':
                return redirect('aranceles')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@despachante_required
def busqueda_view(request):
    secciones = Seccion.objects.all().order_by('titulo')
    capitulos = Capitulo.objects.all().order_by('titulo')
    aranceles = Arancel.objects.all().order_by('capituloaranc__titulo', 'codigo')
    return render(request, 'core/Buscadoraduanas.html', {
        'secciones': secciones,
        'capitulos': capitulos,
        'aranceles': aranceles,
    })

def busqueda_avanzada(request):
    query = request.GET.get('q', '').strip()
    aranceles = Arancel.objects.all()
    resultados = []
    mensaje = ''
    if query:
        # Buscar por código (en todos los campos relevantes) o descripción
        aranceles = aranceles.filter(
            Q(codigo__icontains=query) |
            Q(capituloaranc__titulo__icontains=query) |
            Q(partida__icontains=query) |
            Q(subpartida__icontains=query) |
            Q(subpartida_nacional__icontains=query) |
            Q(desagregacion_nacional__icontains=query) |
            Q(descripcion__icontains=query)
        ).distinct()
        if not aranceles.exists():
            mensaje = 'Arancel de producto no encontrado'
        # Guardar historial si es despachante
        if request.user.is_authenticated and request.user.role == 'despachante':
            HistorialBusqueda.objects.create(usuario=request.user, termino=query)
    secciones = Seccion.objects.all().order_by('titulo')
    capitulos = Capitulo.objects.all().order_by('titulo')
    return render(request, 'core/Buscadoraduanas.html', {
        'secciones': secciones,
        'capitulos': capitulos,
        'aranceles': aranceles,
        'busqueda_query': query,
        'busqueda_mensaje': mensaje,
    })

def busqueda_codigo(request):
    query = request.GET.get('codigo', '').strip()
    aranceles = Arancel.objects.all()
    mensaje = ''
    if query:
        aranceles = aranceles.filter(
            Q(codigo__icontains=query) |
            Q(capituloaranc__titulo__icontains=query) |
            Q(partida__icontains=query) |
            Q(subpartida__icontains=query) |
            Q(subpartida_nacional__icontains=query) |
            Q(desagregacion_nacional__icontains=query)
        ).distinct()
        if not aranceles.exists():
            mensaje = 'Arancel de producto no encontrado por código'
        # Guardar historial si es despachante
        if request.user.is_authenticated and request.user.role == 'despachante':
            HistorialBusqueda.objects.create(usuario=request.user, termino=query)
    secciones = Seccion.objects.all().order_by('titulo')
    capitulos = Capitulo.objects.all().order_by('titulo')
    return render(request, 'core/Buscadoraduanas.html', {
        'secciones': secciones,
        'capitulos': capitulos,
        'aranceles': aranceles,
        'busqueda_codigo': query,
        'busqueda_codigo_mensaje': mensaje,
    })

def busqueda_descripcion(request):
    query = request.GET.get('descripcion', '').strip()
    aranceles = Arancel.objects.all()
    mensaje = ''
    if query:
        aranceles = aranceles.filter(
            Q(descripcion__icontains=query)
        ).distinct()
        if not aranceles.exists():
            mensaje = 'Arancel de producto no encontrado por descripción'
        # Guardar historial si es despachante
        if request.user.is_authenticated and request.user.role == 'despachante':
            HistorialBusqueda.objects.create(usuario=request.user, termino=query)
    secciones = Seccion.objects.all().order_by('titulo')
    capitulos = Capitulo.objects.all().order_by('titulo')
    return render(request, 'core/Buscadoraduanas.html', {
        'secciones': secciones,
        'capitulos': capitulos,
        'aranceles': aranceles,
        'busqueda_descripcion': query,
        'busqueda_descripcion_mensaje': mensaje,
    })

def autocompletar_arancel(request):
    term = request.GET.get('term', '').strip()
    sugerencias = []
    if term:
        aranceles = Arancel.objects.filter(
            Q(codigo__icontains=term) |
            Q(capituloaranc__titulo__icontains=term) |
            Q(partida__icontains=term) |
            Q(subpartida__icontains=term) |
            Q(subpartida_nacional__icontains=term) |
            Q(desagregacion_nacional__icontains=term) |
            Q(descripcion__icontains=term)
        ).distinct()[:10]
        for a in aranceles:
            sugerencias.append({
                'id': a.id,
                'codigo': a.codigo,
                'descripcion': a.descripcion,
            })
    return JsonResponse(sugerencias, safe=False)

def autocompletar_codigo(request):
    term = request.GET.get('term', '').strip()
    sugerencias = []
    if term:
        aranceles = Arancel.objects.filter(
            Q(codigo__icontains=term) |
            Q(capituloaranc__titulo__icontains=term) |
            Q(partida__icontains=term) |
            Q(subpartida__icontains=term) |
            Q(subpartida_nacional__icontains=term) |
            Q(desagregacion_nacional__icontains=term)
        ).distinct()[:10]
        for a in aranceles:
            sugerencias.append({
                'id': a.id,
                'codigo': a.codigo,
                'descripcion': a.descripcion,
            })
    return JsonResponse(sugerencias, safe=False)

def autocompletar_descripcion(request):
    term = request.GET.get('term', '').strip()
    sugerencias = []
    if term:
        aranceles = Arancel.objects.filter(
            Q(descripcion__icontains=term)
        ).distinct()[:10]
        for a in aranceles:
            sugerencias.append({
                'id': a.id,
                'codigo': a.codigo,
                'descripcion': a.descripcion,
            })
    return JsonResponse(sugerencias, safe=False)

def busqueda_combinada(request):
    codigo = request.GET.get('codigo', '').strip()
    descripcion = request.GET.get('descripcion', '').strip()
    aranceles = Arancel.objects.all()
    mensaje = ''
    if codigo:
        aranceles = aranceles.filter(
            Q(codigo__icontains=codigo) |
            Q(capituloaranc__titulo__icontains=codigo) |
            Q(partida__icontains=codigo) |
            Q(subpartida__icontains=codigo) |
            Q(subpartida_nacional__icontains=codigo) |
            Q(desagregacion_nacional__icontains=codigo)
        )
    if descripcion:
        aranceles = aranceles.filter(
            Q(descripcion__icontains=descripcion)
        )
    aranceles = aranceles.distinct()
    if (codigo or descripcion) and not aranceles.exists():
        mensaje = 'Arancel de producto no encontrado'
    # Guardar historial si es despachante
    if request.user.is_authenticated and request.user.role == 'despachante':
        termino = f"{codigo} {descripcion}".strip()
        if termino:
            HistorialBusqueda.objects.create(usuario=request.user, termino=termino)
    secciones = Seccion.objects.all().order_by('titulo')
    capitulos = Capitulo.objects.all().order_by('titulo')
    return render(request, 'core/Buscadoraduanas.html', {
        'secciones': secciones,
        'capitulos': capitulos,
        'aranceles': aranceles,
        'busqueda_codigo': codigo,
        'busqueda_descripcion': descripcion,
        'busqueda_mensaje': mensaje,
    })

@gerente_required
def aranceles_panel(request):
    aranceles = Arancel.objects.select_related('capituloaranc').all().order_by('capituloaranc__titulo', 'codigo')
    form = ArancelForm()
    return render(request, 'core/aranceles.html', {'aranceles': aranceles, 'form': form})

@gerente_required
@require_POST
def arancel_create(request):
    form = ArancelForm(request.POST)
    if form.is_valid():
        arancel = form.save()
        html = render_to_string('core/partials/arancel_row.html', {'arancel': arancel})
        return JsonResponse({'success': True, 'html': html, 'message': 'Arancel creado correctamente.'})
    # Mostrar todos los errores, incluyendo duplicados
    error_list = []
    for field, errors in form.errors.items():
        for error in errors:
            error_list.append(f"{form.fields.get(field).label if field in form.fields else field}: {error}")
    if form.non_field_errors():
        error_list += [str(e) for e in form.non_field_errors()]
    return JsonResponse({'success': False, 'errors': error_list})

@gerente_required
@require_POST
def arancel_edit(request, pk):
    arancel = Arancel.objects.get(pk=pk)
    form = ArancelForm(request.POST, instance=arancel)
    if form.is_valid():
        arancel = form.save()
        html = render_to_string('core/partials/arancel_row.html', {'arancel': arancel})
        return JsonResponse({'success': True, 'html': html, 'message': 'Arancel editado correctamente.'})
    error_list = []
    for field, errors in form.errors.items():
        for error in errors:
            error_list.append(f"{form.fields.get(field).label if field in form.fields else field}: {error}")
    if form.non_field_errors():
        error_list += [str(e) for e in form.non_field_errors()]
    return JsonResponse({'success': False, 'errors': error_list})

@gerente_required
@require_POST
def arancel_delete(request, pk):
    arancel = Arancel.objects.get(pk=pk)
    arancel.delete()
    return JsonResponse({'success': True})

@gerente_required
@require_GET
def arancel_form(request, pk=None):
    if pk:
        arancel = Arancel.objects.get(pk=pk)
        form = ArancelForm(instance=arancel)
    else:
        form = ArancelForm()
    html = render_to_string('core/partials/arancel_form_fields.html', {'form': form}, request=request)
    return JsonResponse({'html': html})

@gerente_required
def despachantes_panel(request):
    despachantes = CustomUser.objects.filter(role='despachante').order_by('username')
    form = DespachanteForm()
    return render(request, 'core/despachantes.html', {'despachantes': despachantes, 'form': form})

@gerente_required
@require_POST
def despachante_create(request):
    form = DespachanteForm(request.POST)
    if form.is_valid():
        despachante = form.save()
        html = render_to_string('core/partials/despachante_row.html', {'despachante': despachante})
        return JsonResponse({'success': True, 'html': html, 'message': 'Despachante creado correctamente.'})
    error_list = []
    for field, errors in form.errors.items():
        for error in errors:
            error_list.append(f"{form.fields.get(field).label if field in form.fields else field}: {error}")
    if form.non_field_errors():
        error_list += [str(e) for e in form.non_field_errors()]
    return JsonResponse({'success': False, 'errors': error_list})

@gerente_required
@require_POST
def despachante_delete(request, pk):
    despachante = CustomUser.objects.get(pk=pk, role='despachante')
    despachante.delete()
    return JsonResponse({'success': True})

@gerente_required
def historial_panel(request):
    despachantes = CustomUser.objects.filter(role='despachante').order_by('username')
    usuario_id = request.GET.get('usuario')
    historial = HistorialBusqueda.objects.select_related('usuario').order_by('-fecha')
    if usuario_id:
        historial = historial.filter(usuario_id=usuario_id)
    return render(request, 'core/historial.html', {
        'despachantes': despachantes,
        'historial': historial,
        'usuario_id': usuario_id,
    })



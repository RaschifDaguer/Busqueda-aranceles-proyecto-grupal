from django.db import models

class Seccion(models.Model):
    titulo = models.CharField(max_length=10, verbose_name="Título de Sección")  # Ej: 1, 2, 3...
    descripcion = models.TextField(verbose_name="Descripción")
    notas = models.TextField(verbose_name="Notas", blank=True, null=True)
    notas_complementarias_nandina = models.TextField(verbose_name="Notas Complementarias NANDINA", blank=True, null=True)

    def __str__(self):
        return f"Sección {self.titulo}"

class Capitulo(models.Model):
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name="capitulos")
    titulo = models.CharField(max_length=10, verbose_name="Capítulo")  # Ej: 01, 02, etc.
    descripcion = models.TextField(verbose_name="Descripción")
    nota = models.TextField(verbose_name="Nota", blank=True, null=True)

    def __str__(self):
        return f"Capítulo {self.titulo}"

class DocumentosAdicionales(models.Model):
    tipo_doc = models.CharField(max_length=50, verbose_name="Tipo de Doc")
    entidad_emite = models.CharField(max_length=100, verbose_name="Entidad que emite")
    disp_legal = models.CharField(max_length=255, verbose_name="Disp. Legal")

    def __str__(self):
        return f"{self.tipo_doc} - {self.entidad_emite}"

class PreferenciasArancelarias(models.Model):
    can = models.CharField(max_length=50, verbose_name="CAN", blank=True, null=True)
    ace_36 = models.CharField(max_length=50, verbose_name="ACE 36", blank=True, null=True)
    ace_47 = models.CharField(max_length=50, verbose_name="ACE 47", blank=True, null=True)
    ven = models.CharField(max_length=50, verbose_name="VEN", blank=True, null=True)

    def __str__(self):
        if self.can == '100' or self.ace_36 == '100' or self.ace_47 == '100' or self.ven == '100':
            return '100'
        return ''

class ACE22(models.Model):
    chi = models.CharField(max_length=50, verbose_name="Chi", blank=True, null=True)
    prot = models.CharField(max_length=50, verbose_name="Prot", blank=True, null=True)

    def __str__(self):
        return f"Chi: {self.chi}, Prot: {self.prot}"

class ACE66Mexico(models.Model):
    ace_66_mexico = models.CharField(max_length=100, verbose_name="ACE 66 / México", blank=True, null=True)

    def __str__(self):
        return self.ace_66_mexico or ""

class Arancel(models.Model):
    # El campo 'codigo' sigue existiendo pero no se mostrará en el admin
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código completo", blank=True)
    capituloaranc = models.ForeignKey(Capitulo, on_delete=models.CASCADE, verbose_name="Capítulo")
    partida = models.CharField(max_length=4, verbose_name="Partida", blank=True, null=True)
    subpartida = models.CharField(max_length=4, verbose_name="Subpartida", blank=True, null=True)
    subpartida_nacional = models.CharField(max_length=6, verbose_name="Subpartida Nacional", blank=True, null=True)
    desagregacion_nacional = models.CharField(max_length=10, verbose_name="Desagregación Nacional", blank=True, null=True)
    descripcion = models.CharField(max_length=255, verbose_name="Descripción de la Mercancía", blank=True, null=True)
    ga = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="GA %", blank=True, null=True)
    ice = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="ICE %", blank=True, null=True)
    unidad_medida = models.CharField(max_length=50, verbose_name="Unidad de Medida", blank=True, null=True)
    despacho_frontera = models.CharField(max_length=100, verbose_name="Despacho en Frontera", blank=True, null=True)
    documentos_adicionales = models.ForeignKey(DocumentosAdicionales, on_delete=models.SET_NULL, null=True, blank=True)
    preferencias_arancelarias = models.ForeignKey(PreferenciasArancelarias, on_delete=models.SET_NULL, null=True, blank=True)
    ace22 = models.ForeignKey(ACE22, on_delete=models.SET_NULL, null=True, blank=True)
    ace66_mexico = models.ForeignKey(ACE66Mexico, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Formatear el capítulo a dos dígitos para el código
        capitulo = f"{int(self.capituloaranc.titulo):02}" if self.capituloaranc and self.capituloaranc.titulo.isdigit() else (self.capituloaranc.titulo if self.capituloaranc else '')
        partida = f"{self.partida}." if self.partida else ''
        subpartida = f"{self.subpartida}." if self.subpartida else ''
        subpartida_nacional = f"{self.subpartida_nacional}." if self.subpartida_nacional else ''
        desagregacion = self.desagregacion_nacional or ''
        self.codigo = f"{capitulo}{partida}{subpartida}{subpartida_nacional}{desagregacion}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.capituloaranc} - {self.descripcion}"

# ...no cambies nada más aquí...

from django.contrib import admin
from .models import Seccion, Capitulo, DocumentosAdicionales, PreferenciasArancelarias, ACE22, ACE66Mexico, Arancel

@admin.register(Arancel)
class ArancelAdmin(admin.ModelAdmin):
    exclude = ('codigo',)

admin.site.register(Seccion)
admin.site.register(Capitulo)
admin.site.register(DocumentosAdicionales)
admin.site.register(PreferenciasArancelarias)
admin.site.register(ACE22)
admin.site.register(ACE66Mexico)

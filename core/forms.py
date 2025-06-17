from django import forms
from .models import CustomUser, Arancel

class LoginForm(forms.Form):
    username = forms.CharField(label='Nombre de usuario', max_length=150)
    credencial = forms.CharField(label='Credencial (6 dígitos)', max_length=6, min_length=6, widget=forms.PasswordInput)

    def clean_credencial(self):
        credencial = self.cleaned_data['credencial'].strip()
        if not credencial.isdigit() or len(credencial) != 6:
            raise forms.ValidationError('La credencial debe ser un número de 6 dígitos.')
        return credencial

    def clean_username(self):
        return self.cleaned_data['username'].strip()

class DespachanteForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'credencial', 'role']
        widgets = {
            'credencial': forms.PasswordInput(),
            'role': forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].initial = 'despachante'
        self.fields['role'].required = True

class ArancelForm(forms.ModelForm):
    class Meta:
        model = Arancel
        fields = [
            'capituloaranc', 'partida', 'subpartida', 'subpartida_nacional',
            'desagregacion_nacional', 'descripcion', 'ga', 'ice', 'unidad_medida',
            'despacho_frontera', 'documentos_adicionales', 'preferencias_arancelarias',
            'ace22', 'ace66_mexico'
        ]
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'unidad_medida': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        capituloaranc = cleaned_data.get('capituloaranc')
        partida = cleaned_data.get('partida')
        subpartida = cleaned_data.get('subpartida')
        subpartida_nacional = cleaned_data.get('subpartida_nacional')
        desagregacion_nacional = cleaned_data.get('desagregacion_nacional')
        # Generar el código como en el modelo
        capitulo = f"{int(capituloaranc.titulo):02}" if capituloaranc and capituloaranc.titulo.isdigit() else (capituloaranc.titulo if capituloaranc else '')
        codigo = f"{capitulo}{partida or ''}{subpartida or ''}{subpartida_nacional or ''}{desagregacion_nacional or ''}"
        qs = Arancel.objects.filter(codigo=codigo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un arancel con ese código. No se permiten duplicados.')
        return cleaned_data

class GerenteForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'credencial', 'role', 'is_staff']
        widgets = {
            'credencial': forms.PasswordInput(),
            'role': forms.HiddenInput(),
            'is_staff': forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].initial = 'gerente'
        self.fields['role'].required = True
        self.fields['is_staff'].initial = True
        self.fields['is_staff'].required = True
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.role = 'gerente'
        instance.is_staff = True
        if commit:
            instance.save()
        return instance

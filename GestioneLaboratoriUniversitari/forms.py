from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
import re

class BaseUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label="Nome")
    last_name = forms.CharField(label="Cognome")
    matricola = forms.CharField(max_length=6, min_length=6, help_text="6 caratteri. Es: P12345, S12345, T12345")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']


class ProfessoreForm(BaseUserForm):
    dipartimento = forms.CharField(max_length=100)
    materia = forms.CharField(max_length=100)

    def clean_matricola(self):
        matricola = self.cleaned_data['matricola']
        if not re.match(r'^P\d{5}$', matricola):
            raise forms.ValidationError("Matricola non valida.")
        return matricola

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['matricola']
        if commit:
            user.save()
            Profilo.objects.create(user=user, ruolo='professore', matricola=self.cleaned_data['matricola'])
            Professore.objects.create(user=user, dipartimento=self.cleaned_data['dipartimento'], materia=self.cleaned_data['materia'])
        return user


class StudenteForm(BaseUserForm):
    corso_laurea = forms.CharField(max_length=100)
    anno = forms.IntegerField()

    def clean_matricola(self):
        matricola = self.cleaned_data['matricola']
        if not re.match(r'^S\d{5}$', matricola):
            raise forms.ValidationError("Matricola non valida.")
        return matricola

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['matricola']
        if commit:
            user.save()
            Profilo.objects.create(user=user, ruolo='studente', matricola=self.cleaned_data['matricola'])
            Studente.objects.create(user=user, corso_laurea=self.cleaned_data['corso_laurea'], anno=self.cleaned_data['anno'])
        return user


class TecnicoForm(BaseUserForm):
    area_competenza = forms.CharField(max_length=100)
    responsabile_laboratorio = forms.BooleanField(required=False)

    def clean_matricola(self):
        matricola = self.cleaned_data['matricola']
        if not re.match(r'^T\d{5}$', matricola):
            raise forms.ValidationError("Matricola non valida.")
        return matricola

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['matricola']
        if commit:
            user.save()
            Profilo.objects.create(user=user, ruolo='tecnico', matricola=self.cleaned_data['matricola'])
            Tecnico.objects.create(user=user, area_competenza=self.cleaned_data['area_competenza'], responsabile_laboratorio=self.cleaned_data['responsabile_laboratorio'])
        return user



class ProgettoForm(forms.ModelForm):
    class Meta:
        model = ProgettoSperimentale
        fields = ['titolo', 'descrizione', 'obiettivi', 'data_inizio', 'data_fine']
        widgets = {
            'data_inizio': forms.DateInput(attrs={'type': 'date'}),
            'data_fine': forms.DateInput(attrs={'type': 'date'}),
        }


from django import forms
from .models import Esperimento, Laboratorio, Attrezzatura, PrenotazioneLaboratorio, PrenotazioneAttrezzatura
from django.core.exceptions import ValidationError

class EsperimentoForm(forms.ModelForm):
    laboratorio = forms.ModelChoiceField(queryset=Laboratorio.objects.all(), label="Laboratorio")
    attrezzature = forms.ModelMultipleChoiceField(
        queryset=Attrezzatura.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Attrezzature"
    )
    data = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    ora_inizio = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    ora_fine = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Esperimento
        fields = [
            'titolo', 'descrizione', 'obiettivi', 'materiali',
            'data_inizio', 'data_fine',
            'laboratorio', 'attrezzature',
            'data', 'ora_inizio', 'ora_fine'
        ]
        widgets = {
            'data_inizio': forms.DateInput(attrs={'type': 'date'}),
            'data_fine': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        laboratorio = cleaned_data.get('laboratorio')
        attrezzature = cleaned_data.get('attrezzature')
        data = cleaned_data.get('data')
        ora_inizio = cleaned_data.get('ora_inizio')
        ora_fine = cleaned_data.get('ora_fine')

        if laboratorio and data and ora_inizio and ora_fine:
            # Verifica conflitti con prenotazioni laboratorio
            if PrenotazioneLaboratorio.objects.filter(
                laboratorio=laboratorio,
                data=data,
                ora_inizio__lt=ora_fine,
                ora_fine__gt=ora_inizio
            ).exists():
                raise ValidationError("Il laboratorio è già prenotato per l'orario selezionato.")

        if attrezzature and data and ora_inizio and ora_fine:
            for att in attrezzature:
                if PrenotazioneAttrezzatura.objects.filter(
                    attrezzatura=att,
                    data=data,
                    ora_inizio__lt=ora_fine,
                    ora_fine__gt=ora_inizio
                ).exists():
                    raise ValidationError(f"L'attrezzatura '{att.nome}' è già prenotata nell'orario selezionato.")

        return cleaned_data

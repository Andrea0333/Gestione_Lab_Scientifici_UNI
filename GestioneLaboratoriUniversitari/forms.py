# forms.py

from django import forms
from .models import *
from django.contrib.auth.hashers import make_password  # Importiamo solo la funzione per l'hashing
import re


# --- Form di Base modificato per non usare UserCreationForm ---
class BaseUserRegistrationForm(forms.ModelForm):
    # Aggiungiamo manualmente i campi per la password, che ModelForm non ha.
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        help_text="La password verrà salvata in modo sicuro."
    )
    password2 = forms.CharField(
        label='Conferma Password',
        widget=forms.PasswordInput,
        help_text="Inserisci di nuovo la password per conferma."
    )

    class Meta:
        model = Utente
        # Campi del modello che vogliamo mostrare automaticamente nel form.
        # Escludiamo il campo 'password' del modello, perché lo gestiamo noi.
        fields = ('matricola', 'nome', 'cognome', 'email')

    def clean_password2(self):
        # Controlliamo che le due password inserite nel form coincidano.
        cd = self.cleaned_data
        if 'password' in cd and 'password2' in cd:
            if cd['password'] != cd['password2']:
                raise forms.ValidationError('Le password non corrispondono.')
        return cd.get('password2')

    def save(self, commit=True):
        # Creiamo l'istanza del modello ma non la salviamo ancora sul database.
        user = super().save(commit=False)

        # Hashiamo la password presa dal form e la impostiamo sull'utente.
        # Questa è la parte di sicurezza che ora gestiamo manualmente.
        user.password = make_password(self.cleaned_data['password'])

        if commit:
            user.save()
        return user


# --- Form specifico per il Professore ---
# Eredita dal nostro nuovo form di base. Il nome è stato cambiato per coerenza.
class ProfessoreForm(BaseUserRegistrationForm):
    dipartimento = forms.CharField(max_length=100)
    materia = forms.CharField(max_length=100)

    def clean_matricola(self):
        matricola = self.cleaned_data.get('matricola')
        if not re.match(r'^P\d{5}$', matricola):
            raise forms.ValidationError("Formato matricola non valido. Deve essere P seguita da 5 cifre (es. P12345).")
        if Utente.objects.filter(matricola=matricola).exists():
            raise forms.ValidationError("Questa matricola è già stata registrata.")
        return matricola

    def save(self, commit=True):
        # Chiama il save del genitore (BaseUserRegistrationForm) per ottenere
        # l'istanza dell'utente con la password già hashata.
        user = super().save(commit=False)

        # Imposta il ruolo e i campi specifici del professore.
        user.ruolo = Ruolo.PROFESSORE
        user.dipartimento = self.cleaned_data.get('dipartimento')
        user.materia = self.cleaned_data.get('materia')

        if commit:
            user.save()
        return user


# --- Form specifico per lo Studente ---
class StudenteForm(BaseUserRegistrationForm):
    corso_di_studi = forms.CharField(max_length=100)
    anno = forms.IntegerField(min_value=1, max_value=5)

    def clean_matricola(self):
        matricola = self.cleaned_data.get('matricola')
        if not re.match(r'^S\d{5}$', matricola):
            raise forms.ValidationError("Formato matricola non valido. Deve essere S seguita da 5 cifre (es. S12345).")
        if Utente.objects.filter(matricola=matricola).exists():
            raise forms.ValidationError("Questa matricola è già stata registrata.")
        return matricola

    def save(self, commit=True):
        user = super().save(commit=False)
        user.ruolo = Ruolo.STUDENTE
        user.corso_di_studi = self.cleaned_data.get('corso_di_studi')
        user.anno = self.cleaned_data.get('anno')

        if commit:
            user.save()
        return user


# --- Form specifico per il Tecnico ---
class TecnicoForm(BaseUserRegistrationForm):
    area_competenza = forms.CharField(max_length=100)
    is_responsabile = forms.BooleanField(required=False, label="È responsabile di un laboratorio?")

    def clean_matricola(self):
        matricola = self.cleaned_data.get('matricola')
        if not re.match(r'^T\d{5}$', matricola):
            raise forms.ValidationError("Formato matricola non valido. Deve essere T seguita da 5 cifre (es. T12345).")
        if Utente.objects.filter(matricola=matricola).exists():
            raise forms.ValidationError("Questa matricola è già stata registrata.")
        return matricola

    def save(self, commit=True):
        user = super().save(commit=False)
        user.ruolo = Ruolo.TECNICO
        user.area_competenza = self.cleaned_data.get('area_competenza')
        user.is_responsabile = self.cleaned_data.get('is_responsabile')

        if commit:
            user.save()
        return user



class ProgettoSperimentaleForm(forms.ModelForm):
    class Meta:
        model = ProgettoSperimentale
        # Campi che l'utente potrà compilare
        fields = ['titolo', 'descrizione', 'obiettivi', 'data_inizio', 'data_fine', 'max_posti']

        widgets = {
            'descrizione': forms.Textarea(attrs={'rows': 4}),
            'obiettivi': forms.Textarea(attrs={'rows': 4}),
            'data_inizio': forms.DateInput(attrs={'type': 'date'}),
            'data_fine': forms.DateInput(attrs={'type': 'date'}),
        }


# forms.py
from .models import Laboratorio, Attrezzatura


class CreaEsperimentoForm(forms.Form):
    #esperimento
    titolo = forms.CharField(max_length=100)
    descrizione = forms.CharField(widget=forms.Textarea)
    obiettivi = forms.CharField(widget=forms.Textarea)

    #prenotazione
    laboratorio = forms.ModelChoiceField(queryset=Laboratorio.objects.all(), label="Laboratorio")
    attrezzature = forms.ModelMultipleChoiceField(
        queryset=Attrezzatura.objects.filter(stato='Funzionante'),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    data_prenotazione = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    ora_inizio = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    ora_fine = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    #  evitare conflitti (RF8)
    def clean(self):
        cleaned_data = super().clean()
        lab = cleaned_data.get("laboratorio")
        data = cleaned_data.get("data_prenotazione")
        inizio = cleaned_data.get("ora_inizio")
        fine = cleaned_data.get("ora_fine")

        if lab and data and inizio and fine:
            #controllo conflitti per il laboratorio
            prenotazioni_lab_conflitto = PrenotazioneLaboratorio.objects.filter(
                laboratorio=lab,
                data=data,
                ora_fine__gt=inizio,
                ora_inizio__lt=fine
            )
            if prenotazioni_lab_conflitto.exists():
                self.add_error('laboratorio', "Il laboratorio è già prenotato in questa fascia oraria.")

            #controlla conflitti per  attrezzature
            attrezzature_selezionate = cleaned_data.get('attrezzature', [])
            for attr in attrezzature_selezionate:
                prenotazioni_attr_conflitto = PrenotazioneAttrezzatura.objects.filter(
                    codice_inventario=attr,
                    data=data,
                    ora_fine__gt=inizio,
                    ora_inizio__lt=fine
                )
                if prenotazioni_attr_conflitto.exists():
                    self.add_error('attrezzature', f"L'attrezzatura '{attr}' è già prenotata in questa fascia oraria.")

        return cleaned_data
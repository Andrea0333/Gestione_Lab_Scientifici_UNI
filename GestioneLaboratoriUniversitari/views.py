from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from .forms import ProfessoreForm, StudenteForm, TecnicoForm, ProgettoForm, EsperimentoForm
from .models import (Profilo, Professore, Studente, Tecnico,
                     ProgettoSperimentale, Esperimento,
                     PrenotazioneLaboratorio, PrenotazioneAttrezzatura)

# ------------------------------------
# PAGINE PUBBLICHE
# ------------------------------------

def home_view(request):
    return render(request, 'home.html')


def registrazione_view(request):
    return render(request, 'registrazione.html')

# ------------------------------------
# REGISTRAZIONE UTENTI
# ------------------------------------

def registrazione_professore_view(request):
    form = ProfessoreForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Registrazione Professore completata. Ora puoi effettuare il login.")
        return redirect('login')
    return render(request, 'professore/registrazione_professore.html', {'form': form})


def registrazione_studente_view(request):
    form = StudenteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Registrazione Studente completata. Ora puoi effettuare il login.")
        return redirect('login')
    return render(request, 'studente/registrazione_studente.html', {'form': form})


def registrazione_tecnico_view(request):
    form = TecnicoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Registrazione Tecnico completata. Ora puoi effettuare il login.")
        return redirect('login')
    return render(request, 'tecnico/registrazione_tecnico.html', {'form': form})

# ------------------------------------
# AUTENTICAZIONE
# ------------------------------------

def login_view(request):
    if request.method == 'POST':
        matricola = request.POST.get('matricola')
        password = request.POST.get('password')
        user = authenticate(request, username=matricola, password=password)
        if user is None:
            messages.error(request, "Matricola o password errati.")
            return render(request, 'login.html')

        login(request, user)
        try:
            ruolo = user.profilo.ruolo
        except Profilo.DoesNotExist:
            logout(request)
            messages.error(request, "Profilo non trovato: contatta l’amministratore.")
            return redirect('login')

        if ruolo == 'professore':
            return redirect('dashboard_professore')
        elif ruolo == 'studente':
            return redirect('dashboard_studente')
        elif ruolo == 'tecnico':
            return redirect('dashboard_tecnico')

        logout(request)
        messages.error(request, "Ruolo utente non riconosciuto.")
        return redirect('login')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

# ------------------------------------
# DASHBOARD PROFESSORE
# ------------------------------------

@login_required
def dashboard_professore(request):
    progetti = ProgettoSperimentale.objects.filter(responsabile__user=request.user)
    return render(request, 'professore/dashboard_professore.html', {'progetti': progetti})


@login_required
def crea_progetto(request):
    form = ProgettoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        progetto = form.save(commit=False)
        professore = get_object_or_404(Professore, user=request.user)
        progetto.responsabile = professore
        progetto.save()
        return redirect('dashboard_professore')
    return render(request, 'professore/crea_progetto.html', {'form': form})


@login_required
def elimina_progetto(request, progetto_id):
    progetto = get_object_or_404(ProgettoSperimentale, id=progetto_id, responsabile__user=request.user)
    if request.method == 'POST':
        progetto.delete()
        return redirect('dashboard_professore')
    return render(request, 'professore/conferma_eliminazione.html', {'progetto': progetto})


@login_required
def visualizza_esperimenti(request, progetto_id):
    progetto = get_object_or_404(ProgettoSperimentale, id=progetto_id, responsabile__user=request.user)
    esperimenti = Esperimento.objects.filter(progetto=progetto)
    return render(request, 'professore/visualizza_esperimenti.html', {
        'progetto': progetto,
        'esperimenti': esperimenti,
    })


@login_required
def crea_esperimento(request, progetto_id):
    progetto = get_object_or_404(ProgettoSperimentale, id=progetto_id, responsabile__user=request.user)
    professore = get_object_or_404(Professore, user=request.user)

    form = EsperimentoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        esperimento = form.save(commit=False)
        esperimento.progetto = progetto
        esperimento.save()

        PrenotazioneLaboratorio.objects.create(
            professore=professore,
            laboratorio=form.cleaned_data['laboratorio'],
            esperimento=esperimento,
            data=form.cleaned_data['data'],
            ora_inizio=form.cleaned_data['ora_inizio'],
            ora_fine=form.cleaned_data['ora_fine']
        )
        for att in form.cleaned_data['attrezzature']:
            PrenotazioneAttrezzatura.objects.create(
                professore=professore,
                attrezzatura=att,
                esperimento=esperimento,
                data=form.cleaned_data['data'],
                ora_inizio=form.cleaned_data['ora_inizio'],
                ora_fine=form.cleaned_data['ora_fine']
            )
        return redirect('visualizza_esperimenti', progetto_id=progetto.id)

    return render(request, 'professore/crea_esperimento.html', {
        'form': form,
        'progetto': progetto,
    })

# ------------------------------------
# DASHBOARD STUDENTE & TECNICO
# ------------------------------------

@login_required
def dashboard_studente(request):
    return render(request, 'studente/dashboard_studente.html')


@login_required
def dashboard_tecnico(request):
    return render(request, 'tecnico/dashboard_tecnico.html')

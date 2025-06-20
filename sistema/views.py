from django.contrib.auth import logout

# Create your views here.
from .models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Utente, Professore, Studente, Tecnico
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, get_object_or_404


def home_view(request):
    progetti = ProgettoSperimentale.objects.all().order_by('data_inizio')
    return render(request, 'home.html', {'progetti': progetti})

from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Utente

def login_view(request):
    if request.method == 'POST':
        matricola = request.POST.get('matricola', '').strip().upper()
        password = request.POST.get('password', '')

        try:
            utente = Utente.objects.get(matricola=matricola)   # 🔑 solo matricola
        except Utente.DoesNotExist:
            utente = None

        if utente and check_password(password, utente.password):
            request.session['matricola'] = utente.matricola
            request.session['tipo'] = utente.tipo

            if utente.tipo == 'professore':
                return redirect('dashboard_professore')
            elif utente.tipo == 'studente':
                return redirect('dashboard_studente')
            elif utente.tipo == 'tecnico':
                return redirect('dashboard_tecnico')
        else:
            messages.error(request, "Credenziali non valide.")

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')


def registrazione_view(request):
    return render(request, 'registrazione.html')


# ----------- Professore -----------
def registrazione_professore(request):
    if request.method == 'POST':
        matricola = request.POST['matricola'].strip().upper()
        if not matricola.startswith('P') or len(matricola) != 5:
            messages.error(request, "Matricola non valida per professore.")
            return redirect('registrazione_professore')

        if Utente.objects.filter(matricola=matricola).exists():
            messages.error(request, "Matricola già esistente.")
            return redirect('registrazione_professore')

        utente = Utente.objects.create(
            matricola=matricola,
            nome=request.POST['nome'],
            cognome=request.POST['cognome'],
            email=request.POST['email'],
            password=make_password(request.POST['password']),
            tipo='professore'
        )

        Professore.objects.create(
            utente=utente,
            dipartimento=request.POST['dipartimento'],
            materia=request.POST['materia']
        )

        messages.success(request, "Registrazione professore completata!")
        return redirect('login')

    return render(request, 'registrazione_professore.html')


# ----------- Studente -----------
def registrazione_studente(request):
    if request.method == 'POST':
        matricola = request.POST['matricola'].strip().upper()
        if not matricola.startswith('S') or len(matricola) != 5:
            messages.error(request, "Matricola non valida per studente.")
            return redirect('registrazione_studente')

        if Utente.objects.filter(matricola=matricola).exists():
            messages.error(request, "Matricola già esistente.")
            return redirect('registrazione_studente')

        utente = Utente.objects.create(
            matricola=matricola,
            nome=request.POST['nome'],
            cognome=request.POST['cognome'],
            email=request.POST['email'],
            password=make_password(request.POST['password']),
            tipo='studente'
        )

        Studente.objects.create(
            utente=utente,
            corso_laurea=request.POST['corso_laurea'],
            anno=request.POST['anno']
        )

        messages.success(request, "Registrazione studente completata!")
        return redirect('login')

    return render(request, 'registrazione_studente.html')


# ----------- Tecnico -----------
def registrazione_tecnico(request):
    if request.method == 'POST':
        matricola = request.POST['matricola'].strip().upper()
        if not matricola.startswith('T') or len(matricola) != 5:
            messages.error(request, "Matricola non valida per tecnico.")
            return redirect('registrazione_tecnico')

        if Utente.objects.filter(matricola=matricola).exists():
            messages.error(request, "Matricola già esistente.")
            return redirect('registrazione_tecnico')

        utente = Utente.objects.create(
            matricola=matricola,
            nome=request.POST['nome'],
            cognome=request.POST['cognome'],
            email=request.POST['email'],
            password=make_password(request.POST['password']),
            tipo='tecnico'
        )

        Tecnico.objects.create(
            utente=utente,
            area_competenza=request.POST['area_competenza'],
            responsabile_laboratorio='responsabile_laboratorio' in request.POST
        )

        messages.success(request, "Registrazione tecnico completata!")
        return redirect('login')

    return render(request, 'registrazione_tecnico.html')


def dashboard_professore(request):
    matricola = request.session.get('matricola')
    if not matricola:
        return redirect('login')

    try:
        professore = Professore.objects.get(utente__matricola=matricola)
    except Professore.DoesNotExist:
        messages.error(request, "Accesso non autorizzato.")
        return redirect('login')

    progetti = ProgettoSperimentale.objects.filter(responsabile=professore)

    return render(request, 'dashboard_professore.html', {
        'professore': professore,
        'progetti': progetti
    })





@require_http_methods(["GET", "POST"])
def crea_progetto(request):
    if request.session.get('tipo') != 'professore':
        return redirect('login')  # blocca accesso se non è un professore

        # recupera il professore autenticato
    matricola = request.session.get('matricola')
    professore = Professore.objects.get(utente__matricola=matricola)



    if request.method == 'POST':
        titolo = request.POST.get('titolo')
        descrizione = request.POST.get('descrizione')
        obiettivi = request.POST.get('obiettivi')
        data_inizio = request.POST.get('data_inizio')
        data_fine = request.POST.get('data_fine')

        ProgettoSperimentale.objects.create(
            responsabile=professore,
            titolo=titolo,
            descrizione=descrizione,
            obiettivi=obiettivi,
            data_inizio=data_inizio,
            data_fine=data_fine
        )

        messages.success(request, "Progetto creato con successo!")
        return redirect('dashboard_professore')

    return render(request, 'crea_progetto.html')




def elimina_progetto(request):
    if request.method == 'POST':
        matricola = request.session.get('matricola')
        if not matricola:
            return redirect('login')

        professore = get_object_or_404(Professore, utente__matricola=matricola)

        progetto_id = request.POST.get('progetto_id')
        progetto = get_object_or_404(ProgettoSperimentale, id_progetto=progetto_id, responsabile=professore)

        progetto.delete()
        messages.success(request, "Progetto eliminato con successo.")
        return redirect('dashboard_professore')

    return redirect('dashboard_professore')


def lista_esperimenti(request, progetto_id):
    try:
        progetto = ProgettoSperimentale.objects.get(id_progetto=progetto_id)
    except ProgettoSperimentale.DoesNotExist:
        messages.error(request, "Progetto non trovato.")
        return redirect('dashboard_professore')

    esperimenti = Esperimento.objects.filter(progetto=progetto)

    return render(request, 'lista_esperimenti.html', {
        'progetto': progetto,
        'esperimenti': esperimenti
    })





def crea_esperimento(request, progetto_id):
    professore = get_object_or_404(
        Professore, utente__matricola=request.session.get('matricola')
    )
    progetto = get_object_or_404(ProgettoSperimentale, id_progetto=progetto_id)

    laboratori   = Laboratorio.objects.all()
    attrezzature = Attrezzatura.objects.all()

    if request.method == 'POST':
        #  dati esperimento
        titolo       = request.POST['titolo']
        descrizione  = request.POST['descrizione']
        obiettivi    = request.POST['obiettivi']
        materiali    = request.POST['materiali']
        data_inizio  = request.POST['data_inizio']
        data_fine    = request.POST['data_fine']

        #  dati prenotazione
        laboratorio  = get_object_or_404(Laboratorio, pk=request.POST['laboratorio'])
        attrezzatura = get_object_or_404(Attrezzatura,pk=request.POST['attrezzatura'])
        data        = request.POST['data']
        ora_inizio  = request.POST['ora_inizio']
        ora_fine    = request.POST['ora_fine']

        # CONTROLLI DI CONFLITTO
        if PrenotazioneLaboratorio.objects.filter(
            laboratorio=laboratorio,
            data=data,
            ora_inizio=ora_inizio,
            ora_fine=ora_fine
        ).exists():
            messages.error(request,
                "Questo laboratorio è già prenotato in questo intervallo.")
            return redirect('crea_esperimento', progetto_id=progetto.id_progetto)

        if PrenotazioneAttrezzatura.objects.filter(
            attrezzatura=attrezzatura,
            data=data,
            ora_inizio=ora_inizio,
            ora_fine=ora_fine
        ).exists():
            messages.error(request,
                "Questa attrezzatura è già prenotata in questo intervallo.")
            return redirect('crea_esperimento', progetto_id=progetto.id_progetto)

        # CREAZIONE ESPERIMENTO
        esperimento = Esperimento.objects.create(
            progetto     = progetto,
            titolo       = titolo,
            descrizione  = descrizione,
            obiettivi    = obiettivi,
            materiali    = materiali,
            data_inizio  = data_inizio,
            data_fine    = data_fine
        )

        # CREAZIONE PRENOTAZIONI
        PrenotazioneLaboratorio.objects.create(
            professore = professore,
            laboratorio = laboratorio,
            esperimento = esperimento,
            data        = data,
            ora_inizio  = ora_inizio,
            ora_fine    = ora_fine
        )

        PrenotazioneAttrezzatura.objects.create(
            professore   = professore,
            attrezzatura = attrezzatura,
            esperimento  = esperimento,
            data         = data,
            ora_inizio   = ora_inizio,
            ora_fine     = ora_fine
        )

        messages.success(request, "Esperimento creato e prenotazioni registrate.")
        return redirect('dashboard_professore')

    # GET
    return render(request, 'crea_esperimento.html', {
        'progetto': progetto,
        'laboratori': laboratori,
        'attrezzature': attrezzature
    })

def partecipanti_esperimento(request, id):
    esperimento = Esperimento.objects.get(pk=id)
    partecipazioni = PrenotazioneEsperimento.objects.filter(esperimento=esperimento)

    return render(request, 'partecipanti_esperimento.html', {
        'esperimento': esperimento,
        'partecipazioni': partecipazioni
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils import  timezone

from .forms import *
from .models import *
from django.contrib.auth.hashers import check_password


# views.py

# Aggiungi questa vista al tuo views.py

def home_view(request):


    # Controlla se l'utente ha una sessione attiva
    if request.session.get('is_authenticated'):
        ruolo = request.session.get('ruolo')

        # Reindirizza alla dashboard corretta in base al ruolo
        if ruolo == 'Professore':
            return redirect('dashboard_professore')
        elif ruolo == 'Studente':
            return redirect('dashboard_studente')
        elif ruolo == 'Tecnico':
            return redirect('dashboard_tecnico')
        else:
            # Fallback nel caso in cui la sessione sia anomala
            return redirect('login')

    # Se l'utente non è autenticato, mostra la home page pubblica
    return render(request, 'home.html')

# Vista per la pagina di scelta
def registrazione_view(request):
    return render(request, 'registrazione.html')

# Vista per la registrazione del professore
def registrazione_professore_view(request):
    if request.method == 'POST':
        form = ProfessoreForm(request.POST)
        if form.is_valid():
            form.save()
            # Puoi aggiungere un messaggio di successo qui
            return redirect('login') # Reindirizza al login dopo il successo
    else:
        form = ProfessoreForm()
    return render(request, 'professore/registrazione_professore.html', {'form': form})

# Vista per la registrazione dello studente
def registrazione_studente_view(request):
    if request.method == 'POST':
        form = StudenteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = StudenteForm()
    return render(request, 'studente/registrazione_studente.html', {'form': form})

# Vista per la registrazione del tecnico
def registrazione_tecnico_view(request):
    if request.method == 'POST':
        form = TecnicoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = TecnicoForm()
    return render(request, 'tecnico/registrazione_tecnico.html', {'form': form})


# VISTA DI LOGIN
def login_view(request):

    if request.method == "POST":
        matricola = request.POST.get('matricola')
        password_in_chiaro = request.POST.get('password')

        if not matricola or not password_in_chiaro:
            return render(request, 'login.html', {'error_message': "Matricola e password sono obbligatorie."})

        try:
            utente = Utente.objects.get(matricola=matricola)

            if check_password(password_in_chiaro, utente.password):
                # Credenziali valide, salviamo i dati in sessione
                request.session['matricola'] = utente.matricola
                request.session['ruolo'] = utente.ruolo
                request.session['is_authenticated'] = True

                #  REDIRECT BASATO SUL RUOLO
                if utente.ruolo == 'Professore':
                    return redirect('dashboard_professore')
                elif utente.ruolo == 'Studente':
                    return redirect('dashboard_studente')
                elif utente.ruolo == 'Tecnico':
                    return redirect('dashboard_tecnico')
            else:
                return render(request, 'login.html', {'error_message': "Credenziali non valide, riprova."})

        except Utente.DoesNotExist:
            return render(request, 'login.html', {'error_message': "Credenziali non valide, riprova."})

    return render(request, 'login.html')


# VISTA DI LOGOUT (RF11)
def logout_view(request):

    # request.session.flush() rimuove tutti i dati dalla sessione corrente.
    request.session.flush()
    return redirect('login')


#
# VISTA DASHBOARD PROFESSORE (RF3, RF4)
def dashboard_professore(request):

    #controllo
    if not request.session.get('is_authenticated') or request.session.get('ruolo') != 'Professore':
        return redirect('login')

    try:
        #Recupera l'utente dalla matricola salvata in sessione
        matricola_professore = request.session.get('matricola')
        professore = Utente.objects.get(matricola=matricola_professore)

        # [cite_start]Recupera tutti i progetti sperimentali creati da questo professore [cite: 9]
        progetti_creati = ProgettoSperimentale.objects.filter(docente=professore).order_by('-data_inizio')

        context = {
            'professore': professore,
            'progetti': progetti_creati,
        }
        return render(request, 'professore/dashboard_professore.html', context)

    except Utente.DoesNotExist:
        # Se per qualche motivo l'utente non esiste più, effettua il logout
        return redirect('logout')



# VISTA DASHBOARD STUDENTE (RF3, RF9)
def dashboard_studente(request):

    #Controllo di autorizzazione
    if not request.session.get('is_authenticated') or request.session.get('ruolo') != 'Studente':
        return redirect('login')

    try:
        matricola_studente = request.session.get('matricola')
        studente = Utente.objects.get(matricola=matricola_studente)

        # Recupera gli ID dei progetti a cui lo studente è già iscritto
        progetti_iscritti_ids = PartecipazioneProgetto.objects.filter(studente=studente).values_list('progetto_id',
                                                                                                     flat=True)

        # Recupera gli oggetti ProgettoSperimentale a cui lo studente partecipa
        progetti_partecipa = ProgettoSperimentale.objects.filter(id_progetto__in=progetti_iscritti_ids)

        # [cite_start]Recupera tutti i progetti disponibili a cui lo studente NON è iscritto [cite: 16]
        progetti_disponibili = ProgettoSperimentale.objects.exclude(id_progetto__in=progetti_iscritti_ids)

        context = {
            'studente': studente,
            'progetti_partecipa': progetti_partecipa,
            'progetti_disponibili': progetti_disponibili,
        }
        return render(request, 'studente/dashboard_studente.html', context)

    except Utente.DoesNotExist:
        return redirect('logout')



# VISTA DASHBOARD TECNICO (RF3, RF12)
def dashboard_tecnico(request):
    if not request.session.get('is_authenticated') or request.session.get('ruolo') != 'Tecnico':
        return redirect('login')

    try:
        matricola_tecnico = request.session.get('matricola')
        tecnico = Utente.objects.get(matricola=matricola_tecnico)

        laboratorio_responsabile = Laboratorio.objects.filter(responsabile=tecnico).first()

        attrezzature_da_gestire = []
        prenotazioni_imminenti = []

        if laboratorio_responsabile:

            attrezzature_da_gestire = Attrezzatura.objects.filter(laboratorio=laboratorio_responsabile).order_by('tipo')

            #recuperiamo le prenotazioni per il laboratorio di oggi e dei giorni futuri
            oggi = timezone.now().date()
            prenotazioni_imminenti = PrenotazioneLaboratorio.objects.filter(
                laboratorio=laboratorio_responsabile,
                data__gte=oggi
            ).order_by('data', 'ora_inizio')

        context = {
            'tecnico': tecnico,
            'laboratorio': laboratorio_responsabile,
            'attrezzature': attrezzature_da_gestire,
            'prenotazioni': prenotazioni_imminenti,
        }
        return render(request, 'tecnico/dashboard_tecnico.html', context)

    except Utente.DoesNotExist:
        return redirect('logout')






# FUNZIONALITA' PROFESSORE
def crea_progetto_view(request):

    #  solo i professori autenticati possono accedere
    if not request.session.get('is_authenticated') or request.session.get('ruolo') != 'Professore':
        return redirect('login')

    if request.method == 'POST':
        form = ProgettoSperimentaleForm(request.POST)
        if form.is_valid():
            #creiamo il progetto ma non lo salviamo ancora nel DB
            progetto = form.save(commit=False)

            #associamo la matricola del professore al progetto
            matricola_professore = request.session.get('matricola')
            professore = Utente.objects.get(matricola=matricola_professore)
            progetto.docente = professore


            progetto.save()

            #reindirizziamo alla dashboard del professore
            return redirect('dashboard_professore')
    else:
        form = ProgettoSperimentaleForm()

    context = {
        'form': form
    }
    return render(request, 'professore/crea_progetto.html', context)


def dettaglio_progetto_view(request, progetto_id):

    if not request.session.get('is_authenticated') or request.session.get('ruolo') != 'Professore':
        return redirect('login')

    progetto = get_object_or_404(ProgettoSperimentale, id_progetto=progetto_id)

    # assicuriamoci che il professore che richiede la pagina sia il proprietario del progetto
    if progetto.docente.matricola != request.session.get('matricola'):
        # Se non è il proprietario, reindirizzalo alla sua dashboard
        return redirect('dashboard_professore')

    esperimenti = Esperimento.objects.filter(progetto=progetto)

    context = {
        'progetto': progetto,
        'esperimenti': esperimenti
    }
    return render(request, 'professore/dettaglio_progetto.html', context)


def crea_esperimento_view(request, progetto_id):
    if not request.session.get('is_authenticated') or request.session.get('ruolo') != 'Professore':
        return redirect('login')

    progetto = get_object_or_404(ProgettoSperimentale, id_progetto=progetto_id)
    professore = get_object_or_404(Utente, matricola=request.session.get('matricola'))

    if progetto.docente != professore:
        return redirect('dashboard_professore')

    if request.method == 'POST':
        form = CreaEsperimentoForm(request.POST)
        if form.is_valid():
            dati = form.cleaned_data

            #1 crea l'esperimento
            nuovo_esperimento = Esperimento.objects.create(
                progetto=progetto,
                titolo=dati['titolo'],
                descrizione=dati['descrizione'],
                obiettivi=dati['obiettivi'],
                data_inizio=dati['data_prenotazione'],
                data_fine=dati['data_prenotazione']
            )

            #2  prenotazione del laboratorio
            PrenotazioneLaboratorio.objects.create(
                docente=professore,
                laboratorio=dati['laboratorio'],
                esperimento=nuovo_esperimento,
                data=dati['data_prenotazione'],
                ora_inizio=dati['ora_inizio'],
                ora_fine=dati['ora_fine']
            )

            #3  prenotazioni per le attrezzature
            for attrezzatura in dati['attrezzature']:
                PrenotazioneAttrezzatura.objects.create(
                    docente=professore,
                    codice_inventario=attrezzatura,
                    esperimento=nuovo_esperimento,
                    data=dati['data_prenotazione'],
                    ora_inizio=dati['ora_inizio'],
                    ora_fine=dati['ora_fine']
                )

            return redirect('dettaglio_progetto', progetto_id=progetto.id_progetto)
    else:
        form = CreaEsperimentoForm()

    return render(request, 'professore/crea_esperimento.html', {'form': form, 'progetto': progetto})


# views.py
from django.shortcuts import get_object_or_404  # Assicurati che sia importato


def elimina_progetto_view(request, progetto_id):

    #solo professori autenticati
    if not request.session.get('is_authenticated') or request.session.get('ruolo') != 'Professore':
        return redirect('login')

    progetto = get_object_or_404(ProgettoSperimentale, id_progetto=progetto_id)

    #il professore può eliminare solo i propri progetti importante per evitare manipolazioni url
    if progetto.docente.matricola != request.session.get('matricola'):
        return redirect('dashboard_professore')


    if request.method == 'POST':
        progetto.delete()
        return redirect('dashboard_professore')


    context = {
        'progetto': progetto
    }
    return render(request, 'professore/conferma_eliminazione.html', context)



#FINZIONALITA' TECNICO
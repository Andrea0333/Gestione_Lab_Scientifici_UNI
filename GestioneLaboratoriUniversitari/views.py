from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
from django.utils import  timezone

from .forms import *
from .models import *
from django.contrib.auth.hashers import check_password





def home_view(request):
    if request.session.get('is_authenticated'):
        ruolo = request.session.get('ruolo')

        # indirizziamo  alla dashboard corretta in base al ruolo
        if ruolo == 'Professore':
            return redirect('dashboard_professore')
        elif ruolo == 'Studente':
            return redirect('dashboard_studente')
        elif ruolo == 'Tecnico':
            return redirect('dashboard_tecnico')
        else:

            return redirect('login')


    return render(request, 'home.html')


def registrazione_view(request):
    return render(request, 'registrazione.html')



# registrazione  professore
def registrazione_professore_view(request):
    if request.method == 'POST':
        form = ProfessoreForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registrazione completata!')
            return redirect('login') # Reindirizza al login dopo il successo
    else:
        form = ProfessoreForm()
    return render(request, 'professore/registrazione_professore.html', {'form': form})



# registrazione studente
def registrazione_studente_view(request):
    if request.method == 'POST':
        form = StudenteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registrazione completata!')
            return redirect('login')
    else:
        form = StudenteForm()
    return render(request, 'studente/registrazione_studente.html', {'form': form})



#registrazione tecnico
def registrazione_tecnico_view(request):
    if request.method == 'POST':
        form = TecnicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registrazione completata!')
            return redirect('login')
    else:
        form = TecnicoForm()
    return render(request, 'tecnico/registrazione_tecnico.html', {'form': form})


#  LOGIN
def login_view(request):

    if request.method == "POST":
        matricola = request.POST.get('matricola')
        password = request.POST.get('password')

        if not matricola or not password:
            return render(request, 'login.html', {'error_message': "Matricola e password sono obbligatorie."})

        try:
            utente = Utente.objects.get(matricola=matricola)

            if check_password(password, utente.password):
                #salviamo i dati in sessione
                request.session['matricola'] = utente.matricola
                request.session['ruolo'] = utente.ruolo
                request.session['is_authenticated'] = True

                # indirizzamento basato sul ruolo dell'utente
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


# LOGOUT (RF11)
def logout_view(request):
    request.session.flush()
    return redirect('login')



# DASHBOARD PROFESSORE (RF3, RF4)
def dashboard_professore(request):

    #controllo
    if not request.session.get('is_authenticated') or request.session.get('ruolo') != 'Professore':
        return redirect('login')

    try:
        #recuperiami l'utente dalla matricola
        matricola_professore = request.session.get('matricola')
        professore = Utente.objects.get(matricola=matricola_professore)

        progetti_creati = ProgettoSperimentale.objects.filter(docente=professore).order_by('-data_inizio')

        context = {
            'professore': professore,
            'progetti': progetti_creati,
        }
        return render(request, 'professore/dashboard_professore.html', context)

    except Utente.DoesNotExist:

        return redirect('logout')



#  DASHBOARD STUDENTE (RF3, RF9)
def dashboard_studente(request):

    #  controllo di autorizzazione
    if not request.session.get('is_authenticated') or request.session.get('ruolo') != 'Studente':
        return redirect('login')

    try:
        matricola_studente = request.session.get('matricola')
        studente = Utente.objects.get(matricola=matricola_studente)

        #recupero degli id dei progetti a cui lo studente è  iscritto
        progetti_iscritti_ids = PartecipazioneProgetto.objects.filter(studente=studente).values_list('progetto_id',  flat=True)

        # recupero gli oggetti ProgettoSperimentale a cui lo studente partecipa
        progetti_partecipa = ProgettoSperimentale.objects.filter(id_progetto__in=progetti_iscritti_ids)
        #mostriamo i progetti disponibili
        progetti_disponibili = ProgettoSperimentale.objects.exclude(id_progetto__in=progetti_iscritti_ids)

        context = {
            'studente': studente,
            'progetti_partecipa': progetti_partecipa,
            'progetti_disponibili': progetti_disponibili,
        }
        return render(request, 'studente/dashboard_studente.html', context)

    except Utente.DoesNotExist:
        return redirect('logout')



# DASHBOARD TECNICO (RF3, RF12)
def dashboard_tecnico(request):
    if not request.session.get('is_authenticated') or request.session.get('ruolo') != 'Tecnico':
        return redirect('login')

    try:
        matricola_tecnico = request.session.get('matricola')
        tecnico = Utente.objects.get(matricola=matricola_tecnico)

        laboratorio_responsabile = Laboratorio.objects.filter(responsabile=tecnico).first()

        attrezzature_da_gestire = []
        prenotazioni_imminenti_lab = []
        prenotazione_imminenti_attrezzature = []

        if laboratorio_responsabile:

            attrezzature_da_gestire = Attrezzatura.objects.filter(laboratorio=laboratorio_responsabile).order_by('tipo')

            #recuperiamo le prenotazioni per il laboratorio  giorni futuri
            oggi = timezone.now().date()
            prenotazioni_imminenti_lab = PrenotazioneLaboratorio.objects.filter(
                laboratorio=laboratorio_responsabile,
                data__gte=oggi
            ).order_by('data', 'ora_inizio')

            oggi = timezone.now().date()
            prenotazione_imminenti_attrezzature = PrenotazioneAttrezzatura.objects.filter(
                attrezzatura__laboratorio=laboratorio_responsabile,
                data__gte=oggi
            ).order_by('data', 'ora_inizio')

        context = {
            'tecnico': tecnico,
            'laboratorio': laboratorio_responsabile,
            'attrezzature': attrezzature_da_gestire,
            'prenotazioni_laboratorio': prenotazioni_imminenti_lab,
            'prenotazioni_attrezzature': prenotazione_imminenti_attrezzature,

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
            #creiamo il progetto ma non lo salviamo ancora nel database
            progetto = form.save(commit=False)

            #associamo la matricola del professore al progetto
            matricola_professore = request.session.get('matricola')
            professore = Utente.objects.get(matricola=matricola_professore)
            progetto.docente = professore
            progetto.save()

            return redirect('dashboard_professore')
    else:
        form = ProgettoSperimentaleForm()

    context = {
        'form': form
    }
    return render(request, 'professore/crea_progetto.html', context)


def dettaglio_progetto_view(request, progetto_id):
    # controlliamo  se l'utente è semplicemente autenticato.

    if not request.session.get('is_authenticated'):
        return redirect('login')


    progetto = get_object_or_404(ProgettoSperimentale, id_progetto=progetto_id)
    esperimenti = Esperimento.objects.filter(progetto=progetto).prefetch_related('prenotazionelaboratorio_set')

    #  verifichiamo il ruolo
    ruolo_utente = request.session.get('ruolo')

    #  è un professore  controlliamo che sia il proprietario del progetto
    if ruolo_utente == 'Professore':
        if progetto.docente.matricola != request.session.get('matricola'):
            # Se non è il proprietario, non può vedere la pagina
            return redirect('dashboard_professore')


   #srudente
    is_studente = (ruolo_utente == 'Studente')
    studente_is_iscritto = False
    if is_studente:
        try:
            studente = Utente.objects.get(matricola=request.session.get('matricola'))
            studente_is_iscritto = PartecipazioneProgetto.objects.filter(progetto=progetto, studente=studente).exists()
        except Utente.DoesNotExist:
            return redirect('logout')

    context = {
        'progetto': progetto,
        'esperimenti': esperimenti,
        'is_studente': is_studente,
        'studente_is_iscritto': studente_is_iscritto,
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

            #3  prenotazioni delle attrezzature
            for attrezzatura in dati['attrezzature']:
                PrenotazioneAttrezzatura.objects.create(
                    docente=professore,
                    attrezzatura=attrezzatura,
                    esperimento=nuovo_esperimento,
                    data=dati['data_prenotazione'],
                    ora_inizio=dati['ora_inizio'],
                    ora_fine=dati['ora_fine']
                )

            return redirect('dettaglio_progetto', progetto_id=progetto.id_progetto)
    else:
        form = CreaEsperimentoForm()

    return render(request, 'professore/crea_esperimento.html', {'form': form, 'progetto': progetto})





def elimina_progetto_view(request, progetto_id):

    #solo professori autenticati
    if not request.session.get('is_authenticated') or request.session.get('ruolo') != 'Professore':
        return redirect('login')

    progetto = get_object_or_404(ProgettoSperimentale, id_progetto=progetto_id)

    #il professore può eliminare solo i propri progetti importante per evitare manipolazioni url
    if progetto.docente.matricola != request.session.get('matricola'):
        messages.error(request, "Non sei autorizzato a eseguire questa operazione.")
        return redirect('dashboard_professore')


    if request.method == 'POST':
        progetto.delete()
        return redirect('dashboard_professore')


    context = {
        'progetto': progetto
    }
    return render(request, 'professore/conferma_eliminazione.html', context)




def elimina_esperimento_view(request, esperimento_id):
    if not request.session.get('is_authenticated') or request.session.get('ruolo') != 'Professore':
        return redirect('login')

    esperimento = get_object_or_404(Esperimento, id_esperimento=esperimento_id)
    progetto = esperimento.progetto  # Recuperiamo il progetto per il redirect e i controlli

    #controlliamo che il professore sia il proprietario del progetto
    if progetto.docente.matricola != request.session.get('matricola'):
        return redirect('dashboard_professore')

    if request.method == 'POST':
        esperimento.delete()
        return redirect('dettaglio_progetto', progetto_id=progetto.id_progetto)

    return render(request, 'professore/conferma_eliminazione_esperimento.html', {'esperimento': esperimento})






#FINZIONALITA' TECNICO

def aggiungi_attrezzatura_view(request):
    if not request.session.get('is_authenticated') or request.session.get('ruolo') != 'Tecnico':
        return redirect('login')

    tecnico = Utente.objects.get(matricola=request.session.get('matricola'))
    laboratorio = Laboratorio.objects.filter(responsabile=tecnico).first()

    if not laboratorio:  #solo i tecnici responsabili di un lab possono aggiungere attrezzature
        return redirect('dashboard_tecnico')

    if request.method == 'POST':
        form = AttrezzaturaForm(request.POST)
        if form.is_valid():
            attrezzatura = form.save(commit=False)
            attrezzatura.laboratorio = laboratorio
            attrezzatura.save()
            return redirect('dashboard_tecnico')
    else:
        form = AttrezzaturaForm()

    return render(request, 'form_generico.html', {'form': form, 'titolo': 'Aggiungi Nuova Attrezzatura'})


def modifica_stato_attrezzatura_view(request, attrezzatura_id):
    if not request.session.get('is_authenticated') or request.session.get('ruolo') != 'Tecnico':
        return redirect('login')

    attrezzatura = get_object_or_404(Attrezzatura, codice_inventario=attrezzatura_id)
    tecnico = Utente.objects.get(matricola=request.session.get('matricola'))

    # controlliammo  che l'attrezzatura appartenga al laboratorio del tecnico, come abbiamo fatto per i professori
    if attrezzatura.laboratorio.responsabile != tecnico:
        return redirect('dashboard_tecnico')

    if request.method == 'POST':
        form = ModificaStatoAttrezzaturaForm(request.POST, instance=attrezzatura)
        if form.is_valid():
            form.save()
            return redirect('dashboard_tecnico')
    else:
        form = ModificaStatoAttrezzaturaForm(instance=attrezzatura)

    return render(request, 'form_generico.html', {'form': form, 'titolo': f"Modifica Stato di: {attrezzatura.tipo} ({attrezzatura.marca})"})





#FUNZIONALITA' STUDENTE

def partecipa_progetto_view(request, progetto_id):
    #solo studenti autenticati
    if not request.session.get('is_authenticated') or request.session.get('ruolo') != 'Studente':
        return redirect('login')

    progetto = get_object_or_404(ProgettoSperimentale, id_progetto=progetto_id)
    studente = get_object_or_404(Utente, matricola=request.session.get('matricola'))


    if request.method == 'POST':
        #controllo  se lo studente è iscritto
        gia_iscritto = PartecipazioneProgetto.objects.filter(progetto=progetto, studente=studente).exists()
        if gia_iscritto:
            messages.warning(request, 'Sei già iscritto a questo progetto.')
            return redirect('dettaglio_progetto', progetto_id=progetto.id_progetto)

        # Controllo  (RF10) se il progetto ha raggiunto il numero massimo di posti
        partecipanti_attuali = PartecipazioneProgetto.objects.filter(progetto=progetto).count()
        if partecipanti_attuali >= progetto.max_posti:
            messages.error(request, 'Impossibile iscriversi: il progetto ha raggiunto il numero massimo di partecipanti.')
            return redirect('dettaglio_progetto', progetto_id=progetto.id_progetto)

        #se i controlli sono superati, crea la partecipazione
        PartecipazioneProgetto.objects.create(progetto=progetto, studente=studente)
        messages.success(request, f"Iscrizione al progetto '{progetto.titolo}' avvenuta con successo!")
        return redirect('dashboard_studente')


    return redirect('dettaglio_progetto', progetto_id=progetto.id_progetto)





def partecipa_esperimento_view(request, esperimento_id):
    # Protezione: solo studenti autenticati
    if not request.session.get('is_authenticated') or request.session.get('ruolo') != 'Studente':
        return redirect('login')

    esperimento = get_object_or_404(Esperimento, id_esperimento=esperimento_id)
    studente = get_object_or_404(Utente, matricola=request.session.get('matricola'))
    progetto = esperimento.progetto

    if request.method == 'POST':
        #verifichiamo che lo studente è iscritto al progetto
        iscritto_al_progetto = PartecipazioneProgetto.objects.filter(progetto=progetto, studente=studente).exists()
        if not iscritto_al_progetto:
            messages.error(request, 'Devi essere iscritto al progetto per poter partecipare ai suoi esperimenti.')
            return redirect('dettaglio_progetto', progetto_id=progetto.id_progetto)

        # verifichiamo se lo studente è gia iscritto all'esperimento
        gia_iscritto_esperimento = PartecipazioneEsperimento.objects.filter(esperimento=esperimento, studente=studente).exists()
        if gia_iscritto_esperimento:
            messages.warning(request, 'Sei già iscritto a questo esperimento.')
            return redirect('dettaglio_progetto', progetto_id=progetto.id_progetto)

        # se le verifiche sono ok crea la partecipazione all'esperimento
        PartecipazioneEsperimento.objects.create(esperimento=esperimento, studente=studente)
        messages.success(request, f"Iscrizione all'esperimento '{esperimento.titolo}' avvenuta con successo!")
        return redirect('dettaglio_progetto', progetto_id=progetto.id_progetto)

    return redirect('dettaglio_progetto', progetto_id=progetto.id_progetto)



#CODICE CHE PERMETTE UN ATTACCO DI TIPO MANIPOLAZIONE URL
def elimina_progetto_view_vulnerabile(request, progetto_id):
    progetto = get_object_or_404(ProgettoSperimentale, id_progetto=progetto_id)

    #DISATTIVIAMO LA PROTEZIONE  CHE ABBIAMO IMPLEMENTATO
    # if progetto.docente.matricola != request.session.get('matricola'):
    #     messages.error(request, "Non sei autorizzato a eseguire questa operazione.")
    #     return redirect('dashboard_professore')

    if request.method == 'POST':
        progetto.delete()
        messages.success(request, f"Il progetto '{progetto.titolo}' è stato eliminato tramite manipolazione URL.")
        return redirect('dashboard_professore')

    # SENZA IL CONTROLLO, LA VISTA PROCEDE E MOSTRA LA PAGINA DI CONFERMA
    return render(request, 'professore/conferma_eliminazione.html', {'progetto': progetto})



#CODICE CHE PERMETTE SQL INJECTION

def login_vulnerabile_view(request):
    if request.method == 'POST':
        matricola = request.POST.get('matricola')
        password = request.POST.get('password')

        # QUERY SQL VULNERABILE
        # L'input dell'utente viene inserito direttamente nella stringa della query.
        query = f"SELECT * FROM gestionelaboratoriuniversitari_utente WHERE matricola = '{matricola}' AND password = '{password}'"

        with connection.cursor() as cursor:
            cursor.execute(query)
            utente = cursor.fetchone()

            if utente:

                request.session['matricola'] = utente[0]
                request.session['ruolo'] = utente[5]
                request.session['is_authenticated'] = True
                return redirect('dashboard_professore')
            else:
                messages.error(request, "Credenziali non valide.")
                return redirect('login_vulnerabile')

    return render(request, 'login_vulnerabile.html')

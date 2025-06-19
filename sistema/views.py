
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.contrib import messages


def home_view(request):
    progetti = ProgettoSperimentale.objects.all().order_by('data_inizio')
    return render(request, 'home.html', {'progetti': progetti})

def login_view(request):
    if request.method == 'POST':
        matricola = request.POST.get('matricola')
        password = request.POST.get('password')

        try:
            utente = Utente.objects.get(matricola=matricola, password=password)
        except Utente.DoesNotExist:
            utente = None

        if utente:
            request.session['matricola'] = utente.matricola
            request.session['tipo'] = utente.tipo

            # Redirect dinamico in base al tipo di utente
            if utente.tipo == 'professore':
                return redirect('dashboard_professore')
            elif utente.tipo == 'studente':
                return redirect('dashboard_studente')
            elif utente.tipo == 'tecnico':
                return redirect('dashboard_tecnico')
        else:
            messages.error(request, "Credenziali non valide.")

    return render(request, 'login.html')

def registration_view(request):
    if request.method == 'POST':
        matricola = request.POST['matricola'].strip().upper()
        nome = request.POST['nome']
        cognome = request.POST['cognome']
        email = request.POST['email']
        password = request.POST['password']
        dipartimento = request.POST['dipartimento']
        materia = request.POST['materia']
        corso_laurea= request.POST['corso_laurea']
        anno= request.POST['anno']
        area_competenza = request.POST['area_competenza']
        responsabile = request.POST['responsabile']

        tipo = request.POST['tipo']

        # Prefissi attesi
        prefissi = {
            'studente': 'S',
            'tecnico': 'T',
            'professore': 'P'
        }

        # Controllo validità prefisso
        if not matricola.startswith(prefissi.get(tipo, '')):
            messages.error(request, f"La matricola non valida.")
            return redirect('registration')

        if len(matricola) != 5:
            messages.error(request, 'La matricola deve essere lunga esattamente 5 caratteri.')
            return redirect('register')


        if Utente.objects.filter(matricola=matricola).exists():
            messages.error(request, 'Matricola già registrata.')
            return redirect('registration')

        utente = Utente.objects.create(
            matricola=matricola,
            nome=nome,
            cognome=cognome,
            email=email,
            password=password,
            tipo=tipo
        )

        # Crea record specializzazione
        if tipo == 'professore':
            Professore.objects.create(utente=utente, dipartimento=dipartimento, materia=materia)
        elif tipo == 'studente':
            Studente.objects.create(utente=utente, corso_laurea=corso_laurea, anno=anno)
        elif tipo == 'tecnico':
            Tecnico.objects.create(utente=utente, area_competenza=area_competenza, responsabile_laboratorio=responsabile)

        messages.success(request, 'Registrazione completata! Ora effettua il login.')
        return redirect('login')

    return render(request, 'registration.html')

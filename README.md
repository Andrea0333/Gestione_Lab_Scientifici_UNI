# UniLabManager

Questo è un progetto Django per la gestione di laboratori scientifici universitari. 
Include la gestione di utenti con ruoli diversi (Professore, Studente, Tecnico), creazione progetti, esperimenti, e prenotazione di laboratori e attrezzature.

##  Funzionalità principali

- Registrazione con ruoli differenziati
- Login con matricola (Pxxxx, Sxxxx, Txxxx)
- Dashboard dedicata per ogni ruolo
- Progetti ed esperimenti associati al Professore
- Prenotazioni per laboratori e attrezzature

##  Come eseguire il progetto

bash
# Clona il repository
git clone https://github.com/tuo-utente/tuo-repo.git
cd tuo-repo

# Crea un virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Installa le dipendenze
pip install -r requirements.txt

# Avvia il server
python manage.py migrate
python manage.py runserver

from django.db import models

# Create your models here.


#MODELLO GENERALE UTENTE

class Utente(models.Model):
    RUOLI = [('professore','Professore'),
             ('tecnico','Tecnico'),
             ('studente','Studente'),
             ]
    matricola = models.CharField(max_length=5, primary_key=True)
    nome = models.CharField(max_length=50)
    cognome = models.CharField(max_length=50)
    email = models.EmailField()
    password = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20, choices=RUOLI)



#MODELLI SPECIALIZZAZIONI

class Professore(models.Model):
    utente = models.OneToOneField(Utente, on_delete=models.CASCADE, primary_key=True)
    dipartimento = models.CharField(max_length=100)
    materia = models.CharField(max_length=100)


class Studente(models.Model):
    utente = models.OneToOneField(Utente, on_delete=models.CASCADE, primary_key=True)
    corso_laurea = models.CharField(max_length=100)
    anno = models.IntegerField()


class Tecnico(models.Model):
    utente = models.OneToOneField(Utente, on_delete=models.CASCADE, primary_key=True)
    area_competenza = models.CharField(max_length=100)
    responsabile_laboratorio = models.BooleanField(default=False)



# TECNICO

#GESTISCE:
class Laboratorio(models.Model):
    id_laboratorio = models.AutoField(primary_key=True)
    tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    edificio = models.CharField(max_length=100)
    piano = models.CharField(max_length=10)
    stanza = models.CharField(max_length=10)

class Attrezzatura(models.Model):
    STATO_SCELTE = [
        ('funzionante', 'Funzionante'),
        ('manutenzione', 'In manutenzione'),
        ('non_disponibile', 'Non disponibile'),
    ]
    id_attrezzatura = models.AutoField(primary_key=True)
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    codice_inventario = models.CharField(max_length=50)
    stato = models.CharField(max_length=20, choices=STATO_SCELTE, default='funzionante')


#PROFESSORE:

#PUO CREARE:
class ProgettoSperimentale(models.Model):
    id_progetto = models.AutoField(primary_key=True)
    responsabile = models.ForeignKey(Professore, on_delete=models.CASCADE)
    titolo = models.CharField(max_length=100)
    descrizione = models.TextField()
    obiettivi = models.TextField()
    data_inizio = models.DateField()
    data_fine = models.DateField()

class Esperimento(models.Model):
    id_esperimento = models.AutoField(primary_key=True)
    progetto = models.ForeignKey(ProgettoSperimentale, on_delete=models.CASCADE)
    titolo = models.CharField(max_length=100)
    descrizione = models.TextField()
    obiettivi = models.TextField()
    materiali = models.TextField()
    data_inizio = models.DateField()
    data_fine = models.DateField()

#PUO PRENOTARE.
class PrenotazioneLaboratorio(models.Model):
    id_prenotazione = models.AutoField(primary_key=True)
    professore = models.ForeignKey(Professore, on_delete=models.CASCADE)
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    esperimento = models.OneToOneField(Esperimento, on_delete=models.CASCADE)  # Ogni esperimento ha una sola prenotazione
    data = models.DateField()
    ora_inizio = models.TimeField()
    ora_fine = models.TimeField()

    class Meta:
        unique_together = ('laboratorio', 'data', 'ora_inizio', 'ora_fine')

class PrenotazioneAttrezzatura(models.Model):
    id_prenotazione = models.AutoField(primary_key=True)
    professore = models.ForeignKey(Professore, on_delete=models.CASCADE)
    attrezzatura = models.ForeignKey(Attrezzatura, on_delete=models.CASCADE)
    esperimento = models.ForeignKey(Esperimento, on_delete=models.CASCADE)
    data = models.DateField()
    ora_inizio = models.TimeField()
    ora_fine = models.TimeField()

    class Meta:
        unique_together = ('attrezzatura', 'data', 'ora_inizio', 'ora_fine')


#STUDENTE

#PUO PRENOTARSI:
class PrenotazioneProgetto(models.Model):
    studente = models.ForeignKey(Studente, on_delete=models.CASCADE)
    progetto = models.ForeignKey(ProgettoSperimentale, on_delete=models.CASCADE)
    id_prenotazione = models.AutoField(primary_key=True)

    class Meta:
        unique_together = ('studente', 'progetto')

class PrenotazioneEsperimento(models.Model):
    studente = models.ForeignKey(Studente, on_delete=models.CASCADE)
    esperimento = models.ForeignKey(Esperimento, on_delete=models.CASCADE)
    id_prenotazione = models.AutoField(primary_key=True)

    class Meta:
        unique_together = ('studente', 'esperimento')

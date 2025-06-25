from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class Ruolo(models.TextChoices):
    PROFESSORE = 'Professore', _('Professore')
    STUDENTE = 'Studente', _('Studente')
    TECNICO = 'Tecnico', _('Tecnico')


class Utente(models.Model):

    matricola = models.CharField(max_length=7, primary_key=True, unique=True)
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    ruolo = models.CharField(max_length=10, choices=Ruolo.choices)

    # Attributi specifici per Professore
    dipartimento = models.CharField(max_length=100, blank=True, null=True)
    materia = models.CharField(max_length=100, blank=True, null=True)

    # Attributi specifici per Studente
    corso_di_studi = models.CharField(max_length=100, blank=True, null=True)
    anno = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])

    # Attributi specifici per Tecnico
    area_competenza = models.CharField(max_length=100, blank=True, null=True)
    is_responsabile = models.BooleanField(default=False)

    class Meta:
        unique_together = ('matricola', 'email')

    def __str__(self):
        return f"{self.matricola} - {self.nome} {self.cognome}"




class Laboratorio(models.Model):
    id_laboratorio = models.AutoField(primary_key=True)
    responsabile = models.OneToOneField(Utente, on_delete=models.CASCADE, limit_choices_to={'ruolo': Ruolo.TECNICO})
    nome = models.CharField(max_length=100)
    edificio = models.CharField(max_length=100)
    piano = models.IntegerField()
    stanza = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Attrezzatura(models.Model):
    class StatoAttrezzatura(models.TextChoices):
        FUNZIONANTE = 'Funzionante'
        MANUTENZIONE = 'In manutenzione'
        NON_DISPONIBILE = 'Non disponibile'

    codice_inventario = models.AutoField(primary_key=True)
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    stato = models.CharField(max_length=20, choices=StatoAttrezzatura.choices)

    def __str__(self):
        return f"{self.tipo} ({self.codice_inventario})"


class ProgettoSperimentale(models.Model):
    id_progetto = models.AutoField(primary_key=True)
    docente = models.ForeignKey(Utente, on_delete=models.CASCADE, limit_choices_to={'ruolo': Ruolo.PROFESSORE})
    titolo = models.CharField(max_length=100)
    descrizione = models.TextField()
    obiettivi = models.TextField()
    data_inizio = models.DateField()
    data_fine = models.DateField()
    max_posti = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)])

    def __str__(self):
        return self.titolo


class Esperimento(models.Model):
    id_esperimento = models.AutoField(primary_key=True)
    progetto = models.ForeignKey(ProgettoSperimentale, on_delete=models.CASCADE)
    titolo = models.CharField(max_length=100)
    descrizione = models.TextField(max_length=200)
    obiettivi = models.TextField(max_length=100)
    data_inizio = models.DateField()
    data_fine = models.DateField()

    def __str__(self):
        return self.titolo


class PrenotazioneLaboratorio(models.Model):
    id_prenotazione_lab = models.AutoField(primary_key=True)
    docente = models.ForeignKey(Utente, on_delete=models.CASCADE, limit_choices_to={'ruolo': Ruolo.PROFESSORE})
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    esperimento = models.ForeignKey(Esperimento, on_delete=models.CASCADE)
    data = models.DateField()
    ora_inizio = models.TimeField()
    ora_fine = models.TimeField()

    def __str__(self):
        return f"{self.docente} - {self.laboratorio} - {self.data}"


class PrenotazioneAttrezzatura(models.Model):
    id_prenotazione_attr = models.AutoField(primary_key=True)
    docente = models.ForeignKey(Utente, on_delete=models.CASCADE, limit_choices_to={'ruolo': Ruolo.PROFESSORE})
    attrezzatura = models.ForeignKey(Attrezzatura, on_delete=models.CASCADE)
    esperimento = models.ForeignKey(Esperimento, on_delete=models.CASCADE)
    data = models.DateField()
    ora_inizio = models.TimeField()
    ora_fine = models.TimeField()

    class Meta:
        unique_together = ('attrezzatura', 'data', 'ora_inizio')

    def __str__(self):
        return f"{self.docente} - {self.attrezzatura} - {self.data}"


class PartecipazioneProgetto(models.Model):
    id_partecipazione_prog = models.AutoField(primary_key=True)
    progetto = models.ForeignKey(ProgettoSperimentale, on_delete=models.CASCADE)
    studente = models.ForeignKey(Utente, on_delete=models.CASCADE, limit_choices_to={'ruolo': Ruolo.STUDENTE})

    class Meta:
        unique_together = ('progetto', 'studente')


    def __str__(self):
        return f"{self.studente} -> {self.progetto}"


class PartecipazioneEsperimento(models.Model):
    id_partecipazione_esp = models.AutoField(primary_key=True)
    esperimento = models.ForeignKey(Esperimento, on_delete=models.CASCADE)
    studente = models.ForeignKey(Utente, on_delete=models.CASCADE, limit_choices_to={'ruolo': Ruolo.STUDENTE})

    class Meta:
         unique_together = ('esperimento', 'studente')


    def __str__(self):
        return f"{self.studente} -> {self.esperimento}"

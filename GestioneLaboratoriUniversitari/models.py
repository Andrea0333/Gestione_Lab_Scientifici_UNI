from django.contrib.auth.models import User
from django.db import models

class Profilo(models.Model):
    RUOLI = [
        ('professore', 'Professore'),
        ('studente', 'Studente'),
        ('tecnico', 'Tecnico'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ruolo = models.CharField(max_length=20, choices=RUOLI)
    matricola = models.CharField(max_length=6, unique=True)


class Professore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dipartimento = models.CharField(max_length=100)
    materia = models.CharField(max_length=100)


class Studente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    corso_laurea = models.CharField(max_length=100)
    anno = models.PositiveIntegerField()


class Tecnico(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    area_competenza = models.CharField(max_length=100)
    responsabile_laboratorio = models.BooleanField(default=False)


class Laboratorio(models.Model):
    tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    edificio = models.CharField(max_length=100)
    piano = models.CharField(max_length=10)
    stanza = models.CharField(max_length=10)

    def __str__(self):
        return self.nome


class Attrezzatura(models.Model):
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    codice_inventario = models.CharField(max_length=50)
    stato = models.CharField(
        max_length=20,
        choices=[
            ('funzionante', 'Funzionante'),
            ('manutenzione', 'In manutenzione'),
            ('non_disponibile', 'Non disponibile')
        ],
        default='funzionante'
    )

    def __str__(self):
        return self.nome


class ProgettoSperimentale(models.Model):
    responsabile = models.ForeignKey(Professore, on_delete=models.CASCADE)
    titolo = models.CharField(max_length=100)
    descrizione = models.TextField()
    obiettivi = models.TextField()
    data_inizio = models.DateField()
    data_fine = models.DateField()
    max_partecipanti = models.PositiveIntegerField(default=15)


class Esperimento(models.Model):
    progetto = models.ForeignKey(ProgettoSperimentale, on_delete=models.CASCADE)
    titolo = models.CharField(max_length=100)
    descrizione = models.TextField()
    obiettivi = models.TextField()
    materiali = models.TextField()
    data_inizio = models.DateField()
    data_fine = models.DateField()
    max_partecipanti = models.PositiveIntegerField(default=15)


class PrenotazioneLaboratorio(models.Model):
    professore = models.ForeignKey(Professore, on_delete=models.CASCADE)
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    esperimento = models.OneToOneField(Esperimento, on_delete=models.CASCADE)
    data = models.DateField()
    ora_inizio = models.TimeField()
    ora_fine = models.TimeField()

    class Meta:
        unique_together = ('laboratorio', 'data', 'ora_inizio', 'ora_fine')


class PrenotazioneAttrezzatura(models.Model):
    professore = models.ForeignKey(Professore, on_delete=models.CASCADE)
    attrezzatura = models.ForeignKey(Attrezzatura, on_delete=models.CASCADE)
    esperimento = models.ForeignKey(Esperimento, on_delete=models.CASCADE)
    data = models.DateField()
    ora_inizio = models.TimeField()
    ora_fine = models.TimeField()

    class Meta:
        unique_together = ('attrezzatura', 'data', 'ora_inizio', 'ora_fine')


class PrenotazioneProgetto(models.Model):
    studente = models.ForeignKey(Studente, on_delete=models.CASCADE)
    progetto = models.ForeignKey(ProgettoSperimentale, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('studente', 'progetto')


class PrenotazioneEsperimento(models.Model):
    studente = models.ForeignKey(Studente, on_delete=models.CASCADE)
    esperimento = models.ForeignKey(Esperimento, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('studente', 'esperimento')

from django.contrib import admin

from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profilo, Professore, Studente, Tecnico, Laboratorio, Attrezzatura, ProgettoSperimentale, Esperimento, PrenotazioneLaboratorio, PrenotazioneAttrezzatura, PrenotazioneProgetto, PrenotazioneEsperimento


@admin.register(Profilo)
class ProfiloAdmin(admin.ModelAdmin):
    list_display = ('user', 'ruolo')
    list_filter = ('ruolo',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(Professore)
class ProfessoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'dipartimento', 'materia')
    search_fields = ('user__username', 'materia')


@admin.register(Studente)
class StudenteAdmin(admin.ModelAdmin):
    list_display = ('user', 'corso_laurea', 'anno')
    search_fields = ('user__username', 'corso_laurea')


@admin.register(Tecnico)
class TecnicoAdmin(admin.ModelAdmin):
    list_display = ('user', 'area_competenza', 'responsabile_laboratorio')
    list_filter = ('responsabile_laboratorio',)


@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tecnico', 'edificio', 'piano', 'stanza')
    search_fields = ('nome', 'edificio')


@admin.register(Attrezzatura)
class AttrezzaturaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'laboratorio', 'codice_inventario', 'stato')
    list_filter = ('stato',)


@admin.register(ProgettoSperimentale)
class ProgettoSperimentaleAdmin(admin.ModelAdmin):
    list_display = ('titolo', 'responsabile', 'data_inizio', 'data_fine')


@admin.register(Esperimento)
class EsperimentoAdmin(admin.ModelAdmin):
    list_display = ('titolo', 'progetto', 'data_inizio', 'data_fine')


@admin.register(PrenotazioneLaboratorio)
class PrenotazioneLaboratorioAdmin(admin.ModelAdmin):
    list_display = ('laboratorio', 'esperimento', 'data', 'ora_inizio', 'ora_fine')


@admin.register(PrenotazioneAttrezzatura)
class PrenotazioneAttrezzaturaAdmin(admin.ModelAdmin):
    list_display = ('attrezzatura', 'esperimento', 'data', 'ora_inizio', 'ora_fine')


@admin.register(PrenotazioneProgetto)
class PrenotazioneProgettoAdmin(admin.ModelAdmin):
    list_display = ('studente', 'progetto')


@admin.register(PrenotazioneEsperimento)
class PrenotazioneEsperimentoAdmin(admin.ModelAdmin):
    list_display = ('studente', 'esperimento')


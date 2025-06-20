# Generated by Django 5.2.3 on 2025-06-19 12:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Laboratorio',
            fields=[
                ('id_laboratorio', models.AutoField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=100)),
                ('edificio', models.CharField(max_length=100)),
                ('piano', models.CharField(max_length=10)),
                ('stanza', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Utente',
            fields=[
                ('matricola', models.CharField(max_length=11, primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=50)),
                ('cognome', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=50)),
                ('tipo', models.CharField(choices=[('professore', 'Professore'), ('tecnico', 'Tecnico'), ('studente', 'Studente')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='ProgettoSperimentale',
            fields=[
                ('id_progetto', models.AutoField(primary_key=True, serialize=False)),
                ('titolo', models.CharField(max_length=100)),
                ('descrizione', models.TextField()),
                ('obiettivi', models.TextField()),
                ('data_inizio', models.DateField()),
                ('data_fine', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Attrezzatura',
            fields=[
                ('id_attrezzatura', models.AutoField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=100)),
                ('marca', models.CharField(max_length=100)),
                ('codice_inventario', models.CharField(max_length=50)),
                ('stato', models.CharField(choices=[('funzionante', 'Funzionante'), ('manutenzione', 'In manutenzione'), ('non_disponibile', 'Non disponibile')], default='funzionante', max_length=20)),
                ('laboratorio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.laboratorio')),
            ],
        ),
        migrations.CreateModel(
            name='Professore',
            fields=[
                ('utente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='sistema.utente')),
                ('dipartimento', models.CharField(max_length=100)),
                ('materia', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Studente',
            fields=[
                ('utente', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='sistema.utente')),
                ('corso_laurea', models.CharField(max_length=100)),
                ('anno', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Tecnico',
            fields=[
                ('utente', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='sistema.utente')),
                ('area_competenza', models.CharField(max_length=100)),
                ('responsabile_laboratorio', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Esperimento',
            fields=[
                ('id_esperimento', models.AutoField(primary_key=True, serialize=False)),
                ('titolo', models.CharField(max_length=100)),
                ('descrizione', models.TextField()),
                ('obiettivi', models.TextField()),
                ('materiali', models.TextField()),
                ('data_inizio', models.DateField()),
                ('data_fine', models.DateField()),
                ('progetto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.progettosperimentale')),
            ],
        ),
        migrations.AddField(
            model_name='progettosperimentale',
            name='responsabile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.professore'),
        ),
        migrations.CreateModel(
            name='PrenotazioneLaboratorio',
            fields=[
                ('id_prenotazione', models.AutoField(primary_key=True, serialize=False)),
                ('data', models.DateField()),
                ('ora_inizio', models.TimeField()),
                ('ora_fine', models.TimeField()),
                ('esperimento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.esperimento')),
                ('laboratorio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.laboratorio')),
                ('professore', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.professore', unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='laboratorio',
            name='tecnico',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.tecnico'),
        ),
        migrations.CreateModel(
            name='PrenotazioneAttrezzatura',
            fields=[
                ('id_prenotazione', models.AutoField(primary_key=True, serialize=False)),
                ('data', models.DateField()),
                ('ora_inizio', models.TimeField()),
                ('ora_fine', models.TimeField()),
                ('attrezzatura', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.attrezzatura')),
                ('esperimento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.esperimento')),
                ('professore', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.professore')),
            ],
            options={
                'unique_together': {('attrezzatura', 'data', 'ora_inizio', 'ora_fine')},
            },
        ),
        migrations.CreateModel(
            name='PrenotazioneProgetto',
            fields=[
                ('id_prenotazione', models.AutoField(primary_key=True, serialize=False)),
                ('progetto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.progettosperimentale')),
                ('studente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.studente')),
            ],
            options={
                'unique_together': {('studente', 'progetto')},
            },
        ),
        migrations.CreateModel(
            name='PrenotazioneEsperimento',
            fields=[
                ('id_prenotazione', models.AutoField(primary_key=True, serialize=False)),
                ('esperimento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.esperimento')),
                ('studente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.studente')),
            ],
            options={
                'unique_together': {('studente', 'esperimento')},
            },
        ),
    ]

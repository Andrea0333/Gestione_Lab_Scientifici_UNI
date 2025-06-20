"""
URL configuration for GestioneLaboratoriScientificiUNI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from sistema import views


urlpatterns = [
    path('admin/', admin.site.urls),
path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registrazione/', views.registrazione_view, name='registrazione'),
    path('registrazione/professore/', views.registrazione_professore, name='registrazione_professore'),
    path('registrazione/studente/', views.registrazione_studente, name='registrazione_studente'),
    path('registrazione/tecnico/', views.registrazione_tecnico, name='registrazione_tecnico'),

    path('dashboard/professore/', views.dashboard_professore, name='dashboard_professore'),
    path('crea_progetto/', views.crea_progetto, name='crea_progetto'),

    path('elimina_progetto/', views.elimina_progetto, name='elimina_progetto'),
    path('progetto/<int:progetto_id>/esperimenti/', views.lista_esperimenti, name='lista_esperimenti'),
    path('crea_esperimento/<int:progetto_id>/', views.crea_esperimento, name='crea_esperimento'),
    path('esperimento/<int:id>/partecipanti/', views.partecipanti_esperimento, name='partecipanti_esperimento'),
]

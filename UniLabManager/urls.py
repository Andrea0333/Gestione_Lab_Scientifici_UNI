"""
URL configuration for UniLabManager project.

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
from GestioneLaboratoriUniversitari import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home_view, name='home'),

    path('registrazione', views.registrazione_view, name='registrazione'),
    path('registrazione/professore/', views.registrazione_professore_view, name='registrazione_professore'),
    path('registrazione/studente/', views.registrazione_studente_view, name='registrazione_studente'),
    path('registrazione/tecnico/', views.registrazione_tecnico_view, name='registrazione_tecnico'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/professore/', views.dashboard_professore, name='dashboard_professore'),

    path('progetto/nuovo/', views.crea_progetto_view, name='crea_progetto'),

    path('dashboard/studente/', views.dashboard_studente, name='dashboard_studente'),
    path('dashboard/tecnico/', views.dashboard_tecnico, name='dashboard_tecnico'),
]

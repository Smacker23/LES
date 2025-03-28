from django import template

from configuracao.models import Diaaberto
from utilizadores.models import Utilizador, ProfessorUniversitario, Participante, Colaborador, Coordenador, Administrador
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
register = template.Library()

@register.filter(name='get_pertence_dia_aberto')
def get_pertence_dia_aberto(value):
    if Diaaberto.objects.all().filter(questionarioid=value):
        return "Sim"
    else:
        return "Não"


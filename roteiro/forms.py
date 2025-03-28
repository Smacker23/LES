from django.forms import *
from datetime import datetime
from configuracao.models import Campus, Horario, Espaco, Departamento
from roteiro.models import Roteiro


def get_choices_time():
    return [(str(t), t) for t in range(30, 361, 30)]


class DateTimeWidget(DateTimeInput):

    def __init__(self, attrs=None, format=None, input_type=None, default=None):
        # input_type = 'datetime-local'
        now = datetime.now()
        if input_type is not None:
            self.input_type = input_type
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            if default is not None:
                self.attrs = {'class': 'input', 'value': default}
            else:
                self.attrs = {'class': 'input', 'value': str(now.date()) + ' ' + str(now.time().strftime('%H:%M'))}
        if format is not None:
            self.format = format
        else:
            self.format = '%Y-%m-%d'





class RoteiroForm(ModelForm):
    duracaoesperada = ChoiceField(choices=get_choices_time)

    class Meta:
        model = Roteiro
        exclude = ['id', 'coordenadorID', 'diaabertoid', 'estado', 'tema']
        widgets = {
            'nome': TextInput(attrs={'class': 'input'}),
            'descricao': Textarea(attrs={'class': 'textarea'}),
            'publicoalvo': Select(),
            'participantesmaximo': NumberInput(attrs={'class': 'input'}),
            'duracaoesperada': Select(),
        }




def get_dep_choices():
    return [(-1, 'Mostra todos os Departamentos')] + [(departamento.id, departamento.nome) for departamento in
                                                      Departamento.objects.all()]


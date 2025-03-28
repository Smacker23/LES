from django.forms import *
from django import forms
from atividades.models import Tema
from questionario.models import Questionario, Pergunta, TemaPerg, TipoResposta, PergQuest, EstadosQuest, \
    questionario_escalaresposta, Resposta


# from questionario.models import Questionario, Pergunta, Resposta

class QuestionarioForm(ModelForm):
    class Meta:
        model = Questionario
        exclude = ['id', 'estadoquestid']
        widgets = {
            'titulo': TextInput(attrs={'class': 'input'}),
        }


class Questionario2Form(forms.Form):
    questionario = forms.ModelChoiceField(
        queryset=Questionario.objects.all(),
        widget=forms.Select(attrs={'class': 'input'}),
        label='', # Isto removerá o label
        empty_label=None
    )

# class Questionario2Form(ModelForm):
#     questionarios = forms.ModelChoiceField(queryset=Questionario.objects.all(), empty_label=None)
    # class Meta:
    #     model = Questionario
    #     exclude = ['id', 'estadoquestid', 'titulo']
    #     widgets = {
    #         'titulo': forms.Select(attrs={'class': 'input'}),
    #     }


class PerguntasForm(ModelForm):
    class Meta:
        model = Pergunta
        exclude = ['id', 'questionarioid', 'subtemaid']
        widgets = {
            'pergunta': TextInput(attrs={'class': 'input'}),
        }


class RespostaForm(ModelForm):
    class Meta:
        model = Resposta
        fields = ['resposta']
        widgets = {
            'pergunta': HiddenInput(),
            'questionario': HiddenInput(),
        }

class TemaFormPerg(ModelForm):
    class Meta:
        model = TemaPerg
        exclude = ['id']
        widgets = {
            'tema': TextInput(attrs={'class': 'input'}),
        }


class TipoRespostaForm(ModelForm):
    class Meta:
        model = TipoResposta
        exclude = ['id']
        widgets = {
            'tiporesposta': TextInput(attrs={'class': 'input'}),
            'escala': Select(attrs={'class': 'input'}),
        }


class PergQuestForm(ModelForm):
    class Meta:
        model = PergQuest
        exclude = ['id']
        widgets = {}

class EstadoForm(ModelForm):
    class Meta:
        model = EstadosQuest
        exclude = ['id']
        widgets = {
            'nome': TextInput(attrs={'class': 'input'}),
            'cor': TextInput(attrs={'type': 'color', 'class': 'color-picker', 'id': 'colorpicker', 'onchange': 'displayHexColor()'}),
        }


class EscalaRespostaForm(ModelForm):
    class Meta:
        model = questionario_escalaresposta
        fields = ['nome', 'valores']
        widgets = {
            'nome': TextInput(attrs={'class': 'input'}),
            'valores': Textarea(attrs={'class': 'textarea', 'rows': 3}),
        }
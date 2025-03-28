import django_filters
from django.db.models import Exists, OuterRef
from questionario.models import *
from configuracao.models import *

def get_estados(queryset, name, value):
    return queryset.filter(
        Exists(EstadosQuest.objects.filter(
            id=OuterRef('pk'),
            estado=value,
        ))
    )

class QuestionarioFilter(django_filters.FilterSet):
    titulo = django_filters.CharFilter(field_name="titulo", lookup_expr='icontains')
    # ano = django_filters.CharFilter(field_name='ano', lookup_expr='icontains')
    estados = django_filters.CharFilter(method=get_estados)

    class Meta:
        model = Questionario
        fields = '__all__'

class TemaPergFilter(django_filters.FilterSet):
    tema = django_filters.CharFilter(
        field_name="tema", lookup_expr='icontains')


    class Meta:
        print("passaste pelo filtro")
        model = TemaPerg
        fields = '__all__'


class TipoRespostaFilter(django_filters.FilterSet):
    tiporesposta = django_filters.CharFilter(
        field_name="tiporesposta", lookup_expr='icontains')


    class Meta:
        print("passaste pelo filtro")
        model = TipoResposta
        fields = '__all__'


class EstadosFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(
        field_name="estado", lookup_expr='icontains')

    class Meta:
        model = EstadosQuest
        fields = '__all__'
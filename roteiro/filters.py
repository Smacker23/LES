import django_filters
from django.db.models import Exists, OuterRef

import roteiro
from questionario.models import *
from roteiro.models import Roteiro


class RoteirosFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(
        field_name="Nome", lookup_expr='icontains')

    class Meta:
        model = Roteiro
        fields = '__all__'
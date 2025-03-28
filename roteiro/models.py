# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils.safestring import mark_safe
from django.urls import reverse

from datetime import date

from atividades.models import Atividade, Sessao


class Roteiro(models.Model):
    # Field name made lowercase.
    id = models.AutoField(db_column='ID', primary_key=True)
    # Field name made lowercase.
    nome = models.CharField(db_column='Nome', max_length=255)
    # Field name made lowercase.
    descricao = models.TextField(db_column='Descricao')

    coordenadorID = models.ForeignKey(
        'utilizadores.Coordenador', models.CASCADE, db_column='coordenadorID')
    diaabertoid = models.ForeignKey(
        'configuracao.Diaaberto', models.CASCADE, db_column='diaabertoID')
    participantesmaximo = models.IntegerField(db_column='nrmaximodeparticipantes')
    duracaoesperada = models.IntegerField(db_column='duracaoEsperada')
    publicosalvo = (("Ciencias e Tecnologia", "CiÃªncias e Tecnologia"),
                    ("Linguas e HumanidadesA", "Linguas e Humanidades"), ("Economia", "Economia"))
    publicoalvo = models.CharField(
        db_column='Publicoalvo', max_length=255, choices=publicosalvo, default='')

    estado = models.ForeignKey('questionario.EstadosQuest', models.CASCADE, db_column='EstadoRoteiroId', null=True)
    tema = models.ForeignKey('atividades.Tema', models.CASCADE,
                             db_column='Tema', blank=False, null=False)

    @property
    def getRoteiroEstado(self):
        return self.estado.nome

    @property
    def getRoteiroCor(self):
        return self.estado.cor
    @property
    def getRoteiroID(self):
        return self.id

    @property
    def getRoteiroNome(self):
        return self.nome

    @property
    def getRoteiroDescricao(self):
        return self.descricao

    @property
    def getRoteiroCoordenadorID(self):
        return self.coordenadorID

    @property
    def getRoteiroDiaAbertoID(self):
        return self.diaabertoid

    @property
    def getRoteiroParticipantesMaximo(self):
        return self.participantesmaximo

    @property
    def getRoteiroDuracao(self):
        return self.duracaoesperada

    @property
    def getRoteiroPublicoAlvo(self):
        return self.publicoalvo

    def getRoteiro_(self):
        return Roteiro.objects.filter(nome=self)

    def getAtividade_(self):
        return Atividade.objects.filter(roteiro_id=self.id)

    def getSessao_(self):
        return Sessao.objects.filter(roteiro=self.id)

    class Meta:
        db_table = 'roteiro'

    def __str__(self):
        return self.nome
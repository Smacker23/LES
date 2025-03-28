from django.db import models

from configuracao.models import Diaaberto


# Create your models here.
class EstadosQuest(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome = models.CharField(db_column='Nome', max_length=100, null=False, blank=False)
    cor = models.CharField(db_column='Cor', max_length=10, null=False, blank=False, default='#0033ff')

    class Meta:
        db_table = 'EstadosQuest'
    def __str__(self):
        return str(self.nome)

    @property
    def getEstadoId(self):
        return self.id

    @property
    def getEstadoNome(self):
        return self.nome

    @property
    def getEstadoCor(self):
        return self.cor


class TemaPerg(models.Model):
    # Field name made lowercase.
    id = models.AutoField(db_column='ID', primary_key=True)
    # Field name made lowercase.
    tema = models.CharField(db_column='Tema', max_length=64, null=True, blank=True)

    @property
    def get_num_perguntas(self):
        return Pergunta.objects.filter(temaid=self).count()

    class Meta:
        db_table = 'TemaPerg'

    def __str__(self):
        return str(self.tema)


class Questionario(models.Model):
    # Field name made lowercase.
    id = models.AutoField(db_column='ID', primary_key=True)
    titulo = models.CharField(db_column='Titulo', max_length=255, blank=True, null=True)
    # dateid = models.ForeignKey('configuracao.Diaaberto', models.CASCADE, db_column='DiaAbertoDateId', null=True,
    #                            blank=True)
    estadoquestid = models.ForeignKey('EstadosQuest', models.CASCADE, db_column='EstadoQuestId', null=True)

    @property
    def getQuestionarioID(self):
        return self.id

    @property
    def getQuestionarioCor(self):
        return self.estadoquestid.cor

    @property
    def get_pertence_dia_aberto(value):
        if Diaaberto.objects.all().filter(questionarioid=value):
            return "Sim"
        else:
            return "Não"

    @property
    def get_responsavel(value):
        if Diaaberto.objects.all().filter(questionarioid=value):
            return Diaaberto.objects.get(questionarioid=value).administradorutilizadorid.full_name
        else:
            return "---------"

    @property
    def getQuestionarioAnswerCounter(self):
        counter = 0
        perguntas = PergQuest.objects.all().filter(questionarioid=self.id)
        for perg in perguntas:
            print(counter)
            counter += Resposta.objects.all().filter(perguntaID=perg).count()
            print(counter)
        print(counter)
        return counter

    @property
    def checkQuestionarioIsFromDiaAberto(self):
        return Diaaberto.objects.all().filter(questionarioid=self.id).count()

    # @property
    # def getQuestionarioDateID(self):
    #     return self.dateid

    @property
    def getQuestionarioEstado(self):
        return self.estadoquestid.nome

    @property
    def getQuestionarioEstadoID(self):
        return self.estadoquestid.id
    @property
    def getQuestionarioPergutnas(self):
        return PergQuest.objects.all().filter(questionarioid=self.id)
    class Meta:
        db_table = 'Questionario'

    def __str__(self):
        return str(self.titulo)


class TipoResposta(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    tiporesposta = models.CharField(db_column='TipoResposta', default='', max_length=255, null=True, blank=True)
    escala = models.ForeignKey('questionario_escalaresposta', models.CASCADE, db_column='EscalaResposta', default=1, null=False, blank=False)
    class Meta:
        db_table = 'TipoResposta'

    def __str__(self):
        return str(self.tiporesposta)


class PergQuest(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    perguntaid = models.ForeignKey('Pergunta', models.CASCADE, db_column='PergQuestId', null=False)
    questionarioid = models.ForeignKey('Questionario', models.CASCADE, db_column='QuestionarioID', null=False)

    class Meta:
        db_table = 'PergQuest'


class Pergunta(models.Model):
    # Field name made lowercase.
    id = models.AutoField(db_column='ID', primary_key=True)
    pergunta = models.CharField(db_column='Pergunta', default='', max_length=255, blank=True)
    # questionarioid = models.ForeignKey('Questionario', models.CASCADE, db_column='QuestionarioID', blank=True,
    #                                    null=False)
    temaid = models.ForeignKey('TemaPerg', models.CASCADE, default=1, db_column='TemaID', null=False)
    tiporespostaid = models.ForeignKey('TipoResposta', models.CASCADE, default=1, db_column='TipoRespostaID',
                                       null=False)

    def getTema(self):
        return self.temaid.tema

    class Meta:
        db_table = 'Pergunta'

    def __str__(self):
        return str(self.pergunta)


class Resposta(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    perguntaID = models.ForeignKey('Pergunta', models.CASCADE, db_column='PerguntaID', blank=True, null=False)
    resposta = models.CharField(db_column='Resposta', default='', max_length=255, blank=True)
    subtemaid = models.CharField(db_column='SubTemaId', default='', max_length=255, blank=True,null=True)
    idcodigo = models.ForeignKey('CodigoQuestionario', models.CASCADE, db_column='CodigoID', blank=True, null=False,
                                 default='')

    class Meta:
        db_table = 'Resposta'

    def __str__(self):
        return str(self.resposta)


class CodigoQuestionario(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    inscricaoID = models.ForeignKey('inscricoes.Inscricaosessao', models.CASCADE, db_column='InscrincaoID', blank=True,
                                    null=False)
    npessoas = models.IntegerField(db_column='npessoas', default=0, blank=True)
    codigo = models.CharField(db_column='codigo', default='', max_length=255, blank=True)

    class Meta:
        db_table = 'CodigoQuestionario'

    def __str__(self):
        return str(self.codigo)



class questionario_escalaresposta(models.Model):
    nome = models.CharField(max_length=100)
    valores = models.TextField()

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'questionario_escalaresposta'  # Garantir que o nome da tabela está correto


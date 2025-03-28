import django_tables2 as django_tables

from atividades.models import Tema, Atividade
from configuracao.models import Diaaberto
from roteiro.models import Roteiro
from utilizadores.models import Administrador
from django.db.models import Count
from questionario.models import Questionario, TemaPerg, TipoResposta, EstadosQuest, questionario_escalaresposta
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import F
import django_tables2 as django_tables
import django_tables2 as tables


class QuestionarioTable(django_tables.Table):
    titulo = django_tables.Column('titulo')
    # ano = django_tables.Column(accessor='getQuestionarioDateID')
    estado = django_tables.Column(accessor='getQuestionarioEstado', attrs={"th": {"width": "130"}})
    acoes = django_tables.Column('Ações', empty_values=(),
                                 orderable=False, attrs={"th": {"width": "200"}})

    class Meta:
        model = Questionario
        sequence = ('titulo', 'estado', 'acoes')

    def before_render(self, request):
        self.columns.hide('id')
        # self.columns.hide('dateid')
        self.columns.hide('estadoquestid')

    # def order_ano(self, queryset, is_descending):
    #     # Ordenar pelo campo associado (exemplo: `dateid`):
    #     queryset = queryset.order_by(F('dateid').desc() if is_descending else F('dateid').asc())
    #     return (queryset, True)

    def render_estado(self, record):
        return format_html(f"""
                 <span class="tag is-warning" style="background-color: {record.getQuestionarioCor}; font-size: small; min-width: 110px;">
                    {record.getQuestionarioEstado}
                </span>
                """)

    def render_acoes(self, record):
        botao_editar = f"""
                            <a data-tooltip="editar" onclick="alert2.render('O questionário não pode ser editado no estado {record.getQuestionarioEstado}.','{reverse('questionarios:consultar-questionarios-admin')}')">
                                <span class="icon">
                                      <i class="fas fa-pencil-alt aria-hidden="true" style="color: #F4B400"></i>
                                </span>
                            </a> 
                        """
        botao_responder = f"""
                                <a data-tooltip="responder" onclick="alert2.render('O questionário não pode ser respondido no estado {record.getQuestionarioEstado}.','{reverse('questionarios:consultar-questionarios-admin')}')">
                                    <span class="icon">
                                            <i class="fas fa-reply" aria-hidden="true" style="color: #3273DC"></i>
                                    </span>
                                </a> 
                            """
        botao_publicar = f"""
                                <a data-tooltip="publicar" onclick="alert2.render('O questionário não pode ser publicado no estado {record.getQuestionarioEstado}.','{reverse('questionarios:consultar-questionarios-admin')}')">
                                    <span class="icon">
                                            <i class="fas fa-upload" style="color:#DB2323"></i>
                                    </span>
                                </a> 
                             """
        botao_despoblicar = f"""
                                <a data-tooltip="validar" onclick="alert2.render('O questionário não pode ser validado no estado {record.getQuestionarioEstado}.','{reverse('questionarios:consultar-questionarios-admin')}')">
                                    <span class="icon">
                                            <i class="fas fa-check" aria-hidden="true" style="color: #1EE232"></i>
                                    </span>
                                </a> 
                             """
        botao_arquivar = f"""
                            <a data-tooltip="arquivar" onclick="alert2.render('O questionário não pode ser arquivado no estado {record.getQuestionarioEstado}.','{reverse('questionarios:consultar-questionarios-admin')}')">
                                <span class="icon">
                                       <i class="fas fa-archive" aria-hidden="true" style="color: #F4B400"></i>
                               </span>
                            </a> 
                         """

        if record.getQuestionarioEstado == "concluido":
            botao_arquivar = f"""
                               <a data-tooltip="Arquivar" href="{reverse('questionarios:arquivar-questionario', args=[record.getQuestionarioID])}">
                                   <span class="icon">
                                       <i class="fas fa-archive" aria-hidden="true" style="color: #F4B400"></i>
                                   </span>
                               </a>
                           """
        # if record.getQuestionarioEstado == "validado":
            # botao_responder = f"""
            #                    <a data-tooltip="Responder" href="{reverse('questionarios:responder-questionario', args=[record.getQuestionarioID])}">
            #                        <span class="icon">
            #                             <i class="fas fa-reply" aria-hidden="true" style="color: #3273DC"></i>
            #                        </span>
            #                    </a>
            #                """
        if record.getQuestionarioEstado == "validado":
            botao_publicar = f"""
                               <a data-tooltip="Publicar" href="{reverse('questionarios:publicar-questionario', args=[record.getQuestionarioID])}">
                                   <span class="icon">
                                        <i class="fas fa-upload" style="color:#DB2323"></i>
                                   </span>
                               </a>
                           """
            # botao_editar = f"""
            #                    <a data-tooltip="editar" href="{reverse('questionarios:editar-questionario', args=[record.getQuestionarioID])}">
            #                      <span class="icon">
            #                           <i class="fas fa-pencil-alt aria-hidden="true" style="color: #F4B400"></i>
            #                      </span>
            #                  </a>
            #              """

        if record.getQuestionarioEstado == "publicado":
            botao_responder = f"""
                               <a data-tooltip="Responder" href="{reverse('questionarios:responder-questionario', args=[record.getQuestionarioID])}">
                                   <span class="icon">
                                        <i class="fas fa-reply" aria-hidden="true" style="color: #3273DC"></i>
                                   </span>
                               </a>
                           """
            botao_despoblicar = f"""
                                <a data-tooltip="Despublicar" href="{reverse('questionarios:validar-questionario', args=[record.getQuestionarioID])}">
                                    <span class="icon">
                                        <i class="fas fa-check" aria-hidden="true" style="color: #1EE232"></i>
                                    </span>
                                </a>
                            """

        if record.getQuestionarioEstado == "pendente":
            botao_responder = f"""
                               <a data-tooltip="Responder" href="{reverse('questionarios:responder-questionario', args=[record.getQuestionarioID])}">
                                   <span class="icon">
                                        <i class="fas fa-reply" aria-hidden="true" style="color: #3273DC"></i>
                                   </span>
                               </a>
                           """
            botao_editar = f"""
                              <a data-tooltip="editar" href="{reverse('questionarios:editar-questionario', args=[record.getQuestionarioID])}">
                                  <span class="icon">
                                       <i class="fas fa-pencil-alt aria-hidden="true" style="color: #F4B400"></i>
                                  </span>
                              </a>
                          """

        if record.getQuestionarioEstado != "publicado" and record.checkQuestionarioIsFromDiaAberto <= 0:
            botao_apagar = f"""
                              <a data-tooltip="Eliminar" onclick="alert.render('Tem a certeza que pretende eliminar este questionário?','{reverse('questionarios:eliminarQuestionario', args=[record.getQuestionarioID])}')">
                                  <span class="icon has-text-danger">
                                    <i class="mdi mdi-trash-can mdi-24px"></i>
                                </span>
                              </a>
                          """

        elif record.getQuestionarioEstado == "publicado":
            botao_apagar = f"""
                              <a data-tooltip="Eliminar" onclick = "alert2.render('O questionário não pode ser eliminado no estado <strong>publicado</strong>.','{reverse('questionarios:consultar-estados-admin')}')" >
                                  <span class="icon has-text-danger">
                                    <i class="mdi mdi-trash-can mdi-24px"></i>
                                </span>
                              </a>
                          """
        else:
            botao_apagar = f"""
                              <a data-tooltip="Eliminar" onclick = "alert2.render('O questionário não pode ser eliminado, porque pertence a um<strong> dia aberto</strong>.','{reverse('questionarios:consultar-estados-admin')}')" >
                                  <span class="icon has-text-danger">
                                    <i class="mdi mdi-trash-can mdi-24px"></i>
                                  </span>
                              </a>
                          """
        return format_html(f"""
               <div>
                    {botao_apagar}
                    {botao_editar}
                    {botao_responder}
                    {botao_publicar}
                    {botao_despoblicar}
                    {botao_arquivar}
               </div>    
           """)


class TemaPergTable(django_tables.Table):
    perg_count = django_tables.Column('Perguntas com o Tema', accessor='get_num_perguntas')
    acoes = django_tables.Column('Ações', empty_values=(), orderable=False)

    class Meta:
        model = TemaPerg

    def before_render(self, request):
        self.columns.hide('id')

    def order_perg_count(self, queryset, is_descending):
        # Anotar o queryset para contar as perguntas por tema
        queryset = queryset.annotate(perg_count=Count('pergunta'))

        # Ordenar pelo campo anotado, perg_count
        queryset = queryset.order_by(("-" if is_descending else "") + "perg_count")

        return queryset, True


class TipoRespostaTable(django_tables.Table):
    acoes = django_tables.Column('Ações', empty_values=(), orderable=False)

    class Meta:
        model = TipoResposta

    def before_render(self, request):
        self.columns.hide('id')

    # def order_perguntas_count(self, queryset, is_descending):
    #     # print("entraste na ordem de perguntas")
    #     # print(queryset)
    #     queryset = queryset.annotate(perg_count=Count('pergunta')).order_by(("" if is_descending else "-") + "perg_count")
    #     return (queryset, True)


class DiaabertoTable(django_tables.Table):
    ano = django_tables.Column('Ano')
    questionarioid = django_tables.Column('Questionário', accessor='questionarioid.titulo')

    class Meta:
        model = Diaaberto
        fields = ('ano', 'questionarioid')  # Define as colunas a serem exibidas


class EscalasTable(django_tables.Table):
    nome = django_tables.Column('nome')
    valores = django_tables.Column('valores')

    class Meta:
        model = questionario_escalaresposta
        fields = ('nome', 'valores')

class EstadoTable(tables.Table):
    cor = tables.Column('Cor', accessor='getEstadoCor', orderable=False)
    acoes = tables.Column('Ações', empty_values=(), orderable=False)
    id = tables.Column('Id', accessor='getEstadoId', orderable=False)

    class Meta:
        model = EstadosQuest
        sequence = ('nome', 'cor', 'acoes')

    def definir_javascript(self):
        return format_html('<script type="text/javascript" src="{}"></script>', '{% static "js/js_custom.js" %}')

    def before_render(self, request):
        self.columns.hide('id')

    def render_cor(self, record):
        return format_html(f"""
                     <span class="tag is-warning" style="background-color: {record.getEstadoCor}; font-size: small; min-width: 12vw;">
                    </span>
                    """)

    def render_acoes(self, record):
        primeiro_botao = f"""
                           <a data-tooltip="Editar" href="{reverse('questionarios:editarEstado', kwargs={'estados_id': record.getEstadoId})}">
                               <span class="icon">
                                   <i class="fas fa-edit" aria-hidden="true" style="color: #F4B400"></i>
                               </span>
                           </a>
                       """

        if Questionario.objects.filter(estadoquestid=record.getEstadoId).exists():
            segundo_botao = f"""
                                <a data-tooltip="eliminar" onclick="alert2.render('O estado está a ser utilizado num questionário.<strong>Não o pode apagar.</strong>','{reverse('questionarios:consultar-estados-admin')}')">
                                    <span class="icon is-small">
                                        <i class="mdi mdi-trash-can-outline mdi-24px" style="color: #ff0000"></i>
                                    </span>
                                </a> 
                            """
        elif Roteiro.objects.filter(estado__id=record.getEstadoId).exists():
            segundo_botao = f"""
                                        <a data-tooltip="eliminar" onclick="alert2.render('O estado está a ser utilizado num roteiro.<strong>Não o pode apagar.</strong>','{reverse('questionarios:consultar-estados-admin')}')">
                                            <span class="icon is-small">
                                                <i class="mdi mdi-trash-can-outline mdi-24px" style="color: #ff0000"></i>
                                            </span>
                                        </a> 
                                    """
        elif Atividade.objects.filter(estado__id=record.getEstadoId).exists():
            segundo_botao = f"""
                                        <a data-tooltip="eliminar" onclick="alert2.render('O estado está a ser utilizado numa atividade.<strong>Não o pode apagar.</strong>','{reverse('questionarios:consultar-estados-admin')}')">
                                            <span class="icon is-small">
                                                <i class="mdi mdi-trash-can-outline mdi-24px" style="color: #ff0000"></i>
                                            </span>
                                        </a> 
                                    """
        else:
            segundo_botao = f"""
                            <a data-tooltip="Eliminar" onclick="alert.render('Tem a certeza que pretende eliminar este estado?','{reverse('questionarios:eliminarEstado', kwargs={'estados_id': record.getEstadoId})}')">
                                <span class="icon is-small">
                                    <i class="mdi mdi-trash-can-outline mdi-24px" style="color: #ff0000"></i>
                                </span>
                            </a> 
                        """

        return format_html(f"""
                           {primeiro_botao}
                           {segundo_botao}
                   """)

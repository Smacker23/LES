import django_tables2 as tables
from atividades.models import *
from django.utils.html import format_html
from django.db.models import Count


class CoordAtividadesTable(tables.Table):
    # acoes = tables.Column('Operações', empty_values=())
    professoruniversitarioutilizadorid = tables.Column('Professor')
    datasubmissao = tables.Column('Data de Submissão')
    acoes = tables.Column('Ações', empty_values=(),
                          orderable=False, attrs={"th": {"width": "55"}})

    class Meta:
        model = Atividade
        sequence = ('nome', 'professoruniversitarioutilizadorid', 'tipo', 'datasubmissao', 'estado', 'acoes')

    def before_render(self, request):
        self.columns.hide('id')
        self.columns.hide('descricao')
        self.columns.hide('nrcolaboradoresnecessario')
        self.columns.hide('publicoalvo')
        # self.columns.hide('tipo')
        self.columns.hide('dataalteracao')
        self.columns.hide('duracaoesperada')
        self.columns.hide('participantesmaximo')
        self.columns.hide('espacoid')
        self.columns.hide('tema')
        self.columns.hide('diaabertoid')

    def render_estado(self, record):
        return format_html(f"""
                 <span class="tag is-warning" style="background-color: {record.getAtividadeCor}; font-size: small; min-width: 110px;">
                    {record.getAtividadeEstado}
                </span>
                """)

    def render_professoruniversitarioutilizadorid(self, record):
        return str(record.professoruniversitarioutilizadorid.full_name)

    def render_acoes(self, record):
        if record.estado.nome != "Aceite" or record.roteiro is not None or record.diaabertoid.ano == 2024:
            botao = ""
        else:
            botao = f"""
                        <a href='{reverse("atividades:duplicar-atividade", args={record.pk})}'
                            data-tooltip="Duplicar">
                            <span class="mdi mdi-content-copy">
                                
                            </span>
                        </a>

                    """
        return format_html(f"""
        <div>
            {botao}
        </div>
        """)


class ProfAtividadesTable(tables.Table):
    acoes = tables.Column('Operações', empty_values=())
    datasubmissao = tables.Column('Data de Submissão')
    coordenador = tables.Column('Coordenador Responsavel', empty_values=())

    class Meta:
        model = Atividade
        sequence = ('nome', 'tipo', 'datasubmissao', 'coordenador', 'estado', 'acoes')

    def before_render(self, request):
        self.columns.hide('id')
        self.columns.hide('descricao')
        self.columns.hide('nrcolaboradoresnecessario')
        self.columns.hide('publicoalvo')
        self.columns.hide('professoruniversitarioutilizadorid')
        self.columns.hide('dataalteracao')
        self.columns.hide('duracaoesperada')
        self.columns.hide('participantesmaximo')
        self.columns.hide('espacoid')
        self.columns.hide('tema')
        self.columns.hide('diaabertoid')

    def render_estado(self, record):
        return format_html(f"""
                 <span class="tag is-warning" style="background-color: {record.getAtividadeCor}; font-size: small; min-width: 110px;">
                    {record.getAtividadeEstado}
                </span>
                """)

    def render_coordenador(self, record):
        if record.get_coord() is not None:
            return format_html(record.get_coord().full_name)

    def render_acoes(self, record):
        sessoes = Sessao.objects.filter(atividadeid=record)
        for sessao in sessoes:
            if sessao.vagas != record.participantesmaximo:
                return format_html(f"""
                <div></div>
                 """)

        if record.estado.nome != "Aceite" or record.roteiro is not None or record.diaabertoid.ano == 2024:
            botao = f"""
            <div>
                    <a id='edit' href="{reverse('atividades:alterarAtividade', kwargs={'id': record.pk})}">
                        <span class="icon is-small">
                            <i class="mdi mdi-circle-edit-outline mdi-24px"></i>
                        </span>
                    </a>
                &nbsp;               
                    <a onclick="alert.render('Tem a certeza que pretende eliminar esta Atividade?','{reverse('atividades:eliminarAtividade', kwargs={'id': record.pk})}')">
                        <span class="icon is-small">
                            <i class="mdi mdi-trash-can-outline mdi-24px" style="color: #ff0000"></i>
                        </span>
                    </a> 
            </div> 
        """
        else:
            botao = f"""
                        <a href='{reverse("atividades:duplicar-atividade", args={record.pk})}'
                            data-tooltip="Duplicar">
                            <span class="mdi mdi-content-copy">

                            </span>
                        </a>
                    <a id='edit' href="{reverse('atividades:alterarAtividade', kwargs={'id': record.pk})}">
                        <span class="icon is-small">
                            <i class="mdi mdi-circle-edit-outline mdi-24px"></i>
                        </span>
                    </a>
                &nbsp;               
                    <a onclick="alert.render('Tem a certeza que pretende eliminar esta Atividade?','{reverse('atividades:eliminarAtividade', kwargs={'id': record.pk})}')">
                        <span class="icon is-small">
                            <i class="mdi mdi-trash-can-outline mdi-24px" style="color: #ff0000"></i>
                        </span>
                    </a> 
                    """
        return format_html(f"""
        <div>
            {botao}
        </div>
        """)


class AdminAtividadesTable(tables.Table):
    professoruniversitarioutilizadorid = tables.Column('Professor')
    datasubmissao = tables.Column('Data de Submissão')

    class Meta:
        model = Atividade
        sequence = ('nome', 'professoruniversitarioutilizadorid', 'tipo', 'datasubmissao', 'estado')

    def before_render(self, request):
        self.columns.hide('id')
        self.columns.hide('descricao')
        self.columns.hide('nrcolaboradoresnecessario')
        self.columns.hide('publicoalvo')
        self.columns.hide('dataalteracao')
        self.columns.hide('duracaoesperada')
        self.columns.hide('participantesmaximo')
        self.columns.hide('espacoid')
        self.columns.hide('tema')
        self.columns.hide('diaabertoid')

    def render_estado(self, record):
        return format_html(f"""
                 <span class="tag is-warning" style="background-color: {record.getAtividadeCor}; font-size: small; min-width: 110px;">
                    {record.getAtividadeEstado}
                </span>
                """)

    def render_professoruniversitarioutilizadorid(self, record):
        return str(record.professoruniversitarioutilizadorid.full_name)

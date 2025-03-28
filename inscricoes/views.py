import csv

from django.shortcuts import get_object_or_404, redirect, render
from inscricoes.models import Inscricao, Inscricaosessao, Responsavel, Inscricaoprato
from inscricoes.templatetags.inscricoes_extras import almocampenhaDia, almocamPenhaInscricao, almocamgambelasDia, \
    almocamGambelasInscricao
from inscricoes.utils import add_vagas_sessao, enviar_mail_confirmacao_inscricao, init_form, nao_tem_permissoes, render_pdf, save_form, update_context, update_post
from atividades.models import Atividade, Sessao
from atividades.serializers import AtividadeSerializer
from atividades.filters import AtividadeFilter
from inscricoes.forms import AlmocoForm, InfoForm, InscricaoForm, ResponsavelForm, SessoesForm, TransporteForm, \
    EmptyForm
from questionario.models import Resposta, Pergunta, Questionario
from utilizadores.models import Administrador, Coordenador, Participante
from utilizadores.views import user_check
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from inscricoes.tables import InscricoesTable
from inscricoes.filters import InscricaoFilter
from django.db.models import Exists, OuterRef
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from formtools.wizard.views import SessionWizardView
from django.views import View
from django_tables2 import SingleTableMixin, RequestConfig
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.views import FilterView
from configuracao.models import Departamento, Diaaberto, Prato
from datetime import datetime
import pytz
from configuracao.tests.test_models import create_open_day
from _datetime import timedelta


from .forms import EditarPresencasForm



from django.views.generic import ListView
from django.urls import reverse_lazy
from .forms import (
    InfoForm, ResponsavelForm, InscricaoUltimaHoraForm, SessoesForm
)


def InscricaoPDF(request, pk):
    print("KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK")
    """ View que gera um PDF com os detalhes da inscrição """
    inscricao = get_object_or_404(Inscricao, pk=pk)
    erro_permissoes = nao_tem_permissoes(request, inscricao)
    if erro_permissoes and not request.user.groups.filter(name="Colaborador").exists():
        return erro_permissoes
    ano = inscricao.diaaberto.ano
    context = {
        'request': request,
        'inscricao': inscricao,
        'ano': ano,
    }
    return render_pdf("inscricoes/pdf.html", context, f"dia_aberto_ualg_{ano}.pdf")


class AtividadesAPI(ListAPIView):
    """ View que gera uma API readonly com as informações das Atividades e das suas sessões
        que vai ser usada para fazer inscrições nas sessões """
    class AtividadesPagination(PageNumberPagination):
        page_size = 10
        page_size_query_param = 'page_size'
        max_page_size = 100

    search_fields = '__all__'
    ordering_fields = '__all__'
    ordering = 'nome'
    filter_backends = (SearchFilter,
                       OrderingFilter, DjangoFilterBackend)
    queryset = Atividade.objects.filter(estado__nome="Aceite")
    serializer_class = AtividadeSerializer
    pagination_class = AtividadesPagination
    filterset_class = AtividadeFilter


class CriarInscricao(SessionWizardView):
    """ View que gera o formulário com passos para criar uma nova inscrição """
    form_list = [
        ('info', InfoForm),
        ('responsaveis', ResponsavelForm),
        ('escola', InscricaoForm),
        ('transporte', TransporteForm),
        ('almoco', AlmocoForm),
        ('sessoes', SessoesForm),
    ]

    def dispatch(self, request, *args, **kwargs):
        _user_check = user_check(request, [Participante])
        if _user_check['exists']:
            participante = _user_check['firstProfile']
            diaaberto = Diaaberto.current()
            if diaaberto is None:
                return redirect('utilizadores:mensagem', 12)
            if datetime.now(pytz.UTC) < diaaberto.datainscricaoatividadesinicio or datetime.now(pytz.UTC) > diaaberto.datainscricaoatividadesfim:
                m = f"Período de abertura das inscrições: {diaaberto.datainscricaoatividadesinicio.strftime('%d/%m/%Y')} até {diaaberto.datainscricaoatividadesfim.strftime('%d/%m/%Y')}"
                return render(request=request,
                              template_name="mensagem.html", context={'m': m, 'tipo': 'error', 'continuar': 'on'})
            self.instance_dict = {
                'responsaveis': Responsavel(nome=f"{participante.first_name} {participante.last_name}", email=participante.email, tel=participante.contacto)
            }
        else:
            return _user_check['render']
        return super(CriarInscricao, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        update_context(context, self.steps.current, self)
        if self.steps.current != 'info':
            context.update({
                'individual': self.get_cleaned_data_for_step('info')['individual']
            })
        visited = []
        for step in self.form_list:
            cleaned_data = self.get_cleaned_data_for_step(step)
            if cleaned_data:
                visited.append(True)
            else:
                visited.append(False)
        context.update({
            'visited': visited
        })
        return context

    def get_template_names(self):
        print(self.steps.current)
        return [f'inscricoes/inscricao_wizard_{self.steps.current}.html']

    def post(self, request, *args, **kwargs):
        # Envia a informação extra necessária para o formulário atual, após preenchê-lo.
        # Necessário para algumas validações especiais de backend, como verificar o número de alunos
        # inscritos para verificar inscritos nos almoços e nas sessões.
        current_step = request.POST.get(
            'criar_inscricao-current_step', self.steps.current)
        update_post(current_step, request.POST, self)
        go_to_step = self.request.POST.get(
            'wizard_goto_step', None)  # get the step name
        if go_to_step is not None:
            form = self.get_form(data=self.request.POST,
                                 files=self.request.FILES)

            if self.get_cleaned_data_for_step(current_step):
                if form.is_valid():
                    self.storage.set_step_data(self.steps.current,
                                               self.process_step(form))
                    self.storage.set_step_files(self.steps.current,
                                                self.process_step_files(form))
                else:
                    return self.render(form)
        return super(CriarInscricao, self).post(*args, **kwargs)

    def done(self, form_list, form_dict, **kwargs):
        # Guardar na Base de Dados
        responsaveis = form_dict['responsaveis'].save(commit=False)
        almoco = form_dict['almoco'].save(commit=False)
        inscricao = form_dict['escola'].save(commit=False)
        inscricao.participante = Participante.objects.filter(
            utilizador_ptr_id=self.request.user.id).first()
        inscricao.meio_transporte = form_dict['transporte'].cleaned_data['meio']
        if(form_dict['transporte'].cleaned_data['meio'] != 'outro'):
            inscricao.hora_chegada = form_dict['transporte'].cleaned_data['hora_chegada']
            inscricao.local_chegada = form_dict['transporte'].cleaned_data['local_chegada']
        inscricao.entrecampi = form_dict['transporte'].cleaned_data['entrecampi']
        inscricao.save()
        sessoes = form_dict['sessoes'].cleaned_data['sessoes']
        for sessaoid in sessoes:
            if sessoes[sessaoid] > 0:
                inscricao_sessao = Inscricaosessao(sessao=Sessao.objects.get(
                    pk=sessaoid), nparticipantes=sessoes[sessaoid], inscricao=inscricao)
                add_vagas_sessao(sessaoid, -sessoes[sessaoid])
                inscricao_sessao.save()
        responsaveis.inscricao = inscricao
        responsaveis.save()
        if almoco is not None:
            almoco.inscricao = inscricao
            almoco.save()
        enviar_mail_confirmacao_inscricao(self.request, inscricao.pk)
        return render(self.request, 'inscricoes/consultar_inscricao_submissao.html', {
            'inscricao': inscricao,
        })


class ConsultarInscricao(View):
    """ View que gera o formulário com passos para consultar ou alterar uma inscrição """
    template_prefix = 'inscricoes/consultar_inscricao'
    step_names = [
        'responsaveis',
        'escola',
        'transporte',
        'almoco',
        'sessoes',
        'submissao'
    ]

    def get(self, request, pk, step=0, alterar=False):
        inscricao = get_object_or_404(Inscricao, pk=pk)
        erro_permissoes = nao_tem_permissoes(request, inscricao)
        if erro_permissoes:
            return erro_permissoes
        if user_check(request, [Participante])['exists'] and datetime.now(pytz.UTC) > inscricao.diaaberto.datainscricaoatividadesfim:
            m = f"Não pode alterar a inscrição fora do período: {inscricao.diaaberto.datainscricaoatividadesinicio.strftime('%d/%m/%Y')} até {inscricao.diaaberto.datainscricaoatividadesfim.strftime('%d/%m/%Y')}"
            return render(request=request, template_name="mensagem.html", context={'m': m, 'tipo': 'error', 'continuar': 'on'})
        form = init_form(self.step_names[step], inscricao)
        context = {'alterar': alterar,
                   'pk': pk,
                   'step': step,
                   'individual': inscricao.individual,
                   'form': form,
                   }
        update_context(context, self.step_names[step], inscricao=inscricao)
        return render(request, f"{self.template_prefix}_{self.step_names[step]}.html", context)

    def post(self, request, pk, step=0, alterar=False):
        inscricao = get_object_or_404(Inscricao, pk=pk)
        erro_permissoes = nao_tem_permissoes(request, inscricao)
        if erro_permissoes:
            return erro_permissoes
        context = {}
        if alterar:
            if request.user.groups.filter(name="Participante").exists() and datetime.now(pytz.UTC) > inscricao.diaaberto.datainscricaoatividadesfim:
                m = f"Não pode alterar a inscrição fora do período: {inscricao.diaaberto.datainscricaoatividadesinicio.strftime('%d/%m/%Y')} até {inscricao.diaaberto.datainscricaoatividadesfim.strftime('%d/%m/%Y')}"
                return render(request=request, template_name="mensagem.html", context={'m': m, 'tipo': 'error', 'continuar': 'on'})
            update_post(self.step_names[step],
                        request.POST, inscricao=inscricao)
            form = init_form(self.step_names[step], inscricao, request.POST)
            inscricoessessao = inscricao.inscricaosessao_set.all()
            if self.step_names[step] == 'sessoes':
                for inscricao_sessao in inscricoessessao:
                    add_vagas_sessao(inscricao_sessao.sessao.id,
                                     inscricao_sessao.nparticipantes)
            if form.is_valid():
                save_form(request, self.step_names[step], form, inscricao)
                return HttpResponseRedirect(reverse('inscricoes:consultar-inscricao', kwargs={'pk': pk, 'step': step}))
            if self.step_names[step] == 'sessoes':
                for inscricao_sessao in inscricoessessao:
                    add_vagas_sessao(inscricao_sessao.sessao.id,
                                     -inscricao_sessao.nparticipantes)
        context.update({'alterar': alterar,
                        'pk': pk,
                        'step': step,
                        'individual': inscricao.individual,
                        'form': form,
                        })
        update_context(context, self.step_names[step], inscricao=inscricao)
        return render(request, f"{self.template_prefix}_{self.step_names[step]}.html", context)


class ConsultarInscricoes(SingleTableMixin, FilterView):
    """ View base para gerar tabelas com inscrições """
    table_class = InscricoesTable

    filterset_class = InscricaoFilter

    table_pagination = {
        'per_page': 10
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = self.get_table(**self.get_table_kwargs())
        table.fixed = True
        context[self.get_context_table_name(table)] = table
        return context

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super(ConsultarInscricoes, self).get_filterset_kwargs(
            filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"diaaberto": Diaaberto.objects.filter(
                ano__lte=datetime.now().year).order_by('-ano').first().id}
        elif "diaaberto" not in kwargs["data"]:
            kwargs["data"] = kwargs["data"].copy()
            kwargs["data"]["diaaberto"] = Diaaberto.objects.filter(
                ano__lte=datetime.now().year).order_by('-ano').first().id
        return kwargs


class MinhasInscricoes(ConsultarInscricoes):
    """ View que gera uma tabela com as inscrições do participante """
    template_name = 'inscricoes/consultar_inscricoes_participante.html'

    def dispatch(self, request, *args, **kwargs):
        user_check_var = user_check(
            request=request, user_profile=[Participante])
        if not user_check_var.get('exists'):
            return user_check_var.get('render')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Inscricao.objects.filter(participante__user_ptr=self.request.user)


class InscricoesUO(ConsultarInscricoes):
    """ View que gera uma tabela com as inscrições com pelo menos uma sessão do departamento
    do coordenador """
    template_name = 'inscricoes/consultar_inscricoes_coordenador.html'

    def dispatch(self, request, *args, **kwargs):
        user_check_var = user_check(request=request, user_profile=[
            Coordenador])
        if not user_check_var.get('exists'):
            return user_check_var.get('render')
        coordenador = Coordenador.objects.get(user_ptr=request.user)
        self.queryset = Inscricao.objects.filter(
            Exists(Inscricaosessao.objects.filter(
                inscricao=OuterRef('pk'),
                sessao__atividadeid__professoruniversitarioutilizadorid__faculdade=coordenador.faculdade
            ))
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        coordenador = Coordenador.objects.get(user_ptr=self.request.user)
        context["departamentos"] = list(
            map(lambda x: (x.id, x.nome), Departamento.objects.filter(unidadeorganicaid=coordenador.faculdade)))
        return context


class InscricoesAdmin(ConsultarInscricoes):
    """ View que gera uma tabela com as todas as inscrições """
    template_name = 'inscricoes/consultar_inscricoes_admin.html'

    def dispatch(self, request, *args, **kwargs):
        user_check_var = user_check(request=request, user_profile=[
            Administrador])
        if not user_check_var.get('exists'):
            return user_check_var.get('render')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["departamentos"] = list(
            map(lambda x: (x.id, x.nome), Departamento.objects.all()))
        return context


def ApagarInscricao(request, pk):
    """ View que apaga uma inscrição """
    inscricao = get_object_or_404(Inscricao, pk=pk)
    erro_permissoes = nao_tem_permissoes(request, inscricao)
    if erro_permissoes:
        return erro_permissoes
    inscricaosessao_set = inscricao.inscricaosessao_set.all()
    for inscricaosessao in inscricaosessao_set:
        sessaoid = inscricaosessao.sessao.id
        nparticipantes = inscricaosessao.nparticipantes
        add_vagas_sessao(sessaoid, nparticipantes)
    inscricao.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def estatisticas(request, diaabertoid=None):
    """ View que mostra as estatísticas do Dia Aberto """
    user_check_var = user_check(request=request, user_profile=[Administrador])
    if not user_check_var.get('exists'):
        return user_check_var.get('render')
    if diaabertoid is None:
        try:
            diaabertoid = Diaaberto.objects.filter(
                ano__lte=datetime.now().year).order_by('-ano').first().id
        except:
            return redirect('utilizadores:mensagem', 18)
    diaaberto = get_object_or_404(Diaaberto, id=diaabertoid)
    numdays = int((diaaberto.datadiaabertofim -
                   diaaberto.datadiaabertoinicio).days)+1
    dias = [(diaaberto.datadiaabertoinicio + timedelta(days=x)
             ).strftime("%d/%m/%Y") for x in range(numdays)]
    return render(request, 'inscricoes/estatisticas.html', {
        'diaaberto': diaaberto,
        'diasabertos': Diaaberto.objects.all(),
        'departamentos': Departamento.objects.filter(
            Exists(
                Atividade.objects.filter(
                    professoruniversitarioutilizadorid__departamento__id=OuterRef(
                        'id'),
                    diaabertoid__id=diaabertoid,
                    estado__nome="Aceite",
                )
            )
        ),
        'dias': dias,
        'meios': Inscricao.MEIO_TRANSPORTE_CHOICES,
    })

def relatorio_almoco(request, diaabertoid=None):
    """ View que mostra as estatísticas do Dia Aberto """
    user_check_var = user_check(request=request, user_profile=[Administrador])
    if not user_check_var.get('exists'):
        return user_check_var.get('render')
    if diaabertoid is None:
        try:
            diaabertoid = Diaaberto.objects.filter(
                ano__lte=datetime.now().year).order_by('-ano').first().id
        except:
            return redirect('utilizadores:mensagem', 18)
    diaaberto = get_object_or_404(Diaaberto, id=diaabertoid)
    numdays = int((diaaberto.datadiaabertofim -
                   diaaberto.datadiaabertoinicio).days) + 1
    dias = [(diaaberto.datadiaabertoinicio + timedelta(days=x)
             ).strftime("%d/%m/%Y") for x in range(numdays)]

    return render(request, 'inscricoes/escolherAnoRelatorioAlmoco.html', {
        'diaaberto': diaaberto,
        'diasabertos': Diaaberto.objects.all(),
        'ultimo_dia_aberto': Diaaberto.objects.order_by('-datadiaabertofim').first(),
        'departamentos': Departamento.objects.filter(
            Exists(
                Atividade.objects.filter(
                    professoruniversitarioutilizadorid__departamento__id=OuterRef(
                        'id'),
                    diaabertoid__id=diaabertoid,
                    estado__nome="Aceite",
                )
            )
        ),
        'dias': dias,
        'meios': Inscricao.MEIO_TRANSPORTE_CHOICES,
        'comidas': Prato.tipos,
        "incricao_comida": Inscricaoprato.npratosalunos,
        "pratos_numero": Inscricaoprato,
    })

def relatorio_almoco_excel(request, diaabertoid=None):
    inscricoes = Inscricao.objects.filter(diaaberto_id=diaabertoid)
    diaaberto = get_object_or_404(Diaaberto, id=diaabertoid)
    numdays = int((diaaberto.datadiaabertofim - diaaberto.datadiaabertoinicio).days) + 1
    dias = [(diaaberto.datadiaabertoinicio + timedelta(days=x)).strftime("%d/%m/%Y") for x in range(numdays)]
    mensagem = ''

    if not inscricoes.exists():
        try:
            return redirect('utilizadores:mensagem2', 19)
        except:
            return redirect('utilizadores:mensagem2', 19)


    try:
        dia_aberto = Diaaberto.objects.get(id=diaabertoid)
    except Diaaberto.DoesNotExist:
        return HttpResponse("Não existe Dia Aberto para o ano fornecido.", status=404)

    response = HttpResponse(content_type='text/csv')
    response.write('\ufeff'.encode('utf8'))
    response['Content-Disposition'] = f'attachment; filename="Refeições_dia_aberto{dia_aberto}.csv"'

    for dia in dias:
        totalpenha = almocampenhaDia(dia)
        totalgambelas = almocamgambelasDia(dia)
        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Informacao sobre os almocos no dia aberto',dia])
        writer.writerow(['Numero grupo', 'Escola', 'Localidade', 'Cantina Penha', 'Cantina Gambelas'])
        for inscricao in inscricoes:
            if dia == inscricao.dia.strftime("%d/%m/%Y"):
                penha = almocamPenhaInscricao(inscricao)
                gambelas = almocamGambelasInscricao(inscricao)
                writer.writerow(
                    [inscricao.id, inscricao.escola.nome, inscricao.escola.local, penha, gambelas])

        writer.writerow(['total de almocos','','',totalpenha,totalgambelas])
        writer.writerow([])
        writer.writerow([])

    return response

def pdfalmocos(request, diaabertoid=None):
    inscricoes = Inscricao.objects.filter(diaaberto_id=diaabertoid)
    user_check_var = user_check(request=request, user_profile=[Administrador])
    if not user_check_var.get('exists'):
        return user_check_var.get('render')
    if diaabertoid is None:
        try:
            diaabertoid = Diaaberto.objects.filter(
                ano__lte=datetime.now().year).order_by('-ano').first().id
        except:
            return redirect('utilizadores:mensagem', 18)
    diaaberto = get_object_or_404(Diaaberto, id=diaabertoid)

    if not inscricoes.exists():
        try:
            return redirect('utilizadores:mensagem2', 19)
        except:
            return redirect('utilizadores:mensagem2', 19)
    numdays = int((diaaberto.datadiaabertofim -
                   diaaberto.datadiaabertoinicio).days) + 1
    dias = [(diaaberto.datadiaabertoinicio + timedelta(days=x)
             ).strftime("%d/%m/%Y") for x in range(numdays)]

    context = {'diaaberto': diaaberto,
               'diasabertos': Diaaberto.objects.all(),
               'departamentos': Departamento.objects.filter(
                   Exists(
                       Atividade.objects.filter(
                           professoruniversitarioutilizadorid__departamento__id=OuterRef(
                               'id'),
                           diaabertoid__id=diaabertoid,
                           estado__nome="Aceite",
                       )
                   )
               ),'dias': dias,
        'meios': Inscricao.MEIO_TRANSPORTE_CHOICES,
        'comidas': Prato.tipos,
        "incricao_comida": Inscricaoprato.npratosalunos,
        "pratos_numero": Inscricaoprato,
        'inscricao': Inscricao.objects.filter(diaaberto__id=diaabertoid).all(),}

    return render_pdf("inscricoes/almoco_pdf.html", context, f"Almoço_dia_aberto_{diaaberto}.pdf")

def estatisticasano(request, diaabertoid=None):
    """ View que mostra as estatísticas do Dia Aberto """
    user_check_var = user_check(request=request, user_profile=[Administrador])
    if not user_check_var.get('exists'):
        return user_check_var.get('render')
    if diaabertoid is None:
        try:
            diaabertoid = Diaaberto.objects.filter(
                ano__lte=datetime.now().year).order_by('-ano').first().id
        except:
            return redirect('utilizadores:mensagem', 18)

    diaaberto = get_object_or_404(Diaaberto, id=diaabertoid)


    numdays = int((diaaberto.datadiaabertofim -
                   diaaberto.datadiaabertoinicio).days)+1
    dias = [(diaaberto.datadiaabertoinicio + timedelta(days=x)
             ).strftime("%d/%m/%Y") for x in range(numdays)]
    return render(request, 'inscricoes/ano.html', {
        'diaaberto': diaaberto,
        'diasabertos': Diaaberto.objects.all(),
        'departamentos': Departamento.objects.filter(
            Exists(
                Atividade.objects.filter(
                    professoruniversitarioutilizadorid__departamento__id=OuterRef(
                        'id'),
                    diaabertoid__id=diaabertoid,
                    estado__nome="Aceite",
                )
            )
        ),
        'dias': dias,
        'meios': Inscricao.MEIO_TRANSPORTE_CHOICES,
        'comidas': Prato.tipos,
        "incricao_comida": Inscricaoprato.npratosalunos,
        "pratos_numero": Inscricaoprato,
    })

def estatisticasAlmocos(request, diaabertoid=None):
    """ View que mostra as estatísticas do Dia Aberto """
    user_check_var = user_check(request=request, user_profile=[Administrador])
    if not user_check_var.get('exists'):
        return user_check_var.get('render')
    if diaabertoid is None:
        try:
            diaabertoid = Diaaberto.objects.filter(
                ano__lte=datetime.now().year).order_by('-ano').first().id
        except:
            return redirect('utilizadores:mensagem', 18)
    diaaberto = get_object_or_404(Diaaberto, id=diaabertoid)

    respostas = Resposta.objects.all().filter(idcodigo__inscricaoID__inscricao__diaaberto=diaaberto)

    if not respostas.exists():
        try:
            return render(request, 'inscricoes/estatisticaVaziaAlmocos.html', {
                'diasabertos': Diaaberto.objects.all(),
                'mensagem': 'Não existe respostas no dia aberto ',
                'diaaberto': diaaberto,
            })
        except:
            return redirect('utilizadores:mensagem', 18)
    numdays = int((diaaberto.datadiaabertofim -
                   diaaberto.datadiaabertoinicio).days)+1
    dias = [(diaaberto.datadiaabertoinicio + timedelta(days=x)
             ).strftime("%d/%m/%Y") for x in range(numdays)]
    return render(request, 'inscricoes/estatisticaAlmoco.html', {
        'diaaberto': diaaberto,
        'diasabertos': Diaaberto.objects.all(),
        'departamentos': Departamento.objects.filter(
            Exists(
                Atividade.objects.filter(
                    professoruniversitarioutilizadorid__departamento__id=OuterRef(
                        'id'),
                    diaabertoid__id=diaabertoid,
                    estado__nome="Aceite",
                )
            )
        ),
        'dias': dias,
        'meios': Inscricao.MEIO_TRANSPORTE_CHOICES,
        'comidas': Prato.tipos,
        "incricao_comida": Inscricaoprato.npratosalunos,
        "pratos_numero": Inscricaoprato,
        'respostas': Resposta.objects.all().filter(perguntaID=109),
        'pergunta':Pergunta.objects.get(id=109),
        'respostas2': Resposta.objects.all().filter(perguntaID=110),
        'pergunta2': Pergunta.objects.get(id=110),
        'respostas3': Resposta.objects.all().filter(perguntaID=111),
        'pergunta3': Pergunta.objects.get(id=111),
        'respostas4': Resposta.objects.all().filter(perguntaID=112),
        'pergunta4': Pergunta.objects.get(id=112),
    })

def exportarcsv(request,diaabertoid=None):
    respostas = Resposta.objects.all()
    if not respostas.exists():
        return HttpResponse("Não existem respostas de questionário para o Dia Aberto do ano fornecido.", status=404)

    if diaabertoid is None:
        try:
            diaabertoid = Diaaberto.objects.filter(
                ano__lte=datetime.now().year).order_by('-ano').first().id
        except:
            return redirect('utilizadores:mensagem', 18)
    diaaberto = get_object_or_404(Diaaberto, id=diaabertoid)

    response = HttpResponse(content_type='text/csv')
    response.write('\ufeff'.encode('utf8'))
    writer = csv.writer(response)

    writer.writerow(['Perguntas utilizadas no questionário sobre almoços'])
    writer.writerow([])
    writer.writerow(['id', 'Pergunta', 'Tema', 'Tipo de Resposta'])
    for pergunta in Pergunta.objects.all().values_list('id','pergunta', 'temaid', 'tiporespostaid'):
        if pergunta[0] == 109 or pergunta[0] == 110 or pergunta[0] == 111 or pergunta[0] == 112:
            writer.writerow(pergunta)

    writer.writerow([])
    writer.writerow(['PerguntaID', 'Resposta',])

    for resposta in Resposta.objects.all():
        if resposta.perguntaID_id in [109, 110,111, 112]:
            writer.writerow([resposta.perguntaID_id,resposta.resposta])

    response['Content-Disposition'] = f'attachment;filename="Refeições_dia_aberto{diaaberto}.csv"'

    return response


def inscricao_escolha(request):
    user_check_var = user_check(request=request, user_profile=[Administrador])
    if user_check_var.get('exists') == False:
        return user_check_var.get('render')
    context = {
    }
    return render(request, "inscricoes/escolher_inscricao.html", context)


class CriarUltimaHora(SessionWizardView):
    """ View que gera o formulário com passos para criar uma nova inscrição """
    form_list = [
        ('info', InfoForm),
        ('responsaveis', ResponsavelForm),
        ('escola', InscricaoForm),
        ('transporte', TransporteForm),
        ('almoco', AlmocoForm),
        ('sessoes', SessoesForm),
    ]

    def dispatch(self, request, *args, **kwargs):
        _user_check = user_check(request, [Administrador])
        if _user_check['exists']:
            #participante = _user_check['firstProfile']
            # participante = User.objects.get(id=45)
            diaaberto = Diaaberto.current()
            if diaaberto is None:
                return redirect('utilizadores:mensagem', 12)
            if datetime.now(pytz.UTC) < diaaberto.datainscricaoatividadesinicio or datetime.now(
                    pytz.UTC) > diaaberto.datainscricaoatividadesfim:
                m = f"Período de abertura das inscrições: {diaaberto.datainscricaoatividadesinicio.strftime('%d/%m/%Y')} até {diaaberto.datainscricaoatividadesfim.strftime('%d/%m/%Y')}"
                return render(request=request,
                              template_name="mensagem.html", context={'m': m, 'tipo': 'error', 'continuar': 'on'})
            self.instance_dict = {
                'responsaveis': Responsavel()
            }
        else:
            return _user_check['render']
        return super(CriarUltimaHora, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        update_context(context, self.steps.current, self)
        if self.steps.current != 'info':
            context.update({
                'individual': self.get_cleaned_data_for_step('info')['individual']
            })
        visited = []
        for step in self.form_list:
            cleaned_data = self.get_cleaned_data_for_step(step)
            if cleaned_data:
                visited.append(True)
            else:
                visited.append(False)
        context.update({
            'visited': visited
        })
        return context

    def get_template_names(self):
        return [f'inscricoes/inscricao_wizard_{self.steps.current}.html']

    def post(self, request, *args, **kwargs):
        # Envia a informação extra necessária para o formulário atual, após preenchê-lo.
        # Necessário para algumas validações especiais de backend, como verificar o número de alunos
        # inscritos para verificar inscritos nos almoços e nas sessões.
        current_step = request.POST.get(
            'criar_inscricao-current_step', self.steps.current)
        update_post(current_step, request.POST, self)
        go_to_step = self.request.POST.get(
            'wizard_goto_step', None)  # get the step name
        if go_to_step is not None:
            form = self.get_form(data=self.request.POST,
                                 files=self.request.FILES)

            if self.get_cleaned_data_for_step(current_step):
                if form.is_valid():
                    self.storage.set_step_data(self.steps.current,
                                               self.process_step(form))
                    self.storage.set_step_files(self.steps.current,
                                                self.process_step_files(form))
                else:
                    return self.render(form)
        return super(CriarUltimaHora, self).post(*args, **kwargs)

    def done(self, form_list, form_dict, **kwargs):
        # Guardar na Base de Dados
        responsaveis = form_dict['responsaveis'].save(commit=False)
        almoco = form_dict['almoco'].save(commit=False)
        inscricao = form_dict['escola'].save(commit=False)
        inscricao.participante = Participante.objects.filter(
            utilizador_ptr_id=33).first()
        inscricao.meio_transporte = form_dict['transporte'].cleaned_data['meio']
        if (form_dict['transporte'].cleaned_data['meio'] != 'outro'):
            inscricao.hora_chegada = form_dict['transporte'].cleaned_data['hora_chegada']
            inscricao.local_chegada = form_dict['transporte'].cleaned_data['local_chegada']
        inscricao.entrecampi = form_dict['transporte'].cleaned_data['entrecampi']
        inscricao.save()
        sessoes = form_dict['sessoes'].cleaned_data['sessoes']
        for sessaoid in sessoes:
            if sessoes[sessaoid] > 0:
                inscricao_sessao = Inscricaosessao(sessao=Sessao.objects.get(
                    pk=sessaoid), nparticipantes=sessoes[sessaoid], inscricao=inscricao)
                add_vagas_sessao(sessaoid, -sessoes[sessaoid])
                inscricao_sessao.save()
        responsaveis.inscricao = inscricao
        responsaveis.save()
        if almoco is not None:
            almoco.inscricao = inscricao
            almoco.save()
        enviar_mail_confirmacao_inscricao(self.request, inscricao.pk)
        return render(self.request, 'inscricoes/consultar_inscricao_submissao.html', {
            'inscricao': inscricao,
        })


def presençaInscricao(request,inscricao_id):
    user_check_var = user_check(request=request, user_profile=[Administrador])
    if user_check_var.get('exists') == False:
        return user_check_var.get('render')
    if inscricao_id is not None:
        inscricao = Inscricao.objects.get(id=inscricao_id)
        allowMore, allowDelete = False, False

    return render(request=request,
                  template_name='inscricoes/cancelarSessao.html', context={
                    'inscricao2': Inscricao.objects.get(id=inscricao_id),
                    'inscricaosessoes': Inscricaosessao.objects.all().filter(inscricao=inscricao_id),
                  })


def editar_presencas(request, pk):
    inscricao = get_object_or_404(Inscricao, pk=pk)

    if request.method == 'POST':
        form = EditarPresencasForm(request.POST, instance=inscricao)
        if form.is_valid():
            form.save()
            if inscricao.nalunos == form.cleaned_data['presentes']:
                return HttpResponseRedirect(reverse('inscricoes:consultar-presencas', kwargs={'pk': pk}))
            else:
                return HttpResponseRedirect(reverse('inscricoes:alterar-inscricao', kwargs={'pk': pk, 'step': 1}))
    else:
        form = EditarPresencasForm(instance=inscricao)

    return render(request, 'inscricoes/editar_presencas.html', {'form': form, 'inscricao': inscricao})

def consultar_presencas(request, pk):
    inscricao = get_object_or_404(Inscricao, pk=pk)
    inscricaosessoes = inscricao.inscricaosessao_set.all()

    return render(request, 'inscricoes/cancelarSessao.html', {
        'inscricao': inscricao,
        'inscricaosessoes': inscricaosessoes,
    })


class EditarInscricaoUltimaHoraListView(ListView):
    model = Inscricao
    template_name = "inscricoes/editar_inscricao_ultima_hora_list2.html"
    context_object_name = 'inscricoes'

    def get_queryset(self):
        return Inscricao.objects.all()


class EditarInscricaoUltimaHoraWizardView(SessionWizardView):
    """ View that generates the form with steps to edit an existing inscription """
    form_list = [
        ('info', InfoForm),
        ('responsaveis', ResponsavelForm),
        ('escola', InscricaoForm),
        ('almoco', AlmocoForm),
        ('sessoes', SessoesForm),
    ]

    def dispatch(self, request, *args, **kwargs):
        _user_check = user_check(request, [Administrador])
        if _user_check['exists']:
            diaaberto = Diaaberto.current()
            if diaaberto is None:
                return redirect('utilizadores:mensagem', 12)
            if datetime.now(pytz.UTC) < diaaberto.datainscricaoatividadesinicio or datetime.now(
                    pytz.UTC) > diaaberto.datainscricaoatividadesfim:
                m = f"Período de abertura das inscrições: {diaaberto.datainscricaoatividadesinicio.strftime('%d/%m/%Y')} até {diaaberto.datainscricaoatividadesfim.strftime('%d/%m/%Y')}"
                return render(request=request, template_name="mensagem.html",
                              context={'m': m, 'tipo': 'error', 'continuar': 'on'})

            inscricao_id = kwargs.get('inscricao_id', None)
            if not inscricao_id:
                return HttpResponse("Inscrição ID is missing.", status=400)

            try:
                inscricao = Inscricao.objects.get(id=inscricao_id)
                responsaveis = Responsavel.objects.get(inscricao=inscricao)
                almoco = Inscricaoprato.objects.get(inscricao=inscricao)
                sessoes = Inscricaosessao.objects.filter(inscricao=inscricao)
            except Inscricao.DoesNotExist:
                return HttpResponse("Inscrição não existe.", status=404)
            except Responsavel.DoesNotExist:
                return HttpResponse("Responsável não existe.", status=404)
            except Inscricaoprato.DoesNotExist:
                almoco = None  # Almoço pode não existir
            except Inscricaosessao.DoesNotExist:
                sessoes = None  # Sessões podem não existir

            self.instance_dict = {
                'responsaveis': responsaveis,
                'almoco': almoco,
                'sessoes': sessoes,
            }
        else:
            return _user_check['render']
        return super(EditarInscricaoUltimaHoraWizardView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        update_context(context, self.steps.current, self)
        if self.steps.current != 'info':
            context.update({
                'individual': self.get_cleaned_data_for_step('info')['individual']
            })
        visited = []
        for step in self.form_list:
            cleaned_data = self.get_cleaned_data_for_step(step)
            if cleaned_data:
                visited.append(True)
            else:
                visited.append(False)
        context.update({
            'visited': visited
        })
        return context

    def get_template_names(self):
        return [f'inscricoes/inscricao_UH_wizard_{self.steps.current}.html']

    def post(self, request, *args, **kwargs):
        current_step = request.POST.get('editar_inscricao-current_step', self.steps.current)
        update_post(current_step, request.POST, self)
        go_to_step = self.request.POST.get('wizard_goto_step', None)
        if go_to_step is not None:
            form = self.get_form(data=self.request.POST, files=self.request.FILES)

            if self.get_cleaned_data_for_step(current_step):
                if form.is_valid():
                    self.storage.set_step_data(self.steps.current, self.process_step(form))
                    self.storage.set_step_files(self.steps.current, self.process_step_files(form))
                else:
                    return self.render(form)
        return super(EditarInscricaoUltimaHoraWizardView, self).post(request, *args, **kwargs)

    def done(self, form_list, form_dict, **kwargs):
        inscricao_id = self.kwargs.get('inscricao_id', None)
        if not inscricao_id:
            return HttpResponse("Inscrição ID is missing.", status=400)

        try:
            inscricao = Inscricao.objects.get(id=inscricao_id)
        except Inscricao.DoesNotExist:
            return HttpResponse("Inscrição não existe.", status=404)

        responsaveis = form_dict['responsaveis'].save(commit=False)
        almoco = form_dict['almoco'].save(commit=False)
        sessoes = form_dict['sessoes'].cleaned_data['sessoes']

        responsaveis.inscricao = inscricao
        responsaveis.save()
        if almoco is not None:
            almoco.inscricao = inscricao
            almoco.save()
        for sessaoid in sessoes:
            if sessoes[sessaoid] > 0:
                inscricao_sessao, created = Inscricaosessao.objects.get_or_create(
                    inscricao=inscricao, sessao_id=sessaoid,
                    defaults={'nparticipantes': sessoes[sessaoid]}
                )
                if not created:
                    inscricao_sessao.nparticipantes = sessoes[sessaoid]
                    inscricao_sessao.save()
                add_vagas_sessao(sessaoid, -sessoes[sessaoid])
        enviar_mail_confirmacao_inscricao(self.request, inscricao.pk)
        return render(self.request, 'inscricoes/consultar_inscricaoDia_submissao.html', {
            'inscricao': inscricao,
        })


class CriarUltimaHoraDia(SessionWizardView):
    """ View que gera o formulário com passos para criar uma nova inscrição """
    form_list = [
        ('info', InfoForm),
        ('responsaveis', ResponsavelForm),
        ('escola', InscricaoForm),
        #('transporte', TransporteForm),
        ('almoco', AlmocoForm),
        ('sessoes', SessoesForm),
    ]

    def dispatch(self, request, *args, **kwargs):
        _user_check = user_check(request, [Administrador])
        if _user_check['exists']:
            #participante = _user_check['firstProfile']
            # participante = User.objects.get(id=45)
            diaaberto = Diaaberto.current()
            if diaaberto is None:
                return redirect('utilizadores:mensagem', 12)
            if datetime.now(pytz.UTC) < diaaberto.datainscricaoatividadesinicio or datetime.now(
                    pytz.UTC) > diaaberto.datainscricaoatividadesfim:
                m = f"Período de abertura das inscrições: {diaaberto.datainscricaoatividadesinicio.strftime('%d/%m/%Y')} até {diaaberto.datainscricaoatividadesfim.strftime('%d/%m/%Y')}"
                return render(request=request,
                              template_name="mensagem.html", context={'m': m, 'tipo': 'error', 'continuar': 'on'})
            self.instance_dict = {
                'responsaveis': Responsavel()
            }
        else:
            return _user_check['render']
        return super(CriarUltimaHoraDia, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        update_context(context, self.steps.current, self)
        if self.steps.current != 'info':
            context.update({
                'individual': self.get_cleaned_data_for_step('info')['individual']
            })
        visited = []
        for step in self.form_list:
            cleaned_data = self.get_cleaned_data_for_step(step)
            if cleaned_data:
                visited.append(True)
            else:
                visited.append(False)
        context.update({
            'visited': visited
        })
        return context

    def get_template_names(self):
        return [f'inscricoes/inscricaoDia_wizard_{self.steps.current}.html']

    def post(self, request, *args, **kwargs):
        # Envia a informação extra necessária para o formulário atual, após preenchê-lo.
        # Necessário para algumas validações especiais de backend, como verificar o número de alunos
        # inscritos para verificar inscritos nos almoços e nas sessões.
        current_step = request.POST.get(
            'criar_inscricao-current_step', self.steps.current)
        update_post(current_step, request.POST, self)
        go_to_step = self.request.POST.get(
            'wizard_goto_step', None)  # get the step name
        if go_to_step is not None:
            form = self.get_form(data=self.request.POST,
                                 files=self.request.FILES)

            if self.get_cleaned_data_for_step(current_step):
                if form.is_valid():
                    self.storage.set_step_data(self.steps.current,
                                               self.process_step(form))
                    self.storage.set_step_files(self.steps.current,
                                                self.process_step_files(form))
                else:
                    return self.render(form)
        return super(CriarUltimaHoraDia, self).post(*args, **kwargs)

    def done(self, form_list, form_dict, **kwargs):
        # Guardar na Base de Dados
        responsaveis = form_dict['responsaveis'].save(commit=False)
        almoco = form_dict['almoco'].save(commit=False)
        inscricao = form_dict['escola'].save(commit=False)
        inscricao.participante = Participante.objects.filter(
            utilizador_ptr_id=33).first()
        inscricao.meio_transporte = "outro"
        inscricao.entrecampi = 1
        inscricao.save()
        sessoes = form_dict['sessoes'].cleaned_data['sessoes']
        for sessaoid in sessoes:
            if sessoes[sessaoid] > 0:
                inscricao_sessao = Inscricaosessao(sessao=Sessao.objects.get(
                    pk=sessaoid), nparticipantes=sessoes[sessaoid], inscricao=inscricao)
                add_vagas_sessao(sessaoid, -sessoes[sessaoid])
                inscricao_sessao.save()
        responsaveis.inscricao = inscricao
        responsaveis.save()
        if almoco is not None:
            almoco.inscricao = inscricao
            almoco.save()
        enviar_mail_confirmacao_inscricao(self.request, inscricao.pk)
        return render(self.request, 'inscricoes/consultar_inscricaoDia_submissao.html', {
            'inscricao': inscricao,
        })

def cancelar_sessao_pagina(request, pk):
    print("ENTROUUUUUUUUU")
    inscricao = get_object_or_404(Inscricao, pk=pk)
    inscricaosessoes = inscricao.inscricaosessao_set.all()
    return render(request, 'inscricoes/cancelarSessao.html', {
        'inscricao': inscricao,
        'inscricaosessoes': inscricaosessoes,
        'pk': pk,
    })

def cancelar_sessao(request, pk, pk2):
    sessao = get_object_or_404(Inscricaosessao, id=pk)
    sessao.delete()

    return redirect(reverse('inscricoes:cancelar-sessao-pagina', args=[pk2]))
from datetime import datetime, timezone, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from atividades.models import Atividade, Sessao
from atividades.views import horariofim
from configuracao.models import Diaaberto, Horario
from questionario.models import EstadosQuest
from roteiro.filters import RoteirosFilter
from roteiro.forms import RoteiroForm
from roteiro.models import Roteiro
from roteiro.tables import RoteiroTable
from utilizadores.models import Administrador, Coordenador
from utilizadores.views import user_check
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST


# Create your views here.

class roteiroCoordenador(SingleTableMixin, FilterView):
    table_class = RoteiroTable
    template_name = 'roteiros/roteirosCoordenador.html'
    table_pagination = {
        'per_page': 5
    }
    filterset_class = RoteirosFilter

    def dispatch(self, request, *args, **kwargs):
        user_check_var = user_check(
            request=request, user_profile=[Coordenador])
        if not user_check_var.get('exists'):
            return user_check_var.get('render')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SingleTableMixin, self).get_context_data(**kwargs)
        table = self.get_table(**self.get_table_kwargs())
        table.request = self.request
        table.fixed = True
        context[self.get_context_table_name(table)] = table

        # Adicionando dados do roteiro ao contexto
        roteiros = Roteiro.objects.all()  # Recupera todos os roteiros (você pode ajustar a consulta conforme necessário)
        context['roteiros'] = roteiros

        return context


def consultarRoteiro(request,roteiro_id):
    user_check_var = user_check(request=request, user_profile=[Coordenador])
    if user_check_var.get('exists') == False:
        return user_check_var.get('render')
    if roteiro_id is not None:
        roteiro = Roteiro.objects.get(id=roteiro_id)
        allowMore, allowDelete = False, False

    return render(request=request,
                  template_name='roteiros/consultar_roteiros_tabela.html',context={
                    'roteiros': Roteiro.objects.get(id=roteiro_id),
                    'sessoes': Sessao.objects.all().filter(roteiro=roteiro_id),
                    'atividades': Atividade.objects.all().filter(roteiro=roteiro_id),
                  })

def duplicarRoteiroDia(request, id):
    print(id)
    user_check_var = user_check(request=request, user_profile=[Coordenador])
    if user_check_var.get('exists') == False:
        return user_check_var.get('render')
    userId = user_check_var.get('firstProfile').utilizador_ptr_id
    roteiro = get_object_or_404(Roteiro, id=id, coordenadorID=userId)

    # Create new activity
    new_roteiro = Roteiro.objects.get(id=id)
    new_roteiro.pk = None  # This will create a new instance instead of updating the existing one
    new_roteiro.estado = EstadosQuest.objects.get(nome="pendente")
    new_roteiro.dataalteracao = datetime.now()
    new_roteiro.diaabertoid = Diaaberto.objects.get(ano=2024)

    if request.method == 'POST':
        print(request)
        submitted_data = request.POST.copy()
        roteiro_object_form = RoteiroForm(submitted_data, instance=new_roteiro)
        if roteiro_object_form.is_valid():
            atividadesToCreate = Atividade.objects.all().filter(roteiro__id=id)
            new_roteiro = roteiro_object_form.save(commit=False)
            new_roteiro.save()
            print(new_roteiro.id)
            for atividade in atividadesToCreate:
                new_activity = atividade
                new_activity.pk = None  # This will create a new instance instead of updating the existing one
                new_activity.estado = EstadosQuest.objects.get(nome="Aceite")
                new_activity.dataalteracao = datetime.now()
                new_activity.diaabertoid = Diaaberto.objects.get(ano=2024)
                new_activity.roteiro = new_roteiro
                nome = new_activity.nome + " (Duplicado)"
                new_activity.nome = nome
                new_activity.save()


            return redirect('roteiros:duplicar-roteiro-sessao', new_roteiro.id)

    else:
        roteiro_object_form = RoteiroForm(instance=new_roteiro)
    a = Atividade.objects.all().filter(roteiro__id=id)
    print(a.count())
    for x in a:
        print(2,x.nome)
    return render(request=request,
                  template_name='roteiros/duplicarRoteiro.html',
                  context={
                      'form': roteiro_object_form,
                      "atividades": Atividade.objects.all().filter(roteiro__id=id)
                  })


def inserirsessaoDuplicarRoteiro(request, id):
    print("Cheguei aqui")
    user_check_var = user_check(request=request, user_profile=[Coordenador])
    if user_check_var.get('exists') == False: return user_check_var.get('render')
    print("Passou aqui")
    userId = user_check_var.get('firstProfile').utilizador_ptr_id
    roteiro = Roteiro.objects.filter(id=id, coordenadorID=userId)
    print("paaa")
    roteirocheck = roteiro.first()

    if roteiro.exists():
        today = datetime.now(timezone.utc)
        diaaberto = Diaaberto.objects.get(datapropostasatividadesincio__lte=today, dataporpostaatividadesfim__gte=today)
        diainicio = diaaberto.datadiaabertoinicio.date()
        diafim = diaaberto.datadiaabertofim.date()
        totaldias = diafim - diainicio + timedelta(days=1)
        dias_diaaberto = []
        for d in range(totaldias.days):
            dias_diaaberto.append(diainicio + timedelta(days=d))
        horariosindisponiveis = []
        disp = []
        roteiroid = Roteiro.objects.get(id=id)
        sessoes = Sessao.objects.all().filter(roteiro=id)
        estado_instance = EstadosQuest.objects.get(id=2)
        check = len(sessoes)
        if request.method == "POST":
            if 'new' in request.POST:
                diasessao = request.POST["diasessao"]
                print(diasessao)
                inicio = request.POST['horarioid']
                splitinicio = inicio.split(":")
                print(splitinicio)
                duracaoesperada = roteiroid.duracaoesperada
                hfim = horariofim(splitinicio, duracaoesperada)
                horario = Horario.objects.filter(inicio=request.POST['horarioid'], fim=hfim).first()
                if horario is None:
                    new_Horario = Horario(inicio=inicio, fim=hfim)
                    new_Horario.save()
                else:
                    new_Horario = horario
                new_Sessao = Sessao(vagas=Roteiro.objects.get(id=id).participantesmaximo, ninscritos=0,
                                    horarioid=Horario.objects.get(id=new_Horario.id),
                                    roteiro=Roteiro.objects.get(id=id), dia=diasessao)
                print(new_Sessao)
                if roteiroid.estado.nome != "nsub":
                    roteiroid.estado = estado_instance
                roteiroid.save()
                new_Sessao.save()
                return redirect('roteiros:duplicar-roteiro-sessao', id)
        print("É ESTE")
        return render(request=request,
                      template_name='roteiros/duplicarRoteiroSessao.html',
                      context={'horarios': "",
                               'sessions_activity': Sessao.objects.all().filter(roteiro=id),
                               'dias': dias_diaaberto,
                               'check': check, "id": id})
    else:
        return render(request=request,
                      template_name='mensagem.html',
                      context={
                          'tipo': 'error',
                          'm': 'Não tem permissões para esta ação!'
                      })

def duplicarRoteiroResumo(request, id):
    user_check_var = user_check(request=request, user_profile=[Coordenador])
    if user_check_var.get('exists') == False: return user_check_var.get('render')

    userId = user_check_var.get('firstProfile').utilizador_ptr_id
    roteiro = Roteiro.objects.filter(id=id, coordenadorID=userId)

    roteirocheck = roteiro.first()
    sessoes = Sessao.objects.filter(roteiro=roteirocheck)
    for sessao in sessoes:
        if sessao.vagas != roteirocheck.participantesmaximo:
            return render(request=request,
                          template_name='mensagem.html',
                          context={
                              'tipo': 'error',
                              'm': 'Não tem permissões para esta ação!'
                          })

    if roteiro.exists():
        roteiro = Roteiro.objects.get(id=id)
        nsub = 0
        if request.method == "POST":
            if 'anterior' in request.POST:
                return redirect('roteiros:duplicar-roteiro-sessao', id)
        sessions_activity = Sessao.objects.filter(roteiro=roteiro)
        return render(request=request,
                      template_name="roteiros/duplicarRoteiroVerResumo.html",
                      context={"roteiro": roteiro, "sessions_activity": sessions_activity, "nsub": nsub,
                               "atividades": Atividade.objects.all().filter(roteiro__id=id)
                               })
    else:
        return render(request=request,
                      template_name='mensagem.html',
                      context={
                          'tipo': 'error',
                          'm': 'Não tem permissões para esta ação!'
                      })


def eliminarSessao(request, id):
    print("ENTROU NO ELIMINAR")
    user_check_var = user_check(request=request, user_profile=[Coordenador])
    if user_check_var.get('exists') == False: return user_check_var.get('render')
    userId = user_check_var.get('firstProfile').utilizador_ptr_id
    sessoes = Sessao.objects.filter(id=id, roteiro__coordenadorID_id=userId)
    print("ENTROU NO ELIMINAR")
    if sessoes.exists():
        sessaor = sessoes.first()
        if sessaor.vagas != sessaor.roteiro.participantesmaximo:
            return render(request=request,
                          template_name='mensagem.html',
                          context={
                              'tipo': 'error',
                              'm': 'Não tem permissões para esta ação!'
                          })
        roteiroid = sessaor.roteiro.id
        sessaor.delete()
        return redirect('roteiros:duplicar-roteiro-sessao', roteiroid)
    else:
        return render(request=request,
                      template_name='mensagem.html',
                      context={
                          'tipo': 'error',
                          'm': 'Não tem permissões para esta ação!'
                      })


def eliminar_roteiro(request, id):
    roteiro = get_object_or_404(Roteiro, pk=id)
    if request.method == "POST":
        choice = request.POST.get("choice")
        if choice == "roteiro":
            roteiro.delete()
            return redirect(reverse('roteiros:roteiroCoordenador'))
        elif choice == "sessoes":
            sessoes = Sessao.objects.filter(roteiro=roteiro)
            return render(request, 'roteiros/eliminar_sessoes.html', {'roteiro': roteiro, 'sessoes': sessoes})
        elif choice == "atividades":
            atividades = Atividade.objects.filter(roteiro=roteiro)
            return render(request, 'roteiros/eliminar_atividades.html', {'roteiro': roteiro, 'atividades': atividades})

    return render(request, 'roteiros/eliminar_opcoes.html', {'roteiro': roteiro})

@require_POST
def eliminar_sessoes(request, id):
    roteiro = get_object_or_404(Roteiro, pk=id)
    sessoes_ids = request.POST.getlist('sessoes')
    Sessao.objects.filter(id__in=sessoes_ids, roteiro=roteiro).delete()
    return redirect(reverse('roteiros:consultarRoteiro', args=[id]))

@require_POST
def eliminar_atividades(request, id):
    roteiro = get_object_or_404(Roteiro, pk=id)
    atividades_ids = request.POST.getlist('atividades')
    Atividade.objects.filter(id__in=atividades_ids, roteiro=roteiro).delete()
    return redirect(reverse('roteiros:consultarRoteiro', args=[id]))
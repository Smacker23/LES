from django.urls import path
from . import views

app_name = 'questionarios'
urlpatterns = [
    path('questionarioadmin', views.consultar_questionarios.as_view(), name='consultar-questionarios-admin'),
    path('criarQuestionario', views.criarquestionario, name='criar-questionario'),
    path('criarQuestionario/<int:questionario_id>', views.criarquestionario, name='criar-questionario'),
    path('arquivarQuestionario/<int:questionario_id>', views.arquivarQuestionario, name='arquivar-questionario'),
    path('associarAnoQuestionario/<int:diaaberto_id>', views.associarAnoQuestionario, name='associar-ano-questionario'),

    path('criarPerguntas/<int:questionario_id>', views.criarperguntas, name='criar-perguntas'),

    path('consultartema', views.consultartema.as_view(), name='consultar-tema'),
    path('criarTema', views.criarTema, name='criar-tema'),

    path('consultarTipoResposta/', views.consultartiporesposta.as_view(), name='consultar-tipo-resposta'),
    path('criarTipoRespost/', views.criarTipoRespost, name='criar-tipo-resposta'),
    path('estados', views.consultar_estados.as_view(), name='consultar-estados-admin'),
    path('eliminarEstados/<int:estados_id>', views.eliminarEstado, name='eliminarEstado'),
    path('editarEstados/<int:estados_id>', views.editarEstado, name='editarEstado'),
    path('publicarQuestionario/<int:questionario_id>', views.publicarQuestionario, name='publicar-questionario'),
    path('validarQuestionario/<int:questionario_id>', views.validarQuestionario, name='validar-questionario'),

    # #ajax ----------
    path('ajax/addPergRow', views.newPergRow, name='ajaxAddPergRow'),
    # path('ajax/addResRow', views.newResRow, name='ajaxAddResRow'),

    path('estatisticas', views.estatisticasTransport, name='estatisticas'),
    path('estatisticas/<int:diaabertoid>', views.estatisticasTransport, name='estatisticasTransport'),
    # path('test', views.test, name='test'),
    # path('ajax/getInc', views.simpIncrement, name='getInc'),
    path('ajax/getRespostas', views.getRespostas, name='getRespostas'),
    path('criarEstado', views.criarEstado, name='criar-estado-admin'),

    path('responder/<int:questionario_id>/', views.responder_questionario, name='responder-questionario'),
    path('responder/<int:questionario_id>/<int:page>/', views.responder_questionario, name='responder-questionario'),
    path('editar-questionario/<int:questionario_id>/', views.editar_questionario, name='editar-questionario'),


    path('criarEscalaResposta/', views.criar_escala_resposta, name='criar-escala-resposta'),
    path('listarEscalaResposta/', views.listar_escala_resposta, name='listar-escala-resposta'),
    path('editarEscalaResposta/<int:id>/', views.editar_escala_resposta, name='editar-escala-resposta'),

    # path('questionario/<int:diaabertoid>', views.relatorio_respostas_transporte_excel, name='relatorio_respostas_transporte_excel'),
    path('exportarcsv/', views.exportarCSVTransporte, name='exportarcsvTransporte'),


    path('estatisticasAtividadeRoteiro', views.estatisticasAtividadeRoteiro, name='estatisticasAtividadeRoteiro'),
    path('estatisticasAtividadeRoteiro/<int:diaabertoid>', views.estatisticasAtividadeRoteiro, name='estatisticasAtividadeRoteiro'),
    path('ajax/getRespostasAtividadeRoteiro', views.getRespostasAtividadeRoteiro, name='getRespostasAtividadeRoteiro'),

    path('eliminarQuestionario/<int:questID>', views.eliminarQuestionario, name='eliminarQuestionario'),
    path('consultarPerguntar/<int:questID>', views.consultarPerguntas, name='consultarPerguntas'),
    path('exportarAtividadeRoteiroCSV/<int:questID>', views.atividadeRoteirocsvEstatistica, name='transportecsvEstatistica'),

]
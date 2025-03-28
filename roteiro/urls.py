from django.urls import path
from . import views

app_name = 'roteiros'
urlpatterns = [
    path('roteiros', views.roteiroCoordenador.as_view(), name='roteiroCoordenador'),
    path('consultarRoteiro/<int:roteiro_id>', views.consultarRoteiro, name='consultarRoteiro'),
    path('duplicarRoteiro/<int:id>', views.duplicarRoteiroDia,name='duplicar-roteiro'),
    path('duplicarRoteiroSessao/<int:id>', views.inserirsessaoDuplicarRoteiro,name='duplicar-roteiro-sessao'),
    path('duplicarRoteiroResumo/<int:id>',views.duplicarRoteiroResumo,name='duplicar-roteiro-resumo'),
    path('eliminarsessao/<int:id>',views.eliminarSessao,name='eliminarSessao'),
    path('eliminar/<int:id>/', views.eliminar_roteiro, name='eliminar_roteiro'),
    path('eliminar_sessoes/<int:id>/', views.eliminar_sessoes, name='eliminar_sessoes'),
    path('eliminar_atividades/<int:id>/', views.eliminar_atividades, name='eliminar_atividades'),
]

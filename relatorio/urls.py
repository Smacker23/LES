from django.urls import path
from . import views

app_name = 'relatorios'
urlpatterns = [
    path('relatorio/Transporte', views.relatorio_Transporte, name='produzirRelatorioTransporte'),
    path('relatorio/pdf/<int:diaabertoid>', views.InscricaoPDF, name='inscricao-pdf'),
    path('relatorio/csv/<int:diaabertoid>', views.transportecsv, name='inscricao-csv'),
    path('relatorio/Atividades', views.relatorio_Atividades, name='produzirRelatorioAtividades'),
    path('relatorio/atividades/pdf/<int:diaabertoid>', views.AtividadesPDF, name='atividades-pdf'),

]
from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('reserva',views.reserva,name='reserva'),
    path('anulacion',views.anulacion,name='anulacion'),
    path('signin',views.signin,name='signin'),
    path('signout',views.signout,name='signout'),
    path('admin_horas',views.admin_horas,name='admin_horas'),
    path('admin_hhcentro',views.admin_hhcentro,name='admin_hhcentro'),
    path('admin_hhmedico',views.admin_hhmedico,name='admin_hhmedico'),
    path('admin_minushhmedico',views.admin_minushhmedico,name='admin_minushhmedico'),
    path('recepcion',views.recepcion,name='recepcion'),
    path('pago_paciente',views.pago_paciente,name='pago_paciente'),
    path('espera',views.espera,name='espera'),
    path('atencion',views.atencion,name='atencion'),
]
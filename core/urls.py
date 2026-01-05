from django.urls import path
from .views import (
    home,
    tipo_pago_list, tipo_pago_create, tipo_pago_update, tipo_pago_delete,
    categoria_list, categoria_create, categoria_update, categoria_delete,
    ingreso_list, ingreso_create, ingreso_update, ingreso_delete,
    consumo_fijo_list, consumo_fijo_create, consumo_fijo_update, consumo_fijo_delete, consumo_fijo_toggle,
    consumo_diario_list, consumo_diario_create, consumo_diario_update, consumo_diario_delete,
    credito_list, credito_create, credito_delete,
    resumen_mensual,
    consumo_tarjeta_list,
    export_data_json
)
from .views.consumo_diario_mobile import consumo_diario_mobile

urlpatterns = [
    # Home
    path('', home, name='home'),
    
    # Tipo de Pago
    path('tipo-pago/', tipo_pago_list, name='tipo_pago_list'),
    path('tipo-pago/crear/', tipo_pago_create, name='tipo_pago_create'),
    path('tipo-pago/editar/<int:pk>/', tipo_pago_update, name='tipo_pago_update'),
    path('tipo-pago/eliminar/<int:pk>/', tipo_pago_delete, name='tipo_pago_delete'),
    
    # Categoría
    path('categoria/', categoria_list, name='categoria_list'),
    path('categoria/crear/', categoria_create, name='categoria_create'),
    path('categoria/editar/<int:pk>/', categoria_update, name='categoria_update'),
    path('categoria/eliminar/<int:pk>/', categoria_delete, name='categoria_delete'),
    
    # Ingreso
    path('ingreso/', ingreso_list, name='ingreso_list'),
    path('ingreso/crear/', ingreso_create, name='ingreso_create'),
    path('ingreso/editar/<int:pk>/', ingreso_update, name='ingreso_update'),
    path('ingreso/eliminar/<int:pk>/', ingreso_delete, name='ingreso_delete'),
    
    # Consumo Fijo Mensual
    path('consumo-fijo/', consumo_fijo_list, name='consumo_fijo_list'),
    path('consumo-fijo/crear/', consumo_fijo_create, name='consumo_fijo_create'),
    path('consumo-fijo/editar/<int:pk>/', consumo_fijo_update, name='consumo_fijo_update'),
    path('consumo-fijo/eliminar/<int:pk>/', consumo_fijo_delete, name='consumo_fijo_delete'),
    path('consumo-fijo/toggle/<int:pk>/', consumo_fijo_toggle, name='consumo_fijo_toggle'),
    
    # Consumo Diario
    path('consumo-diario/', consumo_diario_list, name='consumo_diario_list'),
    path('consumo-diario/crear/', consumo_diario_create, name='consumo_diario_create'),
    path('consumo-diario/editar/<int:pk>/', consumo_diario_update, name='consumo_diario_update'),
    path('consumo-diario/eliminar/<int:pk>/', consumo_diario_delete, name='consumo_diario_delete'),
    path('consumo-diario/mobile/', consumo_diario_mobile, name='consumo_diario_mobile'),
    
    path('creditos/', credito_list, name='credito_list'),
    path('creditos/crear/', credito_create, name='credito_create'),
    path('creditos/eliminar/<int:pk>/', credito_delete, name='credito_delete'),
    
    # Resumen
    path('resumen/', resumen_mensual, name='resumen_mensual'),
    path('consumo-tarjeta/', consumo_tarjeta_list, name='consumo_tarjeta_list'),
    
    # Backup
    path('backup/exportar/', export_data_json, name='export_data_json'),
]

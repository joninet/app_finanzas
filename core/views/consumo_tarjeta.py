from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from ..models import ConsumoDiario, TipoPago, Categoria

def consumo_tarjeta_list(request):
    """
    Lista todos los consumos realizados con tarjeta de crédito.
    """
    # Solo consumos que son de crédito
    consumos = ConsumoDiario.objects.filter(es_credito=True).select_related('tipo_pago', 'categoria').order_by('-fecha', '-id')
    
    # Podríamos agrupar por "compra original" para que sea más fácil de gestionar, 
    # pero por ahora mostramos una lista plana para permitir borrar cuotas individuales si se quiere.
    # O mejor: mostramos los originales y permitimos ver sus cuotas?
    # El usuario pidió "borrar o editar un gasto por si agregué mal". 
    # Si agregó mal una compra de 12 cuotas, querrá borrar las 12.
    
    context = {
        'consumos': consumos,
        'titulo': 'Gestión de Gastos con Tarjeta'
    }
    
    return render(request, 'core/consumo_tarjeta/list.html', context)

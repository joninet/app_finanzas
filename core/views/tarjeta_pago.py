from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from ..models import ConsumoDiario, TipoPago

@require_POST
def card_bulk_payment(request, tipo_pago_id):
    """
    Marca todos los consumos con tarjeta del mes y año especificados como pagados.
    """
    mes = request.POST.get('mes')
    año = request.POST.get('año')
    
    if not mes or not año:
        messages.error(request, "Mes o año no especificados para el pago.")
        return redirect('resumen_mensual')
    
    tipo_pago = get_object_or_404(TipoPago, id=tipo_pago_id)
    
    # Buscar consumos de esa tarjeta en ese mes/año que NO estén pagados
    consumos = ConsumoDiario.objects.filter(
        tipo_pago=tipo_pago,
        fecha__month=mes,
        fecha__year=año,
        es_credito=True,
        pagado=False
    )
    
    count = consumos.count()
    if count > 0:
        consumos.update(pagado=True, fecha_pago=timezone.now().date())
        messages.success(request, f"Se marcaron {count} items como pagados para {tipo_pago.nombre}.")
    else:
        # Si ya estaban pagados, quizás el usuario quiere revertir? 
        # Pero el pedido es "tildar una opción de pagado".
        # Vamos a implementar solo el marcado como pagado por ahora.
        messages.info(request, f"No hay consumos pendientes para {tipo_pago.nombre} en este período.")
        
    return redirect(f"{request.POST.get('next', '/resumen/')}?mes={año}-{int(mes):02d}")

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from ..models import ConsumoFijoMensual, ConsumoDiario

@require_POST
def update_comment(request):
    """
    Actualiza el comentario de un consumo (fijo o diario).
    """
    model_type = request.POST.get('model_type')
    item_id = request.POST.get('item_id')
    comentario = request.POST.get('comentario', '')

    if model_type == 'fijo':
        item = get_object_or_404(ConsumoFijoMensual, id=item_id)
    elif model_type == 'diario':
        item = get_object_or_404(ConsumoDiario, id=item_id)
    else:
        return JsonResponse({'status': 'error', 'message': 'Tipo de modelo inválido'}, status=400)

    item.comentario = comentario
    item.save(update_fields=['comentario'])

    return JsonResponse({'status': 'success', 'comentario': item.comentario})

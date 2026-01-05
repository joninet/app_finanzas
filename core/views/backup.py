import json
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from ..models import TipoPago, Categoria, Ingreso, ConsumoFijoMensual, ConsumoDiario

def export_data_json(request):
    """
    Exporta todos los datos del usuario a un archivo JSON.
    """
    # Obtenemos todos los modelos que queremos respaldar
    tipos_pago = TipoPago.objects.all()
    categorias = Categoria.objects.all()
    ingresos = Ingreso.objects.all()
    consumos_fijos = ConsumoFijoMensual.objects.all()
    consumos_diarios = ConsumoDiario.objects.all()
    
    # Serializamos los datos
    data = []
    data.extend(json.loads(serializers.serialize('json', tipos_pago)))
    data.extend(json.loads(serializers.serialize('json', categorias)))
    data.extend(json.loads(serializers.serialize('json', ingresos)))
    data.extend(json.loads(serializers.serialize('json', consumos_fijos)))
    data.extend(json.loads(serializers.serialize('json', consumos_diarios)))
    
    # Preparamos la respuesta como archivo de descarga
    response = HttpResponse(
        json.dumps(data, indent=4, ensure_ascii=False),
        content_type='application/json'
    )
    response['Content-Disposition'] = 'attachment; filename="backup_finanzas.json"'
    
    return response

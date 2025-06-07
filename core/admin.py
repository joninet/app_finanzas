from django.contrib import admin
from .models import TipoPago, Categoria, Ingreso, ConsumoFijoMensual, ConsumoDiario

@admin.register(TipoPago)
class TipoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'es_tarjeta_credito', 'fecha_creacion')
    list_filter = ('es_tarjeta_credito',)
    search_fields = ('nombre', 'descripcion')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')

@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ('tipo_pago', 'monto', 'fecha', 'fecha_creacion')
    list_filter = ('tipo_pago', 'fecha')
    search_fields = ('descripcion',)
    date_hierarchy = 'fecha'

@admin.register(ConsumoFijoMensual)
class ConsumoFijoMensualAdmin(admin.ModelAdmin):
    list_display = ('categoria', 'tipo_pago', 'monto', 'mes', 'año', 'pagado')
    list_filter = ('categoria', 'tipo_pago', 'mes', 'año', 'pagado')
    search_fields = ('descripcion',)

@admin.register(ConsumoDiario)
class ConsumoDiarioAdmin(admin.ModelAdmin):
    list_display = ('categoria', 'tipo_pago', 'monto', 'fecha', 'es_credito', 'cuotas')
    list_filter = ('categoria', 'tipo_pago', 'fecha', 'es_credito')
    search_fields = ('descripcion',)
    date_hierarchy = 'fecha'

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class TipoPago(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    es_tarjeta_credito = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Tipo de Pago"
        verbose_name_plural = "Tipos de Pago"

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

class Ingreso(models.Model):
    tipo_pago = models.ForeignKey(TipoPago, on_delete=models.CASCADE, related_name='ingresos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(default=timezone.now)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.tipo_pago} - {self.monto}"
    
    class Meta:
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"

class ConsumoFijoMensual(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='consumos_fijos')
    tipo_pago = models.ForeignKey(TipoPago, on_delete=models.CASCADE, related_name='consumos_fijos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    mes = models.IntegerField(choices=[(i, i) for i in range(1, 13)])
    año = models.IntegerField()
    descripcion = models.TextField(blank=True, null=True)
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.categoria} - {self.monto} - {self.mes}/{self.año}"
    
    class Meta:
        verbose_name = "Consumo Fijo Mensual"
        verbose_name_plural = "Consumos Fijos Mensuales"
        unique_together = ('categoria', 'mes', 'año')

class ConsumoDiario(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='consumos_diarios')
    tipo_pago = models.ForeignKey(TipoPago, on_delete=models.CASCADE, related_name='consumos_diarios')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(default=timezone.now)
    descripcion = models.TextField(blank=True, null=True)
    es_credito = models.BooleanField(default=False)
    cuotas = models.IntegerField(default=1)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.categoria} - {self.monto} - {self.fecha}"
    
    class Meta:
        verbose_name = "Consumo Diario"
        verbose_name_plural = "Consumos Diarios"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Si es un pago con tarjeta de crédito en cuotas, crear consumos fijos mensuales
        # Comenzando desde el mes siguiente al de la fecha del consumo
        if self.es_credito and self.cuotas > 1 and self.tipo_pago.es_tarjeta_credito:
            monto_por_cuota = self.monto / self.cuotas
            fecha_actual = self.fecha
            
            # Para tarjetas de crédito, comenzamos en el mes siguiente
            for i in range(self.cuotas):
                # Sumamos 1 mes adicional para que la primera cuota sea el mes siguiente
                mes_cuota = ((fecha_actual.month + i) % 12) + 1  # +i en lugar de +(i-1)
                año_cuota = fecha_actual.year + ((fecha_actual.month + i) // 12)  # Sin -1
                descripcion_cuota = f"Cuota {i+1}/{self.cuotas} - {self.descripcion or 'Consumo con tarjeta'}"
                
                try:
                    # Intentar obtener un consumo fijo existente
                    try:
                        consumo = ConsumoFijoMensual.objects.get(
                            categoria=self.categoria,
                            tipo_pago=self.tipo_pago,
                            mes=mes_cuota,
                            año=año_cuota
                        )
                        # Si existe, actualizar el monto y la descripción
                        consumo.monto += monto_por_cuota
                        consumo.descripcion = (consumo.descripcion or '') + f" + {descripcion_cuota}"
                        consumo.save()
                    except ConsumoFijoMensual.DoesNotExist:
                        # Si no existe, crear uno nuevo
                        ConsumoFijoMensual.objects.create(
                            categoria=self.categoria,
                            tipo_pago=self.tipo_pago,
                            mes=mes_cuota,
                            año=año_cuota,
                            monto=monto_por_cuota,
                            descripcion=descripcion_cuota
                        )
                except Exception as e:
                    # Registrar el error pero no interrumpir la creación del consumo diario
                    print(f"Error al crear consumo fijo para cuota {i+1}: {str(e)}")
                    # Se podría agregar un log más formal aquí

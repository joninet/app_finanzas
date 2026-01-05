from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import date
import calendar

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
    icono = models.CharField(max_length=50, default='fa-solid fa-tag', help_text='Clase de Font Awesome para el icono')
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
    tipo_pago = models.ForeignKey(TipoPago, on_delete=models.CASCADE, related_name='consumos_fijos', null=True, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    mes = models.IntegerField(choices=[(i, i) for i in range(1, 13)])
    año = models.IntegerField()
    descripcion = models.TextField(blank=True, null=True)
    comentario = models.TextField(blank=True, null=True, help_text="Comentario específico para este mes")
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(null=True, blank=True)
    
    # Optional: Link back to the Credito that generated this expense
    credito_origen = models.ForeignKey('Credito', on_delete=models.CASCADE, related_name='cuotas_generadas', null=True, blank=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.categoria} - {self.monto} - {self.mes}/{self.año}"
    
    class Meta:
        verbose_name = "Consumo Fijo Mensual"
        verbose_name_plural = "Consumos Fijos Mensuales"
        # unique_together = ('categoria', 'mes', 'año')

class ConsumoDiario(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    tipo_pago = models.ForeignKey(TipoPago, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    comentario = models.TextField(blank=True, null=True, help_text="Comentario específico para este mes")
    es_credito = models.BooleanField(default=False)
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(null=True, blank=True)
    cuotas = models.IntegerField(default=1)
    cuota_numero = models.IntegerField(default=1)
    cuota_total = models.IntegerField(default=1)
    consumo_original = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='cuotas_relacionadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.categoria} - {self.monto} - {self.fecha}"
    
    class Meta:
        verbose_name = "Consumo Diario"
        verbose_name_plural = "Consumos Diarios"
    
    def save(self, *args, **kwargs):
        # Primero guardamos el objeto
        is_new = self.pk is None  # Verificar si es un objeto nuevo o una edición
        created_from_credit_card = getattr(self, '_created_from_credit_card', False)
        
        super().save(*args, **kwargs)
        
        # Si es un pago con tarjeta de crédito en cuotas, crear consumos diarios para los meses siguientes
        # Solo procesamos cuando es nuevo Y no es una cuota creada por otro consumo
        if is_new and self.es_credito and self.cuotas > 1 and self.tipo_pago and self.tipo_pago.es_tarjeta_credito and not created_from_credit_card:
            try:
                # El record actual (self) es el TOTAL de la compra. 
                # Queremos que este RECORD sea la CUOTA 1.
                total_compra = float(self.monto)
                monto_por_cuota = round(total_compra / int(self.cuotas), 2)
                
                # Actualizar el registro actual para que sea la Cuota 1
                self.monto = monto_por_cuota
                self.cuota_numero = 1
                self.cuota_total = self.cuotas
                
                # Asegurar que fecha_actual sea un objeto date válido
                from datetime import date
                if isinstance(self.fecha, str):
                    try:
                        partes = self.fecha.split('-')
                        fecha_compra = date(int(partes[0]), int(partes[1]), int(partes[2]))
                    except Exception:
                        fecha_compra = date.today()
                else:
                    fecha_compra = self.fecha
                
                # Actualizar descripción del registro actual si no tiene el formato de cuota
                desc_base = self.descripcion if self.descripcion else 'Consumo con tarjeta'
                if "Cuota" not in desc_base:
                    self.descripcion = f"Cuota 1/{self.cuotas} - {desc_base} (Compra: {fecha_compra.strftime('%d/%m/%Y')})"
                
                # Guardar los cambios en el registro actual (el super().save ja se llamó, pero queremos persistir estos cambios de cuota)
                super().save(update_fields=['monto', 'cuota_numero', 'cuota_total', 'descripcion'])
                
                # Para tarjetas de crédito, generamos las cuotas RESTANTES (de la 2 en adelante)
                for num_cuota in range(2, self.cuotas + 1):
                    # Calcular la fecha exacta para el mes/año de la cuota
                    # num_cuota-1 meses después de la compra (Cuota 2 es 1 mes después)
                    meses_a_sumar = num_cuota - 1
                    mes_cuota = ((fecha_compra.month + meses_a_sumar - 1) % 12) + 1
                    año_cuota = fecha_compra.year + ((fecha_compra.month + meses_a_sumar - 1) // 12)
                    
                    try:
                        fecha_cuota = date(año_cuota, mes_cuota, min(fecha_compra.day, 28)) # Simplificado para evitar errores de fin de mes
                        if fecha_compra.day > 28:
                             # Re-intentar con lógica de fin de mes si era > 28
                             import calendar
                             ultimo_dia = calendar.monthrange(año_cuota, mes_cuota)[1]
                             fecha_cuota = date(año_cuota, mes_cuota, min(fecha_compra.day, ultimo_dia))
                    except ValueError:
                        fecha_cuota = date(año_cuota, mes_cuota, 28)
                    
                    descripcion_cuota = f"Cuota {num_cuota}/{self.cuotas} - {desc_base} (Compra: {fecha_compra.strftime('%d/%m/%Y')})"
                    
                    from django.db import transaction
                    try:
                        with transaction.atomic():
                            nuevo_consumo = ConsumoDiario(
                                categoria=self.categoria,
                                tipo_pago=self.tipo_pago,
                                monto=monto_por_cuota,
                                fecha=fecha_cuota,
                                descripcion=descripcion_cuota,
                                es_credito=True,
                                cuotas=1,          # Para evitar recursividad
                                cuota_numero=num_cuota,
                                cuota_total=self.cuotas,
                                consumo_original=self,
                                comentario=self.comentario
                            )
                            setattr(nuevo_consumo, '_created_from_credit_card', True)
                            nuevo_consumo.save()
                    except Exception:
                        pass
                    except Exception:
                        # Continuar con las demás cuotas si hay error en una
                        pass
            except Exception:
                # El consumo diario ya se guardó, así que no afecta su creación
                pass

class Credito(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    monto_cuota = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_cuotas = models.IntegerField()
    fecha_inicio = models.DateField(default=timezone.now, help_text="Fecha de la primera cuota")
    
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='creditos')
    tipo_pago = models.ForeignKey(TipoPago, on_delete=models.SET_NULL, related_name='creditos', null=True, blank=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} ({self.cantidad_cuotas} cuotas)"

    class Meta:
        verbose_name = "Crédito"
        verbose_name_plural = "Créditos"

@receiver(post_save, sender=Credito)
def generar_cuotas_credito(sender, instance, created, **kwargs):
    """
    Genera automáticamente los consumos fijos mensuales para un crédito nuevo.
    """
    if created:
        fecha_actual = instance.fecha_inicio
        
        # Asegurar que fecha_actual es un objeto date
        if isinstance(fecha_actual, str):
            from datetime import datetime
            try:
                fecha_actual = datetime.strptime(fecha_actual, '%Y-%m-%d').date()
            except ValueError:
                # Fallback to today if parsing fails
                fecha_actual = timezone.now().date()
                
        mes_inicio = fecha_actual.month
        año_inicio = fecha_actual.year

        for i in range(instance.cantidad_cuotas):
            # Calcular mes y año
            mes_calculado = ((mes_inicio + i - 1) % 12) + 1
            año_calculado = año_inicio + ((mes_inicio + i - 1) // 12)
            
            # Formatear descripción
            descripcion_cuota = f"Cuota {i+1}/{instance.cantidad_cuotas} - {instance.nombre}"
            
            # Crear ConsumoFijoMensual
            ConsumoFijoMensual.objects.create(
                categoria=instance.categoria,
                tipo_pago=instance.tipo_pago,
                monto=instance.monto_cuota,
                mes=mes_calculado,
                año=año_calculado,
                descripcion=descripcion_cuota,
                credito_origen=instance,
                pagado=False
            )

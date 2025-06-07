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
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    tipo_pago = models.ForeignKey(TipoPago, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255, blank=True, null=True)
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
        # Primero guardamos el objeto
        is_new = self.pk is None  # Verificar si es un objeto nuevo o una edición
        created_from_credit_card = getattr(self, '_created_from_credit_card', False)
        
        super().save(*args, **kwargs)
        
        # Si es un pago con tarjeta de crédito en cuotas, crear consumos diarios para los meses siguientes
        # Solo procesamos cuando es nuevo Y no es una cuota creada por otro consumo
        if is_new and self.es_credito and self.cuotas > 1 and self.tipo_pago and self.tipo_pago.es_tarjeta_credito and not created_from_credit_card:
            try:
                # Redondear a 2 decimales para evitar errores de precisión
                monto_por_cuota = round(float(self.monto) / int(self.cuotas), 2)
                
                # Asegurar que fecha_actual sea un objeto date válido
                from datetime import date
                if isinstance(self.fecha, str):
                    # Si es string, convertir a date
                    try:
                        partes = self.fecha.split('-')
                        fecha_actual = date(int(partes[0]), int(partes[1]), int(partes[2]))
                    except Exception:
                        fecha_actual = date.today()
                else:
                    # Debería ser un objeto date
                    fecha_actual = self.fecha
                
                # Asegurar que la descripción tenga un valor por defecto
                desc_base = self.descripcion if self.descripcion else 'Consumo con tarjeta'
                
                # Para tarjetas de crédito, generamos solo cuotas-1 consumos adicionales
                # Empezamos desde la segunda cuota (1) ya que la primera es el consumo original
                for i in range(1, self.cuotas):
                    # Calcular la fecha exacta para el mes/año de la cuota
                    mes_cuota = ((fecha_actual.month + i) % 12) or 12  # Para que diciembre sea 12, no 0
                    año_cuota = fecha_actual.year + ((fecha_actual.month + i - 1) // 12)
                    
                    # Crear una fecha para el mismo día del mes siguiente
                    try:
                        fecha_cuota = date(año_cuota, mes_cuota, fecha_actual.day)
                    except ValueError:
                        # Si el día no existe en el mes (ej. 31 de febrero), usar el último día
                        if mes_cuota == 2:
                            # Febrero
                            if (año_cuota % 4 == 0 and año_cuota % 100 != 0) or año_cuota % 400 == 0:
                                fecha_cuota = date(año_cuota, mes_cuota, 29)  # Año bisiesto
                            else:
                                fecha_cuota = date(año_cuota, mes_cuota, 28)
                        elif mes_cuota in [4, 6, 9, 11]:  # Meses con 30 días
                            fecha_cuota = date(año_cuota, mes_cuota, 30)
                        else:  # Meses con 31 días
                            fecha_cuota = date(año_cuota, mes_cuota, 31)
                    
                    descripcion_cuota = f"Cuota {i+1}/{self.cuotas} - {desc_base}"
                    
                    # Crear un nuevo consumo diario para esta cuota
                    from django.db import transaction
                    try:
                        with transaction.atomic():
                            # Usamos transaction.atomic para evitar llamadas recursivas al save()
                            nuevo_consumo = ConsumoDiario(
                                categoria=self.categoria,
                                tipo_pago=self.tipo_pago,
                                monto=monto_por_cuota,
                                fecha=fecha_cuota,
                                descripcion=descripcion_cuota,
                                es_credito=False,  # No es crédito para evitar recursividad
                                cuotas=1           # No tiene cuotas para evitar recursividad
                            )
                            # Marcar que este consumo fue creado por otro consumo con tarjeta
                            # para evitar recursividad
                            setattr(nuevo_consumo, '_created_from_credit_card', True)
                            nuevo_consumo.save()
                    except Exception:
                        # Continuar con las demás cuotas si hay error en una
                        pass
            except Exception:
                # El consumo diario ya se guardó, así que no afecta su creación
                pass

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
    es_cuota = models.BooleanField(default=False)  # Para marcar si es una cuota generada por otro consumo
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
        super().save(*args, **kwargs)
        
        # Si es un pago con tarjeta de crédito en cuotas, crear consumos diarios para los meses siguientes
        # Comenzando desde el mes siguiente al de la fecha del consumo
        if is_new and self.es_credito and self.cuotas > 1 and self.tipo_pago and self.tipo_pago.es_tarjeta_credito:
            try:
                # Redondear a 2 decimales para evitar errores de precisión
                monto_por_cuota = round(float(self.monto) / int(self.cuotas), 2)
                fecha_actual = self.fecha
                
                # Asegurar que la descripción tenga un valor por defecto
                desc_base = self.descripcion if self.descripcion else 'Consumo con tarjeta'
                
                # Para tarjetas de crédito, comenzamos en el mes siguiente
                for i in range(self.cuotas):
                    try:
                        # Sumamos 1 mes adicional para que la primera cuota sea el mes siguiente
                        # Calcular la fecha exacta para el mes/año de la cuota
                        mes_cuota = ((fecha_actual.month + i) % 12) + 1  # +i en lugar de +(i-1)
                        año_cuota = fecha_actual.year + ((fecha_actual.month + i) // 12)  # Sin -1
                        
                        # Crear una fecha para el mismo día del mes siguiente
                        from datetime import date
                        try:
                            fecha_cuota = date(año_cuota, mes_cuota, fecha_actual.day)
                        except ValueError:
                            # Si el día no existe en el mes (ej. 31 de febrero), usar el último día del mes
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
                        with transaction.atomic():
                            # Usamos transaction.atomic para evitar llamadas recursivas al save()
                            nuevo_consumo = ConsumoDiario(
                                categoria=self.categoria,
                                tipo_pago=self.tipo_pago,
                                monto=monto_por_cuota,
                                fecha=fecha_cuota,
                                descripcion=descripcion_cuota,
                                es_credito=False,  # No es crédito para evitar recursividad
                                cuotas=1,          # No tiene cuotas para evitar recursividad
                                es_cuota=True      # Marca que es una cuota de otro consumo
                            )
                            # Guardar sin llamar al método save() para evitar recursividad
                            super(ConsumoDiario, nuevo_consumo).save()
                            
                    except Exception as e:
                        # Capturar errores por cuota pero continuar con las demás
                        print(f"Error procesando cuota {i+1}: {str(e)}")
            except Exception as e:
                # Capturar cualquier error en el proceso global de cuotas
                print(f"Error general procesando cuotas: {str(e)}")
                # El consumo diario ya se guardó, así que no afecta su creación

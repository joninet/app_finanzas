import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finanzas_personales.settings')
django.setup()

from core.models import ConsumoDiario
from django.db import transaction

def fix_installments():
    print("Starting data correction for installments...")
    
    # Identify parent records
    parents = ConsumoDiario.objects.filter(
        es_credito=True, 
        cuotas__gt=1, 
        consumo_original__isnull=True
    )
    
    print(f"Found {parents.count()} parent records to inspect.")
    
    with transaction.atomic():
        for parent in parents:
            children = ConsumoDiario.objects.filter(consumo_original=parent).order_by('fecha')
            num_children = children.count()
            actual_total = num_children + 1
            
            # If it's already exactly as we want, skip
            if parent.cuota_total == actual_total and all(c.cuota_total == actual_total for c in children):
                print(f"  Parent {parent.id} already fixed at {actual_total} total cuotas. Skipping.")
                continue

            print(f"Fixing Parent ID {parent.id}: {parent.descripcion}. New total cuotas -> {actual_total}")
            
            # Determine correct installment amount
            # If the parent was originally the total (cuota_total=1), divide it.
            # If we already divided it (cuota_total > 1), don't divide again.
            if parent.cuota_total == 1:
                # This was the first fix run for this record
                num_original_cuotas = parent.cuotas
                monto_cuota = round(float(parent.monto) / num_original_cuotas, 2)
                parent.monto = monto_cuota
            else:
                # Already divided, just use current amount
                monto_cuota = float(parent.monto)
            
            # 1. Update Parent
            parent.cuota_numero = 1
            parent.cuota_total = actual_total
            if not parent.descripcion or "Cuota" not in parent.descripcion:
                parent.descripcion = f"Cuota 1/{actual_total} - {parent.descripcion or 'Consumo con tarjeta'} (Compra: {parent.fecha.strftime('%d/%m/%Y')})"
            else:
                import re
                parent.descripcion = re.sub(r"Cuota \d+/\d+", f"Cuota 1/{actual_total}", parent.descripcion)
            
            setattr(parent, '_created_from_credit_card', True)
            parent.save()
            
            # 2. Update Children
            for i, child in enumerate(children):
                new_num = i + 2
                child.cuota_numero = new_num
                child.cuota_total = actual_total
                child.monto = monto_cuota # Ensure all have same amount
                if child.descripcion:
                    import re
                    child.descripcion = re.sub(r"Cuota \d+/\d+", f"Cuota {new_num}/{actual_total}", child.descripcion)
                
                setattr(child, '_created_from_credit_card', True)
                child.save()
                print(f"  -> Updated Child ID {child.id} to {new_num}/{actual_total}")

    print("Correction complete.")

if __name__ == "__main__":
    fix_installments()

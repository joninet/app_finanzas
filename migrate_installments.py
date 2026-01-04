import os
import django
import re

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finanzas_personales.settings')
django.setup()

from core.models import ConsumoDiario

def run_migration():
    print("Starting data migration for ConsumoDiario installments...")
    
    # Filter potentially relevant items
    # Check for items with 'Cuota X/Y' in description
    items = ConsumoDiario.objects.filter(descripcion__contains="Cuota")
    
    updated_count = 0
    
    regex = r"Cuota (\d+)/(\d+)"
    
    for item in items:
        match = re.search(regex, item.descripcion)
        if match:
            cuota_num = int(match.group(1))
            cuota_tot = int(match.group(2))
            
            # Update fields
            item.cuota_numero = cuota_num
            item.cuota_total = cuota_tot
            
            # Also fix es_credito = True if it was False (old logic)
            # Old logic: es_credito=False for generated installments
            if not item.es_credito:
                item.es_credito = True
                
                # IMPORTANT: If we save with es_credito=True and cuotas=1, 
                # our new save() logic shouldn't recurse because cuotas > 1 is checked.
                # But let's be safe and set _created_from_credit_card = True anyway to avoid side effects
                setattr(item, '_created_from_credit_card', True)
            
            item.save()
            updated_count += 1
            print(f"Updated: {item.descripcion} -> {cuota_num}/{cuota_tot}, es_credito={item.es_credito}")
            
    print(f"Migration complete. Updated {updated_count} items.")

if __name__ == "__main__":
    run_migration()

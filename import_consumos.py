import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_finanzas.settings')
django.setup()

from core.models import ConsumoFijoMensual, Categoria, TipoPago
from django.utils import timezone

def run_import():
    # User data
    raw_data = """
Go cuotas Joni
	20000	20000	20000	20000	20000							
	17500	17500	17500	17500	17500							
	7500	7500	7500	7500	7500							
	5850	5850	5850	5850	5850							
	38150	38150										
	18350	18350	18350									
	9000	9000	9000	9000								
	6300											
	12830	12830	12830	12830	12830							
	32350	32350										
	15600	15600	15600	15600	15600							
Go Cuotas Fher
	28592	28592	28592	28592	28592	28592						
	23554	23554	23554	23554	23554	23554						
	68942	68942	68942	68942	68942	68942	68942	68942	68942			
Credito Hipo (12 cuotas)
	72300	72300	72300									
Credito Hipo (36 cuotas)
	218000	218000	218000	218000	218000	218000	218000	218000	218000	218000	218000	218000
Banco de la gente 1
	23000	23000	23000	23000	23000	23000	23000	23000	23000	23000	23000	23000
Banco de la gente 2
	23000	23000	23000	23000	23000	23000	23000	23000	23000	23000	23000	23000
Mercadopago Joni
	41350	41350										
	11100											
	6175	6175	6175									
	2650	2650	2650	2650	2650	2650	2650	2650	2650			
	50580	50580	50580	50580								
	15100	15100	15100	15100								
	4050											
	2080	2080	2080	2080	2080	2080	2080					
	198											
	263	263										
	41740	41740										
	54371	54371	54371	54371	54371	54371	54371	54371	54371	54371	54371	
	3985	3985	3985	3985	3985	3985	3985	3985	3985	3985	3985	
	379	379	379	379	379	379	379	379	379	379	379	
"""
    
    # 1. Get or Create "Otros" category
    categoria, created = Categoria.objects.get_or_create(
        nombre="Otros", 
        defaults={'descripcion': 'Categoría general para gastos importados', 'icono': 'fa-solid fa-tag'}
    )
    if created:
        print(f"Created category: {categoria.nombre}")
    else:
        print(f"Using existing category: {categoria.nombre}")

    # 2. Parse data
    lines = raw_data.strip().split('\n')
    current_header = "General Import"
    current_year = 2026 # Assuming current budget year
    
    count = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip header lines or subtotals if they appear in text
        if "enero" in line.lower() or "subtotal" in line.lower() or "total" in line.lower():
            continue
            
        # Check if line is a header (no digits, or mostly text)
        # Simple heuristic: if it doesn't contain tabs with numbers, it's a header
        # But wait, "Credito Hipo (12 cuotas)" has spaces.
        # Check if it has the tab-separated structure of values
        parts = line.split('\t')
        # Filter out empty strings from parts
        parts = [p.strip() for p in parts if p.strip()]
        
        # Assume valid data row has numbers
        is_data_row = False
        if parts:
            try:
                float(parts[0].replace('.', '').replace(',', '.'))
                is_data_row = True
            except ValueError:
                is_data_row = False
        
        if not is_data_row:
            current_header = line
            print(f"Processing group: {current_header}")
            # Try to match a TipoPago or create it if needed?
            # User said "el consumo fijo quiero que no sea obligatorio el tipo de pago"
            # So we will leave tipo_pago=None and put header in description
            continue
            
        # Process data row
        # Iterate over parts - each assumes to be a month starting from Jan
        # Note: The visual text has empty tabs. split('\t') keeps empty strings?
        # Let's re-read the raw_data handling.
        # Python strip() on line removes leading/trailing tabs.
        # But internal tabs matter.
        # We need the alignment. "20000" at start is Jan.
        # If there are empty slots at start, it might change.
        # But in the provided text, numbers look left-aligned under months.
        # "Go cuotas Joni" block -> 20000 is under Enero.
        # So usually it's [Value, Value, ...] starting from Jan.
        
        # Wait, Python split() logic:
        # If I copy-pasted tabs, they might be spaces.
        # Let's assume sequential month filling for non-empty values.
        # Looking at "Mercadopago Joni": "41350 41350" -> Jan, Feb.
        # "11100" -> Jan.
        # "2650...2650" -> Jan to ...
        # Yes, it looks like "Start from Jan until finished".
        
        for i, val in enumerate(parts):
            if not val:
                continue
            try:
                monto = float(val.replace('.', '').replace(',', '.'))
                mes = i + 1
                if mes > 12:
                    break
                
                # Check duplicates?
                # We removed unique constraint, so just add.
                ConsumoFijoMensual.objects.create(
                    categoria=categoria,
                    tipo_pago=None, # As requested
                    monto=monto,
                    mes=mes,
                    año=current_year,
                    descripcion=f"{current_header}",
                    pagado=False
                )
                count += 1
            except ValueError:
                pass

    print(f"Imported {count} items.")

if __name__ == "__main__":
    run_import()

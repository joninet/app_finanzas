// Scripts para la aplicación de finanzas personales

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers de Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Funcionalidad para seleccionar todos los checkboxes
    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.item-checkbox');
            checkboxes.forEach(function(checkbox) {
                checkbox.checked = selectAllCheckbox.checked;
            });
        });
    }
    
    // Mostrar/ocultar campos de cuotas cuando se selecciona tarjeta de crédito
    const creditCheckbox = document.getElementById('es_credito');
    if (creditCheckbox) {
        const cuotasContainer = document.getElementById('cuotas_container');
        
        // Función para mostrar/ocultar el contenedor de cuotas
        const toggleCuotas = function() {
            if (cuotasContainer) {
                if (creditCheckbox.checked) {
                    cuotasContainer.classList.remove('d-none');
                } else {
                    cuotasContainer.classList.add('d-none');
                }
            }
        };
        
        // Ejecutar al cargar la página
        toggleCuotas();
        
        // Ejecutar cuando cambie el estado del checkbox
        creditCheckbox.addEventListener('change', toggleCuotas);
    }
    
    // Manejar formulario de fecha para filtros
    const dateForm = document.getElementById('date-filter-form');
    if (dateForm) {
        const dateInputs = dateForm.querySelectorAll('input[type="date"]');
        dateInputs.forEach(function(input) {
            input.addEventListener('change', function() {
                dateForm.submit();
            });
        });
    }
    
    // Mostrar/ocultar campos de fecha de pago
    const pagadoCheckbox = document.getElementById('pagado');
    if (pagadoCheckbox) {
        const fechaPagoContainer = document.getElementById('fecha_pago_container');
        
        // Función para mostrar/ocultar el contenedor de fecha de pago
        const toggleFechaPago = function() {
            if (fechaPagoContainer) {
                if (pagadoCheckbox.checked) {
                    fechaPagoContainer.classList.remove('d-none');
                } else {
                    fechaPagoContainer.classList.add('d-none');
                }
            }
        };
        
        // Ejecutar al cargar la página
        toggleFechaPago();
        
        // Ejecutar cuando cambie el estado del checkbox
        pagadoCheckbox.addEventListener('change', toggleFechaPago);
    }
    
    // Selector de mes y año para consumos fijos
    const mesSelect = document.getElementById('mes_select');
    const anioSelect = document.getElementById('anio_select');
    
    if (mesSelect && anioSelect) {
        mesSelect.addEventListener('change', function() {
            actualizarFiltros();
        });
        
        anioSelect.addEventListener('change', function() {
            actualizarFiltros();
        });
        
        function actualizarFiltros() {
            const url = new URL(window.location.href);
            url.searchParams.set('mes', mesSelect.value);
            url.searchParams.set('año', anioSelect.value);
            window.location.href = url.toString();
        }
    }
});

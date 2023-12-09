document.addEventListener('DOMContentLoaded', (event) => {
    document.querySelectorAll('.confirmar-anulacion').forEach(enlace => {
        enlace.addEventListener('click', function() {
            const confirmacion = confirm('¿Estás seguro de que deseas anular esta cita?');
            if (confirmacion) {
                window.location.href = this.getAttribute('data-href');
            }
        });
    });
});
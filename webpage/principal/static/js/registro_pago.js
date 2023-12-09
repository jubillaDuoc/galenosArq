document.addEventListener('DOMContentLoaded', (event) => {
    document.querySelectorAll('.confirmar-pago_paciente').forEach(enlace => {
        enlace.addEventListener('click', function() {
            const confirmacion = confirm('¿Estás seguro de que deseas registrar el pago de esta cita?');
            if (confirmacion) {
                window.location.href = this.getAttribute('data-href');
            }
        });
    });
});
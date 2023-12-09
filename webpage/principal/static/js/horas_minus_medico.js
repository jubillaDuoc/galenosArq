function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    var selectedDays = [];

    var lastClickedDayIndex = null;
    var dayList = document.getElementById('day-list');
    dayList.querySelectorAll('li').forEach(function(li, index) {
        li.dataset.index = index;
        li.addEventListener('click', function(event) {
            handleDaySelection(event, index);
        });
    });

    function handleDaySelection(event, clickedIndex) {
        if (event.shiftKey && lastClickedDayIndex !== null) {
            var start = Math.min(clickedIndex, lastClickedDayIndex);
            var end = Math.max(clickedIndex, lastClickedDayIndex);
            for (var i = start; i <= end; i++) {
                dayList.children[i].classList.add('selected');
            }
            updateSelectedDays()
        } else {
            event.target.classList.toggle('selected');
            updateSelectedDays()
            lastClickedDayIndex = clickedIndex;
        }
    }

    function updateSelectedDays() {
        selectedDays = [];
        document.querySelectorAll('#day-list li.selected').forEach(function(li) {
            selectedDays.push(li.dataset.idhora);
        });
    }

    // Manejo del checkbox
    document.getElementById('addToCalendar').addEventListener('change', function() {
        document.getElementById('acceptButton').disabled = !this.checked;
    });

    // Manejo del botón "Aceptar"
    document.getElementById('acceptButton').addEventListener('click', function() {
        if (selectedDays.length > 0) {
            // Enviar los días y horas seleccionados
            var form = document.createElement('form');
            form.method = 'POST';
            form.action = '/admin_minushhmedico';

            var selectedDaysField = document.createElement('input');
            selectedDaysField.type = 'hidden';
            selectedDaysField.name = 'selectedDays';
            selectedDaysField.value = JSON.stringify(selectedDays);
            form.appendChild(selectedDaysField);

            // Obtener el valor de 'medico' y agregarlo al formulario
            var medicoId = document.getElementById('medicoId').value;
            var medicoField = document.createElement('input');
            medicoField.type = 'hidden';
            medicoField.name = 'medico';
            medicoField.value = medicoId;
            form.appendChild(medicoField);

            const csrftoken = getCookie('csrftoken');

            var csrfField = document.createElement('input');
            csrfField.type = 'hidden';
            csrfField.name = 'csrfmiddlewaretoken';
            csrfField.value = csrftoken;
            form.appendChild(csrfField);

            document.body.appendChild(form);
            form.submit();
        } else {
            alert('Selecciona al menos una fecha para continuar.');
        }
    });
});

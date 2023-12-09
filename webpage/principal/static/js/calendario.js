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
    var selectedHours = [];

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
            selectedDays.push(li.textContent);
        });
    }

    // Generar la lista de horas
    var lastClickedHourIndex = null;

    var hourList = document.getElementById('hour-list');
    for (var hour = 10; hour <= 17; hour++) {
        for (var min = 0; min < 60; min += 15) {
            var timeString = hour.toString().padStart(2, '0') + ':' + min.toString().padStart(2, '0');
            var li = document.createElement('li');
            li.textContent = timeString;
            li.dataset.index = hourList.children.length; // Guardar índice
            li.addEventListener('click', function(event) {
                handleHourSelection(event, this.dataset.index);
            });
            hourList.appendChild(li);
        }
    }

    function handleHourSelection(event, clickedIndex) {
        if (event.shiftKey && lastClickedHourIndex !== null) {
            var start = Math.min(clickedIndex, lastClickedHourIndex);
            var end = Math.max(clickedIndex, lastClickedHourIndex);
            for (var i = start; i <= end; i++) {
                hourList.children[i].classList.add('selected');
            }
            updateSelectedHours();
        } else {
            event.target.classList.toggle('selected');
            updateSelectedHours();
            lastClickedHourIndex = clickedIndex;
        }
    }

    function updateSelectedHours() {
        selectedHours = [];
        document.querySelectorAll('#hour-list li.selected').forEach(function(li) {
            selectedHours.push(li.textContent);
        });
    }

    // Manejo del checkbox
    document.getElementById('addToCalendar').addEventListener('change', function() {
        document.getElementById('acceptButton').disabled = !this.checked;
    });

    // Manejo del botón "Aceptar"
    document.getElementById('acceptButton').addEventListener('click', function() {
        if (selectedDays.length > 0 && selectedHours.length > 0) {
            // Enviar los días y horas seleccionados
            var form = document.createElement('form');
            form.method = 'POST';
            form.action = '/admin_hhcentro';

            var selectedDaysField = document.createElement('input');
            selectedDaysField.type = 'hidden';
            selectedDaysField.name = 'selectedDays';
            selectedDaysField.value = JSON.stringify(selectedDays);
            form.appendChild(selectedDaysField);

            var selectedHoursField = document.createElement('input');
            selectedHoursField.type = 'hidden';
            selectedHoursField.name = 'selectedHours';
            selectedHoursField.value = JSON.stringify(selectedHours);
            form.appendChild(selectedHoursField);

            const csrftoken = getCookie('csrftoken');

            var csrfField = document.createElement('input');
            csrfField.type = 'hidden';
            csrfField.name = 'csrfmiddlewaretoken';
            csrfField.value = csrftoken;
            form.appendChild(csrfField);

            document.body.appendChild(form);
            form.submit();
        } else {
            alert('Selecciona al menos un día y una hora para continuar.');
        }
    });
});

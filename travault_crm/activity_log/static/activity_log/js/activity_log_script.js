document.addEventListener('DOMContentLoaded', function () {
    const attendeesInput = document.getElementById('id_attendees_input_display');
    const hiddenAttendeesInput = document.getElementById('id_attendees_input');  
    const selectedAttendeesContainer = document.getElementById('selected-attendees');  // New container for attendee badges
    let selectedAttendees = [];

    attendeesInput.addEventListener('input', function () {
        const query = attendeesInput.value;
        if (query.length < 2) return;

        fetch(`${logMeetingData.searchAttendeesUrl}?q=${query}&company_pk=${logMeetingData.companyPk}`)
            .then(response => response.json())
            .then(data => {
                clearAttendeesList(); 
                showAttendeesSuggestions(data.results);
            });
    });

    function clearAttendeesList() {
        const oldList = document.getElementById('attendees-suggestions');
        if (oldList) oldList.remove();
    }

    function showAttendeesSuggestions(suggestions) {
        const suggestionList = document.createElement('ul');
        suggestionList.id = 'attendees-suggestions';
        suggestionList.classList.add('suggestions-list');

        suggestions.forEach(attendee => {
            const listItem = document.createElement('li');
            listItem.textContent = attendee.name;
            listItem.dataset.pk = attendee.id;
            listItem.style.cursor = 'pointer';  // Set the cursor to pointer on hover
            listItem.addEventListener('click', function () {
                selectAttendee(attendee);
            });
            suggestionList.appendChild(listItem);
        });

        attendeesInput.parentNode.appendChild(suggestionList);
    }

    function selectAttendee(attendee) {
        if (!selectedAttendees.includes(attendee.id)) {
            selectedAttendees.push(attendee.id);
            updateHiddenAttendeesInput();
            showSelectedAttendee(attendee.name);
        }
        attendeesInput.value = '';  // Clear the input field after selection
        clearAttendeesList();  // Clear the suggestions after selection
    }

    function showSelectedAttendee(name) {
        const attendeeBadge = document.createElement('span');
        attendeeBadge.className = 'badge me-2 mb-2 selected-company-badge';
        attendeeBadge.textContent = name;

        const closeButton = document.createElement('button');
        closeButton.innerHTML = '&times;';
        closeButton.className = 'btn-close-custom';
        closeButton.setAttribute('aria-label', 'Remove');

        closeButton.addEventListener('click', (e) => {
            e.preventDefault();
            const index = selectedAttendees.indexOf(name);
            if (index !== -1) {
                selectedAttendees.splice(index, 1);
                updateHiddenAttendeesInput();
                attendeeBadge.remove();
            }
        });

        attendeeBadge.appendChild(closeButton);
        selectedAttendeesContainer.appendChild(attendeeBadge);  // Append badges to the container
    }

    function updateHiddenAttendeesInput() {
        hiddenAttendeesInput.value = selectedAttendees.join(',');
    }
});

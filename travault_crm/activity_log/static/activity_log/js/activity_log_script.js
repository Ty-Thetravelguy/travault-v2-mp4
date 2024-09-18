document.addEventListener('DOMContentLoaded', function () {
    const attendeesInput = document.getElementById('id_attendees_input_display');
    const hiddenAttendeesInput = document.getElementById('id_attendees_input');
    let selectedAttendees = [];

    attendeesInput.addEventListener('input', function () {
        const query = attendeesInput.value;
        if (query.length < 2) return;  // Only search if input length is greater than 2 characters

        fetch(`${logMeetingData.searchAttendeesUrl}?q=${query}&company_pk=${logMeetingData.companyPk}`)
            .then(response => response.json())
            .then(data => {
                clearAttendeesList(); // Clear any old suggestions
                showAttendeesSuggestions(data); // Show new suggestions
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
            listItem.dataset.pk = attendee.pk;
            listItem.addEventListener('click', function () {
                selectAttendee(attendee);
            });
            suggestionList.appendChild(listItem);
        });

        attendeesInput.parentElement.appendChild(suggestionList);
    }

    function selectAttendee(attendee) {
        if (!selectedAttendees.includes(attendee.pk)) {
            selectedAttendees.push(attendee.pk);
            hiddenAttendeesInput.value = selectedAttendees.join(',');
        }
        clearAttendeesList(); // Clear suggestions after selection
        attendeesInput.value = ''; // Clear input field
    }
});
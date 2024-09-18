// activity_log/static/activity_log/js/activity_log_script.js

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('attendees-search');
    const resultsContainer = document.getElementById('attendees-results');
    const selectedContainer = document.getElementById('selected-attendees');
    const attendeesInput = document.getElementById('attendees-input');
    const companyPk = document.getElementById('company-pk')?.value;
    
    if (!searchInput || !resultsContainer || !selectedContainer || !attendeesInput || !companyPk) {
        console.error('One or more required elements are missing from the DOM');
        return;
    }

    let selectedAttendees = [];

    searchInput.addEventListener('input', debounce(function() {
        const query = this.value.trim();
        if (query.length > 2) {
            fetch(`${window.searchAttendeesURL}?q=${encodeURIComponent(query)}&company_pk=${companyPk}`)
                .then(response => response.json())
                .then(data => {
                    // ... rest of your code ...
                })
                .catch(error => {
                    console.error('Error fetching attendees:', error);
                });
        } else {
            resultsContainer.innerHTML = '';
        }
    }, 300));

    function addAttendee(attendeeInfo) {
        const isAlreadySelected = selectedAttendees.some(attendee =>
            attendee.model === attendeeInfo.model && attendee.pk === attendeeInfo.pk
        );

        if (!isAlreadySelected) {
            selectedAttendees.push(attendeeInfo);
            updateSelectedAttendees();
        }

        searchInput.value = '';
        resultsContainer.innerHTML = '';
    }

    function updateSelectedAttendees() {
        selectedContainer.innerHTML = '';
        attendeesInput.value = selectedAttendees.map(a => `${a.model}-${a.pk}`).join(',');

        selectedAttendees.forEach(attendee => {
            const span = document.createElement('span');
            span.classList.add('badge', 'bg-secondary', 'me-1', 'mb-1');
            span.textContent = attendee.name;

            const removeBtn = document.createElement('button');
            removeBtn.classList.add('btn-close', 'btn-close-white', 'btn-sm', 'ms-2');
            removeBtn.type = 'button';
            removeBtn.setAttribute('aria-label', 'Remove');
            removeBtn.addEventListener('click', function() {
                selectedAttendees = selectedAttendees.filter(item =>
                    !(item.model === attendee.model && item.pk === attendee.pk)
                );
                updateSelectedAttendees();
            });

            span.appendChild(removeBtn);
            selectedContainer.appendChild(span);
        });
    }

    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }

    function debounce(func, delay) {
        let timeoutId;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(context, args), delay);
        };
    }

    document.addEventListener('click', function(event) {
        if (!searchInput.contains(event.target) && !resultsContainer.contains(event.target)) {
            resultsContainer.innerHTML = '';
        }
    });
});
document.addEventListener('DOMContentLoaded', function() {
    // CKEditor initialization
    ClassicEditor
        .create(document.querySelector('#id_details'), {
            toolbar: ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote', 'undo', 'redo', 'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor']
        })
        .then(editor => {
            editor.editing.view.change(writer => {
                writer.setStyle('height', '400px', editor.editing.view.document.getRoot());
            });
            console.log('CKEditor initialized successfully', editor);
        })
        .catch(error => {
            console.error('Error initializing CKEditor:', error);
        });

    // Attendees search logic
    window.searchAttendeesURL = document.querySelector('meta[name="searchAttendeesURL"]').content;

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
                    // Process the search results
                    resultsContainer.innerHTML = '';
                    data.forEach(attendee => {
                        const resultItem = document.createElement('div');
                        resultItem.classList.add('attendee-result-item');
                        resultItem.textContent = attendee.name;
                        resultItem.addEventListener('click', function() {
                            addAttendee(attendee);
                        });
                        resultsContainer.appendChild(resultItem);
                    });
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

    function debounce(func, delay) {
        let timeoutId;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(context, args), delay);
        };
    }
});

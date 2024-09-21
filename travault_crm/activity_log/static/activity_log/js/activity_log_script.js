// activity_log/js/activity_log_script.js

document.addEventListener('DOMContentLoaded', function () {

    // -------------------
    // Attendees Handling
    // -------------------
    const attendeesInput = document.getElementById('id_attendees_input_display');
    const hiddenAttendeesInput = document.getElementById('id_attendees_input');  
    const selectedAttendeesContainer = document.getElementById('selected-attendees');  // Container for attendee badges
    let selectedAttendees = [];

    // Debounce function to limit the rate of API calls
    function debounce(func, delay) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), delay);
        };
    }

    attendeesInput.addEventListener('input', debounce(function () {
        const query = attendeesInput.value.trim();
        if (query.length < 2) {
            clearAttendeesList();
            return;
        }

        fetch(`${logMeetingData.searchAttendeesUrl}?q=${encodeURIComponent(query)}&company_pk=${logMeetingData.companyPk}`)
            .then(response => response.json())
            .then(data => {
                clearAttendeesList(); 
                showAttendeesSuggestions(data.results);
            })
            .catch(error => {
                // Handle the error as needed
            });
    }, 300));  // 300ms debounce delay

    function clearAttendeesList() {
        const oldList = document.getElementById('attendees-suggestions');
        if (oldList) oldList.remove();
    }

    function showAttendeesSuggestions(suggestions) {
        if (suggestions.length === 0) return;

        const suggestionList = document.createElement('ul');
        suggestionList.id = 'attendees-suggestions';
        suggestionList.classList.add('list-group', 'position-absolute', 'w-100', 'z-index-1000');

        suggestions.forEach(attendee => {
            const listItem = document.createElement('li');
            listItem.textContent = attendee.name;
            listItem.dataset.pk = attendee.id;  // 'contact_contact_1' or 'contact_user_19'
            listItem.classList.add('list-group-item', 'list-group-item-action');
            listItem.style.cursor = 'pointer';

            listItem.addEventListener('click', function () {
                selectAttendee(attendee);
            });

            suggestionList.appendChild(listItem);
        });

        // Position the suggestion list below the input field
        attendeesInput.parentNode.style.position = 'relative';
        attendeesInput.parentNode.appendChild(suggestionList);
    }

    function selectAttendee(attendee) {
        // Use the prefixed ID directly as returned from the server
        const prefixedId = attendee.id;  // e.g., 'contact_contact_1' or 'contact_user_19'

        if (!selectedAttendees.includes(prefixedId)) {
            selectedAttendees.push(prefixedId);
            updateHiddenAttendeesInput();
            showSelectedAttendee(attendee);
        }

        attendeesInput.value = ''; // Clear the input field after selection
        clearAttendeesList(); // Clear the suggestions after selection
    }

    function showSelectedAttendee(attendee) {
        const attendeeBadge = document.createElement('span');
        attendeeBadge.className = 'badge bg-primary me-2 mb-2 d-inline-flex align-items-center';
        attendeeBadge.textContent = attendee.name;

        // Use the prefixed ID directly
        const prefixedId = attendee.id;  // e.g., 'contact_contact_1' or 'contact_user_19'
        attendeeBadge.dataset.id = prefixedId; // Store the prefixed attendee ID

        const closeButton = document.createElement('button');
        closeButton.innerHTML = '&times;';
        closeButton.className = 'btn-close btn-close-white ms-2';
        closeButton.setAttribute('aria-label', 'Remove');

        // Bind the prefixed attendee ID to the click event using a closure
        closeButton.addEventListener('click', (e) => {
            e.preventDefault();
            const id = prefixedId; // Use the prefixed ID
            const index = selectedAttendees.indexOf(id);
            if (index !== -1) {
                selectedAttendees.splice(index, 1);
                updateHiddenAttendeesInput();
                attendeeBadge.remove();
            }
        });

        attendeeBadge.appendChild(closeButton);
        selectedAttendeesContainer.appendChild(attendeeBadge);
    }

    function updateHiddenAttendeesInput() {
        hiddenAttendeesInput.value = selectedAttendees.join(',');
    }

    // ------------------------------
    // CKEditor Initialization
    // ------------------------------
    let editorInstance;

    ClassicEditor
        .create(document.querySelector('#id_details'), {
            toolbar: {
                items: [
                    'heading', '|',
                    'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote', '|',
                    'undo', 'redo'
                ]
            },
            ui: {
                viewportOffset: {
                    top: 30
                }
            },
            height: 300
        })
        .then(editor => {
            editorInstance = editor;
            // Apply min-height
            editor.ui.view.editable.element.style.minHeight = '300px';
            editor.editing.view.change(writer => {
                writer.setStyle('min-height', '300px', editor.editing.view.document.getRoot());
            });
        })
        .catch(error => {
            // Handle the error as needed
        });

    // ------------------------------
    // To Do Task Modal Handling
    // ------------------------------
    const toDoTaskDateInput = document.getElementById('id_to_do_task_date');
    const toDoTaskModalElement = document.getElementById('toDoTaskModal');
    const toDoTaskModal = new bootstrap.Modal(toDoTaskModalElement);
    const saveToDoTaskButton = document.getElementById('saveToDoTask');
    const toDoTaskMessageInputModal = document.getElementById('id_to_do_task_message_modal');
    const toDoTaskMessageInput = document.getElementById('id_to_do_task_message');  // Hidden input in main form

    // Show modal when a to_do_task_date is selected
    toDoTaskDateInput.addEventListener('change', function() {
        if (this.value) {
            toDoTaskMessageInputModal.value = '';  // Clear previous message
            toDoTaskModal.show();
        }
    });

    // Save the message from the modal to the hidden input in the main form
    saveToDoTaskButton.addEventListener('click', function() {
        const message = toDoTaskMessageInputModal.value.trim();
        if (message) {
            // Set the hidden input in the main form
            toDoTaskMessageInput.value = message;
        } else {
            toDoTaskMessageInput.value = '';
        }
        toDoTaskModal.hide();
    });

    // Add a submit event listener to the form
    const meetingForm = document.getElementById('logMeetingForm');  // Matching form id
    if (meetingForm) {
        meetingForm.addEventListener('submit', function(event) {
            // Update the textarea with CKEditor's data
            if (editorInstance) {
                document.querySelector('#id_details').value = editorInstance.getData();
            }

            // Existing To-Do Task Validation
            const toDoTaskDate = toDoTaskDateInput.value;
            const toDoTaskMessage = toDoTaskMessageInput.value.trim();
            if (toDoTaskDate && !toDoTaskMessage) {
                event.preventDefault();
                alert('Please enter a follow-up message for your task.');
                toDoTaskModal.show();
            }
        });
    }

});

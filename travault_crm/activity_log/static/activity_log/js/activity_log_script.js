document.addEventListener('DOMContentLoaded', function () {

    // -------------------
    // Attendees Handling
    // -------------------
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
            showSelectedAttendee(attendee); // Pass the entire attendee object
        }
        attendeesInput.value = '';  // Clear the input field after selection
        clearAttendeesList();  // Clear the suggestions after selection
    }

    function showSelectedAttendee(attendee) {
        const attendeeBadge = document.createElement('span');
        attendeeBadge.className = 'badge me-2 mb-2 selected-company-badge';
        attendeeBadge.textContent = attendee.name;
        attendeeBadge.dataset.id = attendee.id; // Store the attendee ID

        const closeButton = document.createElement('button');
        closeButton.innerHTML = '&times;';
        closeButton.className = 'btn-close-custom';
        closeButton.setAttribute('aria-label', 'Remove');

        // Bind the attendee ID to the click event using a closure
        closeButton.addEventListener('click', (e) => {
            e.preventDefault();
            const id = attendee.id;
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
            }
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
            console.error(error);
        });

    // ------------------------------
    // To Do Task Modal Handling
    // ------------------------------
    const toDoTaskDateInput = document.getElementById('id_to_do_task_date');
    const toDoTaskModalElement = document.getElementById('toDoTaskModal');
    const toDoTaskModal = new bootstrap.Modal(toDoTaskModalElement);
    const saveToDoTaskButton = document.getElementById('saveToDoTask');
    const toDoTaskMessageInputModal = document.getElementById('id_to_do_task_message_modal');
    const toDoTaskMessageInput = document.getElementById('id_to_do_task_message');  // Updated reference

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

});

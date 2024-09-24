// activity_log/js/activity_log_script.js

document.addEventListener('DOMContentLoaded', function () {


    // -------------------
    // Contacts Handling
    // -------------------
    const contactsInput = document.getElementById('id_contacts_input_display');
    const hiddenContactsInput = document.getElementById('id_contacts_input');  
    const selectedContactsContainer = document.getElementById('selected-contacts');  // Container for contact badges
    let selectedContacts = [];

    // Debounce function to limit the rate of API calls
    function debounce(func, delay) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), delay);
        };
    }

    contactsInput.addEventListener('input', debounce(function () {
        const query = contactsInput.value.trim();
        if (query.length < 2) {
            clearContactsList();
            return;
        }

        fetch(`${logCallData.searchContactsUrl}?q=${encodeURIComponent(query)}&company_pk=${logCallData.companyPk}`)
            .then(response => response.json())
            .then(data => {
                clearContactsList(); 
                showContactsSuggestions(data.results);
            })
            .catch(error => {
                // Handle the error as needed
            });
    }, 300));  // 300ms debounce delay

    function clearContactsList() {
        const oldList = document.getElementById('contacts-suggestions');
        if (oldList) oldList.remove();
    }

    function showContactsSuggestions(suggestions) {
        if (suggestions.length === 0) return;

        const suggestionList = document.createElement('ul');
        suggestionList.id = 'contacts-suggestions';
        suggestionList.classList.add('list-group', 'position-absolute', 'w-100', 'z-index-1000');

        suggestions.forEach(contact => {
            const listItem = document.createElement('li');
            listItem.textContent = contact.name;
            listItem.dataset.pk = contact.id;
            listItem.classList.add('list-group-item', 'list-group-item-action');
            listItem.style.cursor = 'pointer';

            listItem.addEventListener('click', function () {
                selectContact(contact);
            });

            suggestionList.appendChild(listItem);
        });

        contactsInput.parentNode.style.position = 'relative';
        contactsInput.parentNode.appendChild(suggestionList);
    }

    function selectContact(contact) {
        const id = contact.id;

        if (!selectedContacts.includes(id)) {
            selectedContacts.push(id);
            updateHiddenContactsInput();
            showSelectedContact(contact);
        }

        contactsInput.value = ''; // Clear the input field after selection
        clearContactsList(); // Clear the suggestions after selection
    }

    function showSelectedContact(contact) {
        const contactBadge = document.createElement('span');
        contactBadge.className = 'badge bg-primary me-2 mb-2 d-inline-flex align-items-center';
        contactBadge.textContent = contact.name;

        contactBadge.dataset.id = contact.id; // Store the contact ID

        const closeButton = document.createElement('button');
        closeButton.innerHTML = '&times;';
        closeButton.className = 'btn-close btn-close-white ms-2';
        closeButton.setAttribute('aria-label', 'Remove');

        closeButton.addEventListener('click', (e) => {
            e.preventDefault();
            const id = contact.id;
            const index = selectedContacts.indexOf(id);
            if (index !== -1) {
                selectedContacts.splice(index, 1);
                updateHiddenContactsInput();
                contactBadge.remove();
            }
        });

        contactBadge.appendChild(closeButton);
        selectedContactsContainer.appendChild(contactBadge);
    }

    function updateHiddenContactsInput() {
        hiddenContactsInput.value = selectedContacts.join(',');
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

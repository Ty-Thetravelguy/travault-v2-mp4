document.addEventListener('DOMContentLoaded', function () {
    // -------------------
    // Unified Data Variables
    // -------------------
    // This allows passing necessary URLs and data through forms (Meeting, Call, Email)
    // Each form must include a script block defining its data.

    // -------------------
    // Attendees/Contacts Handling
    // -------------------
    // Generalized handling for multiple forms
    // Generalized handling for multiple forms
    const forms = document.querySelectorAll('form[id$="Form"]'); // Select all forms ending with 'Form'

    forms.forEach(form => {
        const formId = form.id;

        let searchAttendeesUrl;
        let companyPk;
        let inputDisplayId;
        let hiddenInputId;
        let selectedContainerId;

        if (formId === 'logMeetingForm') {
            searchAttendeesUrl = logMeetingData.searchAttendeesUrl;
            companyPk = logMeetingData.companyPk;
            inputDisplayId = '#id_attendees_input_display';
            hiddenInputId = '#id_attendees_input';
            selectedContainerId = '#selected-attendees';
        } else if (formId === 'logCallForm') {
            searchAttendeesUrl = logCallData.searchAttendeesUrl;
            companyPk = logCallData.companyPk;
            inputDisplayId = '#id_contacts_input_display';
            hiddenInputId = '#id_contacts_input';
            selectedContainerId = '#selected-contacts';
        } else if (formId === 'logEmailForm') {
            searchAttendeesUrl = logEmailData.searchAttendeesUrl;
            companyPk = logEmailData.companyPk;
            inputDisplayId = '#id_contacts_input_display';
            hiddenInputId = '#id_contacts_input';
            selectedContainerId = '#selected-contacts';
        }

        // If data is not defined, skip this form
        if (!searchAttendeesUrl || !companyPk) return;

        // Now use inputDisplayId, hiddenInputId, selectedContainerId
        const contactsInputDisplay = form.querySelector(inputDisplayId);
        const hiddenContactsInput = form.querySelector(hiddenInputId);
        const selectedContactsContainer = form.querySelector(selectedContainerId);
        let selectedContacts = [];

        if (contactsInputDisplay && hiddenContactsInput && selectedContactsContainer) {
            // Debounce function to limit the rate of API calls
            function debounce(func, delay) {
                let timeout;
                return function(...args) {
                    clearTimeout(timeout);
                    timeout = setTimeout(() => func.apply(this, args), delay);
                };
            }

            contactsInputDisplay.addEventListener('input', debounce(function () {
                const query = contactsInputDisplay.value.trim();
                if (query.length < 2) {
                    clearContactsList();
                    return;
                }

                fetch(`${searchAttendeesUrl}?q=${encodeURIComponent(query)}&company_pk=${companyPk}`)
                    .then(response => response.json())
                    .then(data => {
                        clearContactsList(); 
                        showContactsSuggestions(data.results, formId);
                    })
                    .catch(error => {
                        console.error('Error fetching attendees:', error);
                    });
            }, 300));  // 300ms debounce delay

            function clearContactsList() {
                const oldList = form.querySelector('#contacts-suggestions');
                if (oldList) oldList.remove();
            }

            function showContactsSuggestions(suggestions, formId) {
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
                        selectContact(contact, formId);
                    });

                    suggestionList.appendChild(listItem);
                });

                contactsInputDisplay.parentNode.style.position = 'relative';
                contactsInputDisplay.parentNode.appendChild(suggestionList);
            }

            function selectContact(contact, formId) {
                const id = contact.id;

                if (!selectedContacts.includes(id)) {
                    selectedContacts.push(id);
                    updateHiddenContactsInput();
                    showSelectedContact(contact, formId);
                }

                contactsInputDisplay.value = ''; // Clear the input field after selection
                clearContactsList(); // Clear the suggestions after selection
            }

            function showSelectedContact(contact, formId) {
                const contactBadge = document.createElement('span');
                contactBadge.className = 'badge me-2 mb-2 d-inline-flex align-items-center';
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
        }

        // ------------------------------
        // CKEditor Initialization
        // ------------------------------
        const detailsField = form.querySelector('#id_details');
        if (detailsField) {
            ClassicEditor
                .create(detailsField, {
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
                    form.editorInstance = editor;
                    editor.editing.view.change(writer => {
                        writer.setStyle('min-height', '400px', editor.editing.view.document.getRoot());
                    });
                })
                .catch(error => {
                    console.error('CKEditor initialization error:', error);
                });
        }

        // ------------------------------
        // To Do Task Modal Handling
        // ------------------------------
        const toDoTaskDateInput = form.querySelector('#id_to_do_task_date');
        const toDoTaskModalElement = document.querySelector('#toDoTaskModal'); // Changed
        const saveToDoTaskButton = document.querySelector('#saveToDoTask'); // Changed
        const toDoTaskMessageInputModal = document.querySelector('#id_to_do_task_message_modal'); // Changed
        const toDoTaskMessageInput = form.querySelector('#id_to_do_task_message');
        
        if (toDoTaskDateInput && toDoTaskModalElement && saveToDoTaskButton && toDoTaskMessageInputModal && toDoTaskMessageInput) {
            const toDoTaskModal = new bootstrap.Modal(toDoTaskModalElement);

            // Show modal when a to_do_task_date is selected
            toDoTaskDateInput.addEventListener('change', function() {
                if (this.value) {
                    toDoTaskMessageInputModal.value = '';  // Clear previous message
                    toDoTaskModal.show();  // Show the modal
                }
            });

            // Save the message from the modal to the hidden input in the main form
            saveToDoTaskButton.addEventListener('click', function() {
                const message = toDoTaskMessageInputModal.value.trim();
                if (message) {
                    toDoTaskMessageInput.value = message;
                } else {
                    toDoTaskMessageInput.value = '';
                }
                toDoTaskModal.hide();
            });

            // Add a submit event listener to the form
            form.addEventListener('submit', function(event) {
                // Update the textarea with CKEditor's data
                if (form.editorInstance) {
                    form.querySelector('#id_details').value = form.editorInstance.getData(); // Use form.querySelector
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
});

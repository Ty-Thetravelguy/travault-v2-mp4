// Main event listener that initializes the form handling when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // -------------------
    // Unified Data Variables
    // -------------------
    // These variables are used across different form types (Meeting, Call, Email)
    // Each form must include a script block that defines its specific data

    // Select all forms that end with 'Form' in their ID
    const forms = document.querySelectorAll('form[id$="Form"]');

    // Iterate through each form to set up contact/attendee handling
    forms.forEach(form => {
        const formId = form.id;

        // Variables to store form-specific configuration
        let searchAttendeesUrl;    // API endpoint for searching attendees/contacts
        let companyPk;             // Company primary key
        let inputDisplayId;        // ID of the visible input field
        let hiddenInputId;        // ID of the hidden input storing selected contacts
        let selectedContainerId;   // ID of container showing selected contacts

        // Configure variables based on form type
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

        // Skip if required data is not defined
        if (!searchAttendeesUrl || !companyPk) return;

        // Get DOM elements for the current form
        const contactsInputDisplay = form.querySelector(inputDisplayId);
        const hiddenContactsInput = form.querySelector(hiddenInputId);
        const selectedContactsContainer = form.querySelector(selectedContainerId);
        let selectedContacts = [];  // Array to store selected contact IDs

        // Proceed only if all required elements are found
        if (contactsInputDisplay && hiddenContactsInput && selectedContactsContainer) {
            // Debounce function to prevent excessive API calls
            // Only executes the callback after delay milliseconds have elapsed since the last call
            function debounce(func, delay) {
                let timeout;
                return function (...args) {
                    clearTimeout(timeout);
                    timeout = setTimeout(() => func.apply(this, args), delay);
                };
            }

            // Add input listener with debouncing for contact search
            contactsInputDisplay.addEventListener(
                'input',
                debounce(function () {
                    const query = contactsInputDisplay.value.trim();
                    // Only search if query is at least 2 characters
                    if (query.length < 2) {
                        clearContactsList();
                        return;
                    }

                    // Fetch contacts/attendees from the API
                    fetch(`${searchAttendeesUrl}?q=${encodeURIComponent(query)}&company_pk=${companyPk}`)
                        .then(response => response.json())
                        .then(data => {
                            clearContactsList();
                            showContactsSuggestions(data.results, formId);
                        })
                        .catch(error => {
                            console.error('Error fetching attendees:', error);
                        });
                }, 300)  // Wait 300ms after last keystroke before searching
            );

            // Remove the current suggestions list if it exists
            function clearContactsList() {
                const oldList = form.querySelector('#contacts-suggestions');
                if (oldList) oldList.remove();
            }

            // Create and display the suggestions dropdown
            function showContactsSuggestions(suggestions, formId) {
                if (suggestions.length === 0) return;

                // Create suggestions list with Bootstrap styling
                const suggestionList = document.createElement('ul');
                suggestionList.id = 'contacts-suggestions';
                suggestionList.classList.add('list-group', 'position-absolute', 'w-100', 'z-index-1000');

                // Add each suggestion as a clickable item
                suggestions.forEach(contact => {
                    const listItem = document.createElement('li');
                    listItem.textContent = contact.name;
                    listItem.dataset.pk = contact.id;
                    listItem.classList.add('list-group-item', 'list-group-item-action');
                    listItem.style.cursor = 'pointer';

                    // Add click handler to select the contact
                    listItem.addEventListener('click', function () {
                        selectContact(contact, formId);
                    });

                    suggestionList.appendChild(listItem);
                });

                // Position the suggestions list below the input
                contactsInputDisplay.parentNode.style.position = 'relative';
                contactsInputDisplay.parentNode.appendChild(suggestionList);
            }

            // Handle contact selection
            function selectContact(contact, formId) {
                const id = contact.id;

                // Only add if not already selected
                if (!selectedContacts.includes(id)) {
                    selectedContacts.push(id);
                    updateHiddenContactsInput();
                    showSelectedContact(contact, formId);
                }

                // Clean up after selection
                contactsInputDisplay.value = '';
                clearContactsList();
            }

            // Display selected contact as a badge with remove button
            function showSelectedContact(contact, formId) {
                // Create badge with Bootstrap styling
                const contactBadge = document.createElement('span');
                contactBadge.className = 'badge me-2 mb-2 d-inline-flex align-items-center';
                contactBadge.textContent = contact.name;
                contactBadge.dataset.id = contact.id;

                // Add remove button to badge
                const closeButton = document.createElement('button');
                closeButton.innerHTML = '&times;';
                closeButton.className = 'btn-close btn-close-white ms-2';
                closeButton.setAttribute('aria-label', 'Remove');

                // Handle removing the contact
                closeButton.addEventListener('click', e => {
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

            // Update the hidden input with selected contact IDs
            function updateHiddenContactsInput() {
                hiddenContactsInput.value = selectedContacts.join(',');
            }
        }

        // ------------------------------
        // CKEditor Initialization
        // ------------------------------
        const detailsField = form.querySelector('#id_details');
        let editorInstance; // Declare editorInstance in the outer scope
        if (detailsField) {
            ClassicEditor
                .create(detailsField, {
                    toolbar: {
                        items: [
                            'heading',
                            '|',
                            'bold',
                            'italic',
                            'link',
                            'bulletedList',
                            'numberedList',
                            'blockQuote',
                            '|',
                            'undo',
                            'redo',
                        ],
                    },
                    ui: {
                        viewportOffset: {
                            top: 30,
                        },
                    },
                    height: 300,
                })
                .then(editor => {
                    // CKEditor is initialized and 'editor' is available here
                    editorInstance = editor; // Store the editor instance
                })
                .catch(error => {
                    console.error('CKEditor initialization error:', error);
                });
        }

        // ------------------------------
        // To Do Task Modal Handling
        // ------------------------------
        const toDoTaskDateInput = form.querySelector('#id_to_do_task_date');
        const toDoTaskModalElement = document.querySelector('#toDoTaskModal');
        const saveToDoTaskButton = document.querySelector('#saveToDoTask');
        const toDoTaskMessageInputModal = document.querySelector('#id_to_do_task_message_modal');
        const toDoTaskMessageInput = form.querySelector('#id_to_do_task_message');

        let toDoTaskModal; // Declare variable to store the modal instance
        if (
            toDoTaskDateInput &&
            toDoTaskModalElement &&
            saveToDoTaskButton &&
            toDoTaskMessageInputModal &&
            toDoTaskMessageInput
        ) {
            toDoTaskModal = new bootstrap.Modal(toDoTaskModalElement);

            // Show modal when a to_do_task_date is selected
            toDoTaskDateInput.addEventListener('change', function () {
                if (this.value) {
                    toDoTaskMessageInputModal.value = ''; // Clear previous message
                    toDoTaskModal.show(); // Show the modal
                }
            });

            // Save the message from the modal to the hidden input in the main form
            saveToDoTaskButton.addEventListener('click', function () {
                const message = toDoTaskMessageInputModal.value.trim();
                if (message) {
                    toDoTaskMessageInput.value = message;
                } else {
                    toDoTaskMessageInput.value = '';
                }
                toDoTaskModal.hide();
            });
        }

        // ------------------------------
        // Form Submission Handling
        // ------------------------------
        form.addEventListener('submit', function (event) {
            console.log("Form data before submission:", new FormData(form));
    
            // Update the textarea with CKEditor's data
            if (editorInstance) {
                detailsField.value = editorInstance.getData();
            }

            // Existing To-Do Task Validation
            if (toDoTaskDateInput && toDoTaskMessageInput && toDoTaskModal) {
                const toDoTaskDate = toDoTaskDateInput.value;
                const toDoTaskMessage = toDoTaskMessageInput.value.trim();

                if (toDoTaskDate && !toDoTaskMessage) {
                    event.preventDefault();
                    alert('Please enter a follow-up message for your task.');
                    toDoTaskModal.show();
                }
            }
        });
    });
});
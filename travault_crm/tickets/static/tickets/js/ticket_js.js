// travault_crm/tickets/static/tickets/js/ticket_js.js
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded");

    // Clickable rows functionality
    function initializeClickableRows() {
        const rows = document.querySelectorAll('.clickable-row');
        rows.forEach(row => {
            row.addEventListener('click', function() {
                window.location.href = this.dataset.href;
            });
            row.style.cursor = 'pointer';
        });
    }

    initializeClickableRows();

    // Quick Update Fields via AJAX
    const quickUpdateFields = ['owner', 'assigned_to', 'priority', 'status'];
    
    quickUpdateFields.forEach(field => {
        const select = document.getElementById(`${field}-select`);
        if (select) {
            select.addEventListener('change', function() {
                quickUpdateField(field, this.value);
            });
        }
    });

    function quickUpdateField(field, value) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const ticketId = window.location.pathname.split('/').filter(Boolean).pop();

        fetch(`/tickets/${ticketId}/update-field/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `field=${field}&value=${value}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.reload();
            } else {
                displayDjangoMessage(data.error || 'An error occurred.', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            displayDjangoMessage('An error occurred while updating the ticket.', 'error');
        });
    }

    function displayDjangoMessage(message, type) {
        // Implement a function to display messages to the user.
        // This can be using Bootstrap alerts or any other UI component.
        alert(message);  // Simple alert for demonstration
    }

    // Category field functionality
    var categoryTypeField = document.getElementById('id_category_type');
    var categoryField = document.getElementById('id_category');

    if (categoryTypeField && categoryField) {
        categoryTypeField.addEventListener('change', updateCategoryField);
        function updateCategoryField() {
            var selectedCategoryType = categoryTypeField.value;
            var currentCategory = categoryField.value;  // Store the current category
        
            // Reset options
            categoryField.innerHTML = '<option value="">Select a category</option>';
        
            if (selectedCategoryType === 'client') {
                categoryField.removeAttribute('disabled'); // Enable the dropdown
                populateOptions([
                    { value: 'complaint', text: 'Complaint' },
                    { value: 'query', text: 'Query' },
                    { value: 'request', text: 'Request' }
                ]);
            } else if (selectedCategoryType === 'agency') {
                categoryField.removeAttribute('disabled'); // Enable the dropdown
                populateOptions([
                    { value: 'consultant_error', text: 'Consultant Error' },
                    { value: 'supplier_error', text: 'Supplier Error' },
                    { value: 'supplier_query', text: 'Supplier Query' },
                    { value: 'system_error', text: 'System Error' },
                    { value: 'system_query', text: 'System Query' },
                    { value: 'system_enhancement', text: 'System Enhancement' }
                ]);
            } else {
                // If no valid category type is selected, disable the category field
                categoryField.setAttribute('disabled', 'disabled');
            }
        
            // Restore the previously selected category if it exists in the new options
            if (currentCategory) {
                const option = categoryField.querySelector(`option[value="${currentCategory}"]`);
                if (option) {
                    option.selected = true;
                }
            }
        }

        function populateOptions(options) {
            options.forEach(function(option) {
                var optionElement = document.createElement('option');
                optionElement.value = option.value;
                optionElement.textContent = option.text;
                categoryField.appendChild(optionElement);
            });
        }

        // Attach change listener to category type field
        categoryTypeField.addEventListener('change', updateCategoryField);

        // Initialize the category field state on page load only for new tickets
        if (!categoryField.value) {
            updateCategoryField();
    }
    }

    // Subject field functionality
    var subjectField = document.getElementById('id_subject');
    var subjectSuggestions = document.getElementById('subject_suggestions');
    var addSubjectButton = document.getElementById('add_subject');

    if (subjectField && addSubjectButton) {
        subjectField.addEventListener('input', function() {
            var query = this.value;
            if (query.length > 2) {
                fetchSubjects(query);
            } else {
                subjectSuggestions.innerHTML = '';
            }
        });

        function fetchSubjects(query) {
            fetch(`/tickets/ticket-subject-autocomplete/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    subjectSuggestions.innerHTML = '';
                    data.forEach(subject => {
                        var item = document.createElement('a');
                        item.href = '#';
                        item.className = 'list-group-item list-group-item-action';
                        item.textContent = subject.text;
                        item.addEventListener('click', function(e) {
                            e.preventDefault();
                            subjectField.value = subject.text;
                            subjectField.dataset.subjectId = subject.id;  // Store the ID
                            subjectSuggestions.innerHTML = '';
                        });
                        subjectSuggestions.appendChild(item);
                    });
                });
        }

        let isProcessing = false;
       
        function addSubjectHandler(event) {
            event.preventDefault();
            event.stopPropagation();

            if (isProcessing) {
                return;
            }

            var newSubject = subjectField.value.trim();
            if (newSubject) {
                isProcessing = true;
                fetch('/tickets/create-ticket-subject/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: `subject=${encodeURIComponent(newSubject)}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success === false) {
                        displayDjangoMessage(data.error || 'Failed to add subject.', 'error');
                        return;
                    }
                    subjectField.value = data.subject;
                    subjectField.dataset.subjectId = data.id;  // Store the ID
                    subjectSuggestions.innerHTML = '';
                    showAlert('New subject added successfully!');
                })
                .catch(error => {
                    console.error('Error:', error);
                    displayDjangoMessage('An error occurred while adding the subject.', 'error');
                })
                .finally(() => {
                    isProcessing = false;
                });
            }
        }

        addSubjectButton.addEventListener('click', addSubjectHandler);
    }
    
    let alertShown = false;
    
    function showAlert(message) {
        if (!alertShown) {
            alertShown = true;
            alert(message);
            setTimeout(() => {
                alertShown = false;
            }, 1000);
        }
    }

    // Action modal functionality
    const actionForm = document.getElementById('actionForm');
    const saveActionBtn = document.getElementById('saveAction');

    if (actionForm && saveActionBtn) {
        saveActionBtn.addEventListener('click', function(e) {
            e.preventDefault();
            actionForm.submit();
        });
    }

    // Edit Action Modal
    const editActionModal = document.getElementById('editActionModal');
    if (editActionModal) {
        editActionModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const actionId = button.getAttribute('data-action-id');
            const form = this.querySelector('#editActionForm');
            form.action = form.action.replace(/\/0\//, `/${actionId}/`);
            this.querySelector('#editActionId').value = actionId;
            
            // Populate form fields with current action data
            const actionType = button.closest('.card').querySelector('.card-header').textContent.trim();
            const actionDetails = button.closest('.card').querySelector('.card-body .card-text').textContent.trim();
            this.querySelector('#editActionType').value = actionType.toLowerCase().replace(' ', '_');
            this.querySelector('#editActionDetails').value = actionDetails;
        });
    }

    // Delete Action Modal
    const deleteActionModal = document.getElementById('deleteActionModal');
    if (deleteActionModal) {
        deleteActionModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const actionId = button.getAttribute('data-action-id');
            const form = this.querySelector('#deleteActionForm');
            form.action = form.action.replace(/\/0\//, `/${actionId}/`);
            this.querySelector('#deleteActionId').value = actionId;
            this.querySelector('#deleteActionIdConfirm').textContent = actionId;
        });
    }

    // Sorting functionality
    const table = document.getElementById('tickets-table');
    console.log("Table found:", table);

    const headers = table.querySelectorAll('th[data-sort]');
    console.log("Sortable headers found:", headers.length);

    let currentSort = { column: null, direction: 'asc' };

    headers.forEach(header => {
        header.addEventListener('click', () => {
            console.log("Header clicked:", header.dataset.sort);
            const column = header.dataset.sort;
            const direction = currentSort.column === column && currentSort.direction === 'asc' ? 'desc' : 'asc';
            sortTable(column, direction);
            currentSort = { column, direction };
            updateSortIcons();
        });
    });

    function sortTable(column, direction) {
        console.log("Sorting table:", column, direction);
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr.clickable-row'));
        console.log("Rows to sort:", rows.length);

        rows.sort((a, b) => {
            const aValue = a.children[getColumnIndex(column)].textContent.trim();
            const bValue = b.children[getColumnIndex(column)].textContent.trim();
            console.log("Comparing:", aValue, bValue);
            return direction === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
        });

        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));
    }

    function getColumnIndex(column) {
        return Array.from(headers).findIndex(header => header.dataset.sort === column);
    }

    function updateSortIcons() {
        headers.forEach(header => {
            const icon = header.querySelector('.sort-icon');
            icon.classList.remove('asc', 'desc');
            if (header.dataset.sort === currentSort.column) {
                icon.classList.add(currentSort.direction);
            }
        });
    }

    // Filtering functionality
    const filters = {
        status: document.getElementById('status-filter'),
        priority: document.getElementById('priority-filter'),
        assignedTo: document.getElementById('assigned-to-filter'),
        categoryType: document.getElementById('category-type-filter'),
        category: document.getElementById('category-filter'),
        owner: document.getElementById('owner-filter')
    };

    console.log("Filters found:", Object.values(filters).filter(f => f !== null).length);

    Object.values(filters).forEach(filter => {
        if (filter) {
            filter.addEventListener('change', applyFilters);
        }
    });

    function applyFilters() {
        console.log("Applying filters");
        const rows = table.querySelectorAll('tbody tr.clickable-row');
        console.log("Rows to filter:", rows.length);

        rows.forEach(row => {
            const status = row.children[0].textContent.trim();
            const priority = row.children[1].textContent.trim();
            const assignedTo = row.children[3].textContent.trim();
            const categoryType = row.children[7].textContent.trim();
            const category = row.children[8].textContent.trim();
            const owner = row.children[9].textContent.trim();

            const showRow = (
                (filters.status.value === 'all' || (filters.status.value === 'active' && status !== 'Closed')) &&
                (filters.priority.value === '' || priority.toLowerCase() === filters.priority.value.toLowerCase()) &&
                (filters.assignedTo.value === '' || assignedTo === filters.assignedTo.value) &&
                (filters.categoryType.value === '' || categoryType.toLowerCase() === filters.categoryType.value.toLowerCase()) &&
                (filters.category.value === '' || category === filters.category.value) &&
                (filters.owner.value === '' || owner === filters.owner.value)
            );

            row.style.display = showRow ? '' : 'none';
        });
    }

    // Initialize filters
    applyFilters();

    console.log("Initialization complete");
});
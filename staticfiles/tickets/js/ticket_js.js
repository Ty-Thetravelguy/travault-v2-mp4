document.addEventListener('DOMContentLoaded', function() {

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
    const headers = table.querySelectorAll('th[data-sort]');
    let currentSort = { column: null, direction: 'asc' };

    headers.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.dataset.sort;
            const direction = currentSort.column === column && currentSort.direction === 'asc' ? 'desc' : 'asc';
            sortTable(column, direction);
            currentSort = { column, direction };
            updateSortIcons();
        });
    });

    function sortTable(column, direction) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr.clickable-row'));

        rows.sort((a, b) => {
            const aValue = a.children[getColumnIndex(column)].textContent.trim();
            const bValue = b.children[getColumnIndex(column)].textContent.trim();
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

    Object.values(filters).forEach(filter => {
        if (filter) {
            filter.addEventListener('change', applyFilters);
        }
    });

    function updateCategoryOptions() {
        const categoryTypeFilter = filters.categoryType;
        const categoryFilter = filters.category;

        if (!categoryTypeFilter || !categoryFilter) return;

        const selectedCategoryType = categoryTypeFilter.value;

        // Clear existing options
        categoryFilter.innerHTML = '<option value="">All Categories</option>';

        if (selectedCategoryType === '') {
            // Add all categories
            addCategoryOptions(CATEGORY_CHOICES_CLIENT);
            addCategoryOptions(CATEGORY_CHOICES_AGENCY);
        } else if (selectedCategoryType === 'client') {
            addCategoryOptions(CATEGORY_CHOICES_CLIENT);
        } else if (selectedCategoryType === 'agency') {
            addCategoryOptions(CATEGORY_CHOICES_AGENCY);
        }

        // Trigger change event to update filters
        categoryFilter.dispatchEvent(new Event('change'));
    }

    function addCategoryOptions(categories) {
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category[0];
            option.textContent = category[1];
            filters.category.appendChild(option);
        });
    }

    // Define category choices
    const CATEGORY_CHOICES_CLIENT = [
        ['complaint', 'Complaint'],
        ['query', 'Query'],
        ['request', 'Request'],
    ];

    const CATEGORY_CHOICES_AGENCY = [
        ['consultant_error', 'Consultant Error'],
        ['supplier_error', 'Supplier Error'],
        ['supplier_query', 'Supplier Query'],
        ['system_error', 'System Error'],
        ['system_query', 'System Query'],
        ['system_enhancement', 'System Enhancement'],
    ];

    // Add event listener for category type change
    if (filters.categoryType) {
        filters.categoryType.addEventListener('change', function() {
            updateCategoryOptions();
            applyFilters();
        });
    }

    // Call updateCategoryOptions on page load
    updateCategoryOptions();

    // Row striping after filtering
    function reapplyRowStriping() {
        const visibleRows = Array.from(table.querySelectorAll('tbody tr.clickable-row'))
            .filter(row => row.style.display !== 'none'); // Only count visible rows
    
        visibleRows.forEach((row, index) => {
            // Apply alternating row colors
            row.style.backgroundColor = index % 2 === 0 ? '#e9ffe9' : '#f9f9f9'; // Light green or grey
        });
    }

    // Apply filters
    function applyFilters() {
        const rows = table.querySelectorAll('tbody tr.clickable-row');
        
        // Retrieve filter values
        const statusFilter = filters.status.value;
        const priorityFilter = filters.priority.value.toLowerCase();
        const categoryTypeFilter = filters.categoryType.value.toLowerCase();
        const categoryFilter = filters.category.value.toLowerCase();
        const ownerFilter = filters.owner.value;
        const assignedToFilter = filters.assignedTo.value;
    
        rows.forEach(row => {
            const status = row.dataset.status;
            const priority = row.querySelector('td:nth-child(2)').textContent.trim().toLowerCase();
            const categoryType = row.dataset.category_type || '';
            const category = row.dataset.category || '';
            const assignedTo = row.dataset.assigned_to || '';
            const owner = row.dataset.owner || '';

            const isStatusMatch = (statusFilter === 'all') || 
                                (statusFilter === 'active' && status !== 'closed') ||
                                (status === statusFilter);
    
            const isPriorityMatch = (priorityFilter === '') || (priority === priorityFilter);
            const isCategoryTypeMatch = (categoryTypeFilter === '') || (categoryType === categoryTypeFilter);
            const isCategoryMatch = (categoryFilter === '') || (category === categoryFilter);
            const isOwnerMatch = (ownerFilter === '') || (owner === ownerFilter);
            const isAssignedToMatch = (assignedToFilter === '') || (assignedTo === assignedToFilter);
    
            const showRow = isStatusMatch && 
                            isPriorityMatch && 
                            isCategoryTypeMatch &&
                            isCategoryMatch &&
                            isOwnerMatch &&
                            isAssignedToMatch;
    
            row.style.display = showRow ? '' : 'none';
        });
    
        // Reapply row striping after filtering
        reapplyRowStriping();
    }

    // Initialize filters on page load
    applyFilters();

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

});

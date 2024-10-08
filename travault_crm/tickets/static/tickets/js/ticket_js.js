document.addEventListener('DOMContentLoaded', function() {
    
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

    // Category field functionality
    var categoryTypeField = document.getElementById('id_category_type');
    var categoryField = document.getElementById('id_category');

    if (!categoryTypeField || !categoryField) {
        return;
    }

    function updateCategoryField() {
        var selectedCategoryType = categoryTypeField.value;

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

    // Initialize the category field state on page load
    updateCategoryField();

    // Subject field functionality
    var subjectField = document.getElementById('id_subject');
    var subjectSuggestions = document.getElementById('subject_suggestions');
    var addSubjectButton = document.getElementById('add_subject');

    if (!subjectField || !addSubjectButton) {
        return;
    }

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
                subjectField.value = data.subject;
                subjectField.dataset.subjectId = data.id;  // Store the ID
                subjectSuggestions.innerHTML = '';
                showAlert('New subject added successfully!');
            })
            .catch(error => {
            })
            .finally(() => {
                isProcessing = false;
            });
        }
    }

    addSubjectButton.addEventListener('click', addSubjectHandler);
    
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

    // Debug: Log all clicks on the form
    document.querySelector('form').addEventListener('click', function(event) {
    });

});
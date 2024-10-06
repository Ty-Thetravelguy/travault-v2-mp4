document.addEventListener('DOMContentLoaded', function() {
    // Category field functionality
    var categoryTypeField = document.getElementById('id_category_type');
    var categoryField = document.getElementById('id_category');

    if (!categoryTypeField || !categoryField) {
        console.error('Category Type or Category field not found.');
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

    // New code for subject field autocomplete
    var subjectField = document.getElementById('id_subject');
    var subjectSuggestions = document.getElementById('subject_suggestions');
    var addSubjectButton = document.getElementById('add_subject');

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
                        subjectSuggestions.innerHTML = '';
                    });
                    subjectSuggestions.appendChild(item);
                });
            });
    }

    addSubjectButton.addEventListener('click', function() {
        var newSubject = subjectField.value.trim();
        if (newSubject) {
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
                subjectSuggestions.innerHTML = '';
                alert('New subject added successfully!');
            });
        }
    });
});
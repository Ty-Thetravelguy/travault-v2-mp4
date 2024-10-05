document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');

    var categoryTypeField = document.getElementById('id_category_type');
    var categoryField = document.getElementById('id_category');

    console.log('Category Type Field:', categoryTypeField);
    console.log('Category Field:', categoryField);

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
                {value: 'complaint', text: 'Complaint'},
                {value: 'query', text: 'Query'},
                {value: 'request', text: 'Request'}
            ]);
        } else if (selectedCategoryType === 'agency') {
            categoryField.removeAttribute('disabled'); // Enable the dropdown
            populateOptions([
                {value: 'consultant_error', text: 'Consultant Error'},
                {value: 'supplier_error', text: 'Supplier Error'},
                {value: 'supplier_query', text: 'Supplier Query'},
                {value: 'system_error', text: 'System Error'},
                {value: 'system_query', text: 'System Query'},
                {value: 'system_enhancement', text: 'System Enhancement'}
            ]);
        } else {
            // If no valid category type is selected, disable the category field
            categoryField.setAttribute('disabled', 'disabled');
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
});

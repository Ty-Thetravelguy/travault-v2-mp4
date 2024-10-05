document.addEventListener('DOMContentLoaded', function() {
    // Get references to the select elements
    var categoryTypeField = document.getElementById('id_category_type');
    var categoryField = document.getElementById('id_category');

    // Function to enable and populate the category field based on category type
    function updateCategoryField() {
        var selectedCategoryType = categoryTypeField.value;

        // Reset the category options
        categoryField.innerHTML = '';  // Clear current options
        categoryField.disabled = true;  // Disable until options are loaded

        // Populate based on the selected type
        if (selectedCategoryType === 'client') {
            categoryField.disabled = false;
            categoryField.innerHTML = `
                <option value="complaint">Complaint</option>
                <option value="query">Query</option>
                <option value="request">Request</option>
            `;
        } else if (selectedCategoryType === 'agency') {
            categoryField.disabled = false;
            categoryField.innerHTML = `
                <option value="consultant_error">Consultant Error</option>
                <option value="supplier_error">Supplier Error</option>
                <option value="supplier_query">Supplier Query</option>
                <option value="system_error">System Error</option>
                <option value="system_query">System Query</option>
                <option value="system_enhancement">System Enhancement</option>
            `;
        }
    }

    // Event listener to update the category field when category type changes
    categoryTypeField.addEventListener('change', updateCategoryField);

    // Initialize on page load
    updateCategoryField();
});

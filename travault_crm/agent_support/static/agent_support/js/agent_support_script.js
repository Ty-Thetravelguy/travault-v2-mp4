// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    const supplierNameFilter = document.getElementById('supplierNameFilter');
    const supplierTypeFilter = document.getElementById('supplierTypeFilter');
    const supplierItems = document.querySelectorAll('.supplier-item');

    function normalizeText(text) {
        return text
            .toLowerCase()
            .replace(/[|\/\-]/g, ' ') // Replace special characters with space
            .replace(/\s+/g, ' ')     // Replace multiple spaces with a single space
            .trim();
    }

    function filterSuppliers() {
        const nameFilterValue = normalizeText(supplierNameFilter.value);
        const typeFilterValue = supplierTypeFilter.value; 
        console.log('Type filter value:', typeFilterValue);

        supplierItems.forEach(function(item) {
            const supplierNameRaw = item.getAttribute('data-supplier-name');
            const supplierType = item.getAttribute('data-supplier-type');
            console.log('Supplier type:', supplierType);

            const supplierName = normalizeText(supplierNameRaw);
    
            const nameMatches = nameFilterValue.split(' ').every(function(term) {
                return supplierName.includes(term);
            });
    
            const typeMatches = !typeFilterValue || supplierType === typeFilterValue;
    
            if (nameMatches && typeMatches) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }
    // Event listeners for input and change events
    supplierNameFilter.addEventListener('input', filterSuppliers);
    supplierTypeFilter.addEventListener('change', filterSuppliers);

    // Initial filter on page load
    filterSuppliers();
});
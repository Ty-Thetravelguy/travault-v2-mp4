document.addEventListener('DOMContentLoaded', function() {
    const fetchDataBtn = document.getElementById('fetchDataBtn');
    const companyModal = new bootstrap.Modal(document.getElementById('companyModal'));
    const loadingSpinner = document.getElementById('loading-spinner');

    function showLoadingSpinner() {
        loadingSpinner.style.display = 'flex';
    }

    function hideLoadingSpinner() {
        loadingSpinner.style.display = 'none';
    }

    fetchDataBtn.addEventListener('click', function() {
        let website = document.getElementById('companyWebsiteInput').value.trim();
        
        if (!website.startsWith('http://') && !website.startsWith('https://')) {
            website = 'https://' + website;
        }

        showLoadingSpinner();
        companyModal.hide();

        fetch(`/crm/fetch-company-data/?website=${encodeURIComponent(website)}`)
            .then(response => {
                return response.json().then(data => {
                    if (!response.ok) {
                        throw new Error(data.error || 'Unknown error occurred');
                    }
                    return data;
                });
            })
            .then(data => {
                // Combine address components
                const street = data.street || '';
                const city = data.city || '';
                const country = data.country || '';
                const postcode = (data.postcode || '').toUpperCase();  
                const fullAddress = [street, city, country, postcode].filter(Boolean).join(', ');
                
                // Populate the fields
                const fields = [
                    { name: 'company_name', type: 'input' },
                    { name: 'company_address', type: 'input', value: fullAddress },
                    { name: 'email', type: 'input' },
                    { name: 'industry', type: 'select' },
                    { name: 'description', type: 'textarea' },
                    { name: 'linkedin_social_page', type: 'input' },
                ];

                fields.forEach(field => {
                    const element = document.querySelector(`${field.type}[name="${field.name}"]`);
                    if (element) {
                        const value = field.value || data[field.name] || '';
                        element.value = value;
                    }
                });
            })
            .catch(error => {
                alert(`Error: ${error.message || 'An unexpected error occurred. Please try again.'}`);
            })
            .finally(() => {
                hideLoadingSpinner();
            });
    });
});
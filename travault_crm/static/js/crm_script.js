document.addEventListener('DOMContentLoaded', function() {
    const fetchDataBtn = document.getElementById('fetchDataBtn');
    const companyModal = new bootstrap.Modal(document.getElementById('companyModal'));

    fetchDataBtn.addEventListener('click', function() {
        const website = document.getElementById('companyWebsiteInput').value;
        fetch(`/crm/fetch-company-data/?website=${encodeURIComponent(website)}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    // Populate form fields with data from API
                    document.querySelector('input[name="company_name"]').value = data.company_name || '';
                    document.querySelector('input[name="address"]').value = data.address || '';
                    document.querySelector('input[name="email"]').value = data.email || '';
                    document.querySelector('select[name="industry"]').value = data.industry || '';
                    document.querySelector('textarea[name="description"]').value = data.description || '';
                    document.querySelector('input[name="linkedin_social_page"]').value = data.linkedin_social_page || '';
                }
                // Close modal
                companyModal.hide();
            })
            .catch(error => console.error('Error fetching company data:', error));
    });
});

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
                    { name: 'phone_number', type: 'input' },
                    { name: 'description', type: 'textarea' },
                    { name: 'linkedin_social_page', type: 'input' },
                ];

                fields.forEach(field => {
                    const element = document.querySelector(`${field.type}[name="${field.name}"]`);
                    if (element) {
                        let value = field.value || data[field.name] || '';
            
                        // Ensure LinkedIn URL starts with 'https://'
                        if (field.name === 'linkedin_social_page' && value && !value.startsWith('http://') && !value.startsWith('https://')) {
                            value = 'https://' + value;
                        }
            
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

    // linked companies search functionality
    const linkedCompaniesSearch = document.getElementById('linked-companies-search');
    const linkedCompaniesSelect = document.querySelector('select[name="linked_companies"]');
    const linkedCompaniesResults = document.getElementById('linked-companies-results');
    const selectedCompaniesContainer = document.getElementById('selected-companies');

    function updateSelectedCompanies() {
        selectedCompaniesContainer.innerHTML = '';
        Array.from(linkedCompaniesSelect.selectedOptions).forEach(option => {
            const chip = document.createElement('span');
            chip.className = 'badge me-2 mb-2 selected-company-badge';
            chip.style.backgroundColor = '#001f3f';
            chip.style.color = 'white';
            chip.style.padding = '0.5em 0.7em';
            chip.style.display = 'inline-flex';
            chip.style.alignItems = 'center';
            chip.style.borderRadius = '4px';
            
            const companyName = document.createElement('span');
            companyName.textContent = option.textContent;
            companyName.style.marginRight = '0.5em';
            
            const closeButton = document.createElement('button');
            closeButton.innerHTML = '&times;';
            closeButton.className = 'btn-close-custom';
            closeButton.setAttribute('aria-label', 'Remove');
            
            closeButton.addEventListener('click', (e) => {
                e.preventDefault();
                option.selected = false;
                updateSelectedCompanies();
            });
            
            chip.appendChild(companyName);
            chip.appendChild(closeButton);
            selectedCompaniesContainer.appendChild(chip);
        });
    }

    function addCompany(id, name) {
        let option = linkedCompaniesSelect.querySelector(`option[value="${id}"]`);
        if (!option) {
            option = document.createElement('option');
            option.value = id;
            option.textContent = name;
            linkedCompaniesSelect.appendChild(option);
        }
        option.selected = true;
        updateSelectedCompanies();
    }

    if (linkedCompaniesSearch && linkedCompaniesSelect && linkedCompaniesResults) {
        const searchCompanies = (query) => {
            return fetch(`/crm/search-companies/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => data.results);
        };

        const createResultItem = (company) => {
            const item = document.createElement('div');
            item.className = 'linked-company-result';
            item.textContent = company.text;
            item.dataset.id = company.id;
            item.style.cursor = 'pointer';
            item.addEventListener('click', () => {
                addCompany(company.id, company.text);
                linkedCompaniesSearch.value = '';
                linkedCompaniesResults.innerHTML = '';
                
                // Visual feedback
                item.style.backgroundColor = '#e0e0e0';
                setTimeout(() => {
                    item.style.backgroundColor = '';
                }, 200);
            });
            return item;
        };

        const debounce = (func, delay) => {
            let timeoutId;
            return (...args) => {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => func(...args), delay);
            };
        };

        linkedCompaniesSearch.addEventListener('input', debounce((event) => {
            const query = event.target.value;
            if (query.length >= 2) {
                searchCompanies(query).then(companies => {
                    linkedCompaniesResults.innerHTML = '';
                    companies.forEach(company => {
                        linkedCompaniesResults.appendChild(createResultItem(company));
                    });
                });
            } else {
                linkedCompaniesResults.innerHTML = '';
            }
        }, 250));

        // Initial update of selected companies
        updateSelectedCompanies();
    }
});
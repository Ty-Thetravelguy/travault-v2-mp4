document.addEventListener('DOMContentLoaded', function() {
    
    const fetchDataBtn = document.getElementById('fetchDataBtn');
    const companyModal = document.getElementById('companyModal') ? new bootstrap.Modal(document.getElementById('companyModal')) : null;
    const loadingSpinner = document.getElementById('loading-spinner');

    function showLoadingSpinner() {
        if (loadingSpinner) loadingSpinner.style.display = 'flex';
    }

    function hideLoadingSpinner() {
        if (loadingSpinner) loadingSpinner.style.display = 'none';
    }

    if (fetchDataBtn && companyModal) {
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
                    // Populate the fields
                    const fields = [
                        { name: 'company_name', type: 'input' },
                        { name: 'street_address', type: 'input' },
                        { name: 'city', type: 'input' },
                        { name: 'state_province', type: 'input' },
                        { name: 'postal_code', type: 'input' },
                        { name: 'country', type: 'input' },
                        { name: 'phone_number', type: 'input' },
                        { name: 'email', type: 'input' },
                        { name: 'description', type: 'textarea' },
                        { name: 'linkedin_social_page', type: 'input' },
                    ];

                    fields.forEach(field => {
                        const element = document.querySelector(`${field.type}[name="${field.name}"]`);
                        if (element) {
                            let value = data[field.name] || '';
                
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
    }

    // Linked companies search functionality
    const linkedCompaniesSearch = document.getElementById('linked-companies-search');
    const linkedCompaniesSelect = document.querySelector('select[name="linked_companies"]');
    const linkedCompaniesResults = document.getElementById('linked-companies-results');
    const selectedCompaniesContainer = document.getElementById('selected-companies');

    if (!linkedCompaniesSearch || !linkedCompaniesSelect || !linkedCompaniesResults || !selectedCompaniesContainer) {
        return;
    }

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
});


document.addEventListener('DOMContentLoaded', function() {
    const companyNameFilter = document.getElementById('companyNameFilter');
    const companyTypeFilter = document.getElementById('companyType');
    const companyOwnerFilter = document.getElementById('companyOwnerFilter');
    const tableBody = document.querySelector('.table tbody');
    const originalRows = Array.from(tableBody.querySelectorAll('tr'));

    function filterTable() {
        const nameFilter = companyNameFilter.value.toLowerCase();
        const typeFilter = companyTypeFilter.value;
        const ownerFilter = companyOwnerFilter.value;

        originalRows.forEach(row => {
            const name = row.cells[0].textContent.toLowerCase();
            const owner = row.cells[1].textContent;
            const type = row.cells[7].textContent;

            const nameMatch = name.includes(nameFilter);
            const typeMatch = !typeFilter || type === typeFilter;
            const ownerMatch = !ownerFilter || owner === ownerFilter;

            if (nameMatch && typeMatch && ownerMatch) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    if (companyNameFilter) {
        companyNameFilter.addEventListener('input', filterTable);
    }

    if (companyTypeFilter) {
        companyTypeFilter.addEventListener('change', filterTable);
    }

    if (companyOwnerFilter) {
        companyOwnerFilter.addEventListener('change', filterTable);
    }

    // Sorting functionality
    const headers = document.querySelectorAll('th');
    headers.forEach(header => {
        header.addEventListener('click', () => {
            const index = Array.from(header.parentElement.children).indexOf(header);
            const ascending = header.classList.contains('asc');
            
            sortTable(index, !ascending);
            
            headers.forEach(h => h.classList.remove('asc', 'desc'));
            header.classList.add(ascending ? 'desc' : 'asc');
        });
    });

    function sortTable(column, asc = true) {
        const rows = Array.from(tableBody.querySelectorAll('tr:not([style*="display: none"])'));
        const sortedRows = rows.sort((a, b) => {
            const aColText = a.querySelector(`td:nth-child(${column + 1})`).textContent.trim();
            const bColText = b.querySelector(`td:nth-child(${column + 1})`).textContent.trim();
            return asc ? aColText.localeCompare(bColText) : bColText.localeCompare(aColText);
        });

        while (tableBody.firstChild) {
            tableBody.removeChild(tableBody.firstChild);
        }

        tableBody.append(...sortedRows);
    }
});

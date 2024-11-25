document.addEventListener('DOMContentLoaded', function() {
    // Elements related to fetching company data
    const fetchDataBtn = document.getElementById('fetchDataBtn');
    const companyModal = document.getElementById('companyModal') ? new bootstrap.Modal(document.getElementById('companyModal')) : null;
    const loadingSpinner = document.getElementById('loading-spinner');

    /**
     * Shows the loading spinner when data is being fetched.
     */
    function showLoadingSpinner() {
        if (loadingSpinner) loadingSpinner.style.display = 'flex';
    }

    /**
     * Hides the loading spinner after data fetch is complete.
     */
    function hideLoadingSpinner() {
        if (loadingSpinner) loadingSpinner.style.display = 'none';
    }

    // Fetch company data and populate form fields when the button is clicked
    if (fetchDataBtn && companyModal) {
        fetchDataBtn.addEventListener('click', function() {
            // Retrieve and format the website URL
            let website = document.getElementById('companyWebsiteInput').value.trim();
            if (!website.startsWith('http://') && !website.startsWith('https://')) {
                website = 'https://' + website;
            }

            showLoadingSpinner(); // Show spinner while fetching data
            companyModal.hide();  // Hide the modal during the fetch

            // Fetch data from the server
            fetch(`/crm/fetch-company-data/?website=${encodeURIComponent(website)}`)
                .then(response => {
                    // Parse the JSON response
                    return response.json().then(data => {
                        if (!response.ok) {
                            throw new Error(data.error || 'Unknown error occurred');
                        }
                        return data;
                    });
                })
                .then(data => {
                    // Define fields to be populated with data
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

                    // Populate each field with the corresponding data
                    fields.forEach(field => {
                        const element = document.querySelector(`${field.type}[name="${field.name}"]`);
                        if (element) {
                            let value = data[field.name] || '';

                            // Ensure LinkedIn URLs start with 'https://'
                            if (field.name === 'linkedin_social_page' && value && !value.startsWith('http://') && !value.startsWith('https://')) {
                                value = 'https://' + value;
                            }

                            element.value = value; // Set the value of the field
                        }
                    });
                })
                .catch(error => {
                    // Alert the user in case of errors
                    alert(`Error: ${error.message || 'An unexpected error occurred. Please try again.'}`);
                })
                .finally(() => {
                    hideLoadingSpinner(); // Hide spinner after operation completes
                });
        });
    }

    // Elements and functions related to managing linked companies
    const linkedCompaniesSearch = document.getElementById('linked-companies-search');
    const linkedCompaniesSelect = document.querySelector('select[name="linked_companies"]');
    const linkedCompaniesResults = document.getElementById('linked-companies-results');
    const selectedCompaniesContainer = document.getElementById('selected-companies');

    // Ensure all necessary elements are present before proceeding
    if (!linkedCompaniesSearch || !linkedCompaniesSelect || !linkedCompaniesResults || !selectedCompaniesContainer) {
        return; // Exit if any elements are missing
    }

    /**
     * Updates the display of selected companies as badges.
     */
    function updateSelectedCompanies() {
        selectedCompaniesContainer.innerHTML = '';
        Array.from(linkedCompaniesSelect.selectedOptions).forEach(option => {
            // Create a badge for each selected company
            const chip = document.createElement('span');
            chip.className = 'badge me-2 mb-2 selected-company-badge';
            chip.style.backgroundColor = '#001f3f';
            chip.style.color = 'white';
            chip.style.padding = '0.5em 0.7em';
            chip.style.display = 'inline-flex';
            chip.style.alignItems = 'center';
            chip.style.borderRadius = '4px';

            // Add company name and remove button
            const companyName = document.createElement('span');
            companyName.textContent = option.textContent;
            companyName.style.marginRight = '0.5em';

            const closeButton = document.createElement('button');
            closeButton.innerHTML = '&times;';
            closeButton.className = 'btn-close-custom';
            closeButton.setAttribute('aria-label', 'Remove');

            // Remove the company from selection on button click
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

    /**
     * Adds a company to the selection.
     * @param {string} id - The ID of the company.
     * @param {string} name - The name of the company.
     */
    function addCompany(id, name) {
        let option = linkedCompaniesSelect.querySelector(`option[value="${id}"]`);
        if (!option) {
            // Create a new option if it doesn't exist
            option = document.createElement('option');
            option.value = id;
            option.textContent = name;
            linkedCompaniesSelect.appendChild(option);
        }
        option.selected = true; // Select the company
        updateSelectedCompanies(); // Update display
    }

    /**
     * Searches for companies matching the query.
     * @param {string} query - The search query.
     * @returns {Promise<Array>} A promise resolving to a list of matching companies.
     */
    const searchCompanies = (query) => {
        return fetch(`/crm/search-companies/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => data.results);
    };

    /**
     * Creates a clickable result item for each company found.
     * @param {Object} company - The company data.
     * @returns {HTMLElement} The result item element.
     */
    const createResultItem = (company) => {
        const item = document.createElement('div');
        item.className = 'linked-company-result';
        item.textContent = company.text;
        item.dataset.id = company.id;
        item.style.cursor = 'pointer';

        // Add click event to add the company
        item.addEventListener('click', () => {
            addCompany(company.id, company.text);
            linkedCompaniesSearch.value = ''; // Clear search input
            linkedCompaniesResults.innerHTML = ''; // Clear search results

            // Visual feedback for adding the company
            item.style.backgroundColor = '#e0e0e0';
            setTimeout(() => {
                item.style.backgroundColor = '';
            }, 200);
        });
        return item;
    };

    /**
     * Debounces function execution to limit how often it runs.
     * @param {Function} func - The function to debounce.
     * @param {number} delay - The delay in milliseconds.
     * @returns {Function} A debounced version of the function.
     */
    const debounce = (func, delay) => {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func(...args), delay);
        };
    };

    // Add input listener to the search field with debounce
    linkedCompaniesSearch.addEventListener('input', debounce((event) => {
        const query = event.target.value;
        if (query.length >= 2) {
            // Search for companies if the query length is sufficient
            searchCompanies(query).then(companies => {
                linkedCompaniesResults.innerHTML = '';
                companies.forEach(company => {
                    linkedCompaniesResults.appendChild(createResultItem(company));
                });
            });
        } else {
            linkedCompaniesResults.innerHTML = ''; // Clear results if query is too short
        }
    }, 250));

    // Initial update of selected companies display
    updateSelectedCompanies();
});

document.addEventListener('DOMContentLoaded', function() {
    // Filters for companies on a table
    const companyNameFilter = document.getElementById('companyNameFilter');
    const companyTypeFilter = document.getElementById('companyType');
    const companyOwnerFilter = document.getElementById('companyOwnerFilter');
    const tableBody = document.querySelector('.table tbody');
    const originalRows = Array.from(tableBody.querySelectorAll('tr'));

    /**
     * Filters the table rows based on filter input values.
     */
    function filterTable() {
        const nameFilter = companyNameFilter.value.toLowerCase();
        const typeFilter = companyTypeFilter.value;
        const ownerFilter = companyOwnerFilter.value;

        originalRows.forEach(row => {
            const name = row.cells[0].textContent.toLowerCase();
            const owner = row.cells[1].textContent;
            const type = row.cells[7].textContent;

            // Check if each row matches the current filters
            const nameMatch = name.includes(nameFilter);
            const typeMatch = !typeFilter || type === typeFilter;
            const ownerMatch = !ownerFilter || owner === ownerFilter;

            // Show or hide rows based on match status
            if (nameMatch && typeMatch && ownerMatch) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    // Add event listeners for each filter input
    if (companyNameFilter) {
        companyNameFilter.addEventListener('input', filterTable);
    }

    if (companyTypeFilter) {
        companyTypeFilter.addEventListener('change', filterTable);
    }

    if (companyOwnerFilter) {
        companyOwnerFilter.addEventListener('change', filterTable);
    }

    // Sorting functionality for the table
    const headers = document.querySelectorAll('th');
    headers.forEach(header => {
        header.addEventListener('click', () => {
            const index = Array.from(header.parentElement.children).indexOf(header);
            const ascending = header.classList.contains('asc');
            
            // Sort the table by the selected column
            sortTable(index, !ascending);
            
            // Update sort direction indicators
            headers.forEach(h => h.classList.remove('asc', 'desc'));
            header.classList.add(ascending ? 'desc' : 'asc');
        });
    });

    /**
     * Sorts the table rows based on the selected column.
     * @param {number} column - The index of the column to sort by.
     * @param {boolean} asc - Whether to sort in ascending order.
     */
    function sortTable(column, asc = true) {
        // Get all visible rows for sorting
        const rows = Array.from(tableBody.querySelectorAll('tr:not([style*="display: none"])'));
        const sortedRows = rows.sort((a, b) => {
            const aColText = a.querySelector(`td:nth-child(${column + 1})`).textContent.trim();
            const bColText = b.querySelector(`td:nth-child(${column + 1})`).textContent.trim();
            // Compare text content of the cells
            return asc ? aColText.localeCompare(bColText) : bColText.localeCompare(aColText);
        });

        // Remove existing rows and append sorted rows
        while (tableBody.firstChild) {
            tableBody.removeChild(tableBody.firstChild);
        }

        tableBody.append(...sortedRows);
    }
});

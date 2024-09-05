document.addEventListener("DOMContentLoaded", function() {
    // Show the modal when the page loads
    var websiteModal = new bootstrap.Modal(document.getElementById('websiteModal'), {});
    websiteModal.show();

    // Handle fetching data from Diffbot
    document.getElementById('fetchDataButton').addEventListener('click', function() {
        var website = document.getElementById('companyWebsite').value;
        if (website) {
            fetch(`/fetch-company-data/?website=${encodeURIComponent(website)}`)
                .then(response => response.json())
                .then(data => {
                    // Prepopulate form fields with API data
                    document.getElementById('companyName').value = data.name || '';
                    document.getElementById('companyAddress').value = data.address || '';
                    document.getElementById('companyEmail').value = data.email || '';
                    document.getElementById('description').value = data.description || '';
                    document.getElementById('linkedin').value = data.linkedin || '';
                    // Close the modal
                    websiteModal.hide();
                })
                .catch(error => console.error('Error fetching data:', error));
        }
    });
});
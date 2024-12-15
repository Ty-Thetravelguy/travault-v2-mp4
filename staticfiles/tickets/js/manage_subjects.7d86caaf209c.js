document.addEventListener('DOMContentLoaded', function() {
    const addNewSubjectButton = document.getElementById('addNewSubjectButton');
    const newSubjectInput = document.getElementById('newSubjectInput');
    const editSubjectModal = document.getElementById('editSubjectModal');
    const editSubjectInput = document.getElementById('editSubjectInput');
    const saveSubjectChangesButton = document.getElementById('saveSubjectChangesButton');
    const confirmDeleteModal = document.getElementById('confirmDeleteModal');
    const confirmDeleteButton = document.getElementById('confirmDeleteButton');
    let currentSubjectId = null;

    // Add new subject
    addNewSubjectButton.addEventListener('click', function() {
        const newSubject = newSubjectInput.value.trim();
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
                if (data.redirect) {
                    // If you want to use the subject info before redirecting, you can do so here
                    console.log(`Subject ${data.created ? 'created' : 'already exists'}: ${data.subject} (ID: ${data.id})`);
                    
                    // Redirect to refresh the page and show Django messages
                    window.location.href = data.redirect;
                } else if (data.error) {
                    alert(data.error);
                }
            })
            .catch(error => console.error('Error adding subject:', error));
        }
    });

    // Open edit modal
    editSubjectModal.addEventListener('show.bs.modal', function(event) {
        const button = event.relatedTarget;
        currentSubjectId = button.getAttribute('data-subject-id');
        const subjectName = button.getAttribute('data-subject-name');
        editSubjectInput.value = subjectName;
    });

    // Save changes to subject
    saveSubjectChangesButton.addEventListener('click', function() {
        const updatedSubject = editSubjectInput.value.trim();
        if (updatedSubject && currentSubjectId) {
            fetch(`/tickets/update-subject/${currentSubjectId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: `subject=${encodeURIComponent(updatedSubject)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload(); // Reload the page to update the list
                } 
            })
            .catch(error => console.error('Error updating subject:', error));
        }
    });

    // Confirm delete subject
    confirmDeleteButton.addEventListener('click', function() {
        if (currentSubjectId) {
            // Get the CSRF token from within the modal
            const csrfToken = confirmDeleteModal.querySelector('[name=csrfmiddlewaretoken]');
            
            if (!csrfToken) {
                console.error('CSRF token not found in the modal');
                return;
            }

            fetch(`/tickets/delete-subject/${currentSubjectId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken.value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload(); // Reload the page to update the list and show success message
                } else {
                    // Display the error message
                    alert(data.error || 'Error deleting subject.');
                    // Close the modal
                    const modal = bootstrap.Modal.getInstance(confirmDeleteModal);
                    modal.hide();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An unexpected error occurred while deleting the subject.');
                // Close the modal
                const modal = bootstrap.Modal.getInstance(confirmDeleteModal);
                modal.hide();
            });
        } 
    });

    // Open confirm delete modal
    confirmDeleteModal.addEventListener('show.bs.modal', function(event) {
        const button = event.relatedTarget;
        currentSubjectId = button.getAttribute('data-subject-id');
    });
});
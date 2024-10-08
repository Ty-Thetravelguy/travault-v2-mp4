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
                if (data.created) {
                    alert(`New subject '${data.subject}' added successfully!`);
                    location.reload(); // Reload the page to update the list
                } else {
                    alert(`Subject '${data.subject}' already exists.`);
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
                    alert('Subject updated successfully!');
                    location.reload(); // Reload the page to update the list
                } else {
                    alert('Error updating subject.');
                }
            })
            .catch(error => console.error('Error updating subject:', error));
        }
    });

    // Confirm delete subject
    confirmDeleteButton.addEventListener('click', function() {
        console.log('Confirm delete button clicked');
        console.log('Current subject ID:', currentSubjectId);
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
                    alert('Subject deleted successfully!');
                    location.reload(); // Reload the page to update the list
                } else {
                    alert('Error deleting subject.');
                }
            })
            .catch(error => {
                console.error('Error deleting subject:', error);
                alert('An error occurred while deleting the subject.');
            });
        } else {
            console.error('No subject ID provided');
        }
    });

    // Open confirm delete modal
    confirmDeleteModal.addEventListener('show.bs.modal', function(event) {
        const button = event.relatedTarget;
        currentSubjectId = button.getAttribute('data-subject-id');
        console.log('Preparing to delete subject with ID:', currentSubjectId);
    });
});
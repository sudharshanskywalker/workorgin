function showNotification(message, type = 'success') {
    const container = document.getElementById('notifications-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `notification-toast notification-${type}`;

    // Select icon based on type
    let iconName = 'check-circle';
    let iconColor = '#22c55e';

    if (type === 'error') {
        iconName = 'alert-circle';
        iconColor = '#ef4444';
    } else if (type === 'info') {
        iconName = 'info';
        iconColor = '#0284c7';
    }

    toast.innerHTML = `
        <i data-lucide="${iconName}" style="color: ${iconColor}"></i>
        <div style="flex: 1;">${message}</div>
    `;

    container.appendChild(toast);

    // Initialize icons for the new element
    if (window.lucide) {
        window.lucide.createIcons();
    }

    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function handleBooking(isLoggedIn, workerName, workerId) {
    if (isLoggedIn) {
        // Record booking in backend
        const formData = new FormData();
        formData.append('worker_id', workerId);

        fetch('/book_pro', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(`Booking request sent to ${workerName}! They will contact you shortly.`, 'success');
                } else {
                    showNotification(`Error: ${data.message}`, 'error');
                }
            })
            .catch(err => {
                console.error('Booking error:', err);
                showNotification('Failed to process booking. Please try again.', 'error');
            });
    } else {
        showNotification('Please log in to book a professional.', 'error');
        // Briefly wait then redirect to login
        setTimeout(() => {
            window.location.href = '/login?next=' + window.location.pathname;
        }, 1500);
    }
}

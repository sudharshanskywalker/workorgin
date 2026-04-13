function previewImage(event) {
    const input = event.target;
    const reader = new FileReader();
    
    reader.onload = function() {
        let previewContainer = document.getElementById('image-preview-container');
        
        // Create preview container if it doesn't exist
        if (!previewContainer) {
            previewContainer = document.createElement('div');
            previewContainer.id = 'image-preview-container';
            previewContainer.style.marginTop = '1rem';
            previewContainer.style.textAlign = 'center';
            input.parentNode.appendChild(previewContainer);
        }
        
        // Update preview content
        previewContainer.innerHTML = `
            <p class="form-label" style="margin-bottom: 0.5rem;">Image Preview:</p>
            <img src="${reader.result}" style="max-width: 100%; height: auto; border-radius: 0.5rem; border: 1px solid var(--gray-200); box-shadow: var(--shadow-sm);" />
        `;
    };
    
    if (input.files && input.files[0]) {
        reader.readAsDataURL(input.files[0]);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // ---- UI and Initialization ---- 
    setupDragAndDrop('encodeUploadArea', 'encodeImage', 'encodePreview');
    setupDragAndDrop('decodeUploadArea', 'decodeImage', 'decodePreview');

    // ---- Encode Form Handling ----
    const encodeForm = document.getElementById('encodeForm');
    encodeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const btn = document.getElementById('encodeBtn');
        const alert = document.getElementById('encodeAlert');
        
        // Setup UI for loading
        setLoading(btn, true);
        alert.classList.add('d-none');
        
        try {
            const formData = new FormData(encodeForm);
            
            const response = await fetch('/api/encode', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                // Handle file download
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                
                // Keep the original name base if we can, else generic
                const originalFile = document.getElementById('encodeImage').files[0];
                const originalName = originalFile?.name || 'encoded';
                const isImage = originalFile?.type.startsWith('image/');
                
                const ext = originalName.lastIndexOf('.');
                const baseName = ext !== -1 ? originalName.substring(0, ext) : originalName;
                const origExt = ext !== -1 ? originalName.substring(ext) : '.png';
                
                // Images always save as .png to prevent data loss. Other files keep their extension.
                const targetExt = isImage ? '.png' : origExt;
                
                a.download = `${baseName}_encoded${targetExt}`;
                
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
                
                showAlert(alert, 'success', 'Image encoded successfully! Download started.');
                encodeForm.reset();
                resetPreview('encodeUploadArea', 'encodePreview');
            } else {
                const errorData = await response.json();
                showAlert(alert, 'danger', errorData.error || 'An error occurred during encoding.');
            }
        } catch (error) {
            showAlert(alert, 'danger', 'Failed to communicate with the server.');
        } finally {
            setLoading(btn, false);
        }
    });

    // ---- Decode Form Handling ----
    const decodeForm = document.getElementById('decodeForm');
    decodeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const btn = document.getElementById('decodeBtn');
        const alert = document.getElementById('decodeAlert');
        const resultArea = document.getElementById('resultArea');
        const extractedMsgElement = document.getElementById('extractedMessage');
        
        // Setup UI for loading
        setLoading(btn, true);
        alert.classList.add('d-none');
        resultArea.classList.add('d-none');
        extractedMsgElement.textContent = '';
        
        try {
            const formData = new FormData(decodeForm);
            
            const response = await fetch('/api/decode', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                resultArea.classList.remove('d-none');
                extractedMsgElement.textContent = data.message;
            } else {
                showAlert(alert, 'danger', data.error || 'An error occurred during decoding.');
            }
        } catch (error) {
            showAlert(alert, 'danger', 'Failed to communicate with the server.');
        } finally {
            setLoading(btn, false);
        }
    });
    
    // ---- Helper Functions ----

    function setupDragAndDrop(areaId, inputId, previewId) {
        const dropArea = document.getElementById(areaId);
        const fileInput = document.getElementById(inputId);
        const preview = document.getElementById(previewId);

        // Click to open file dialog
        dropArea.addEventListener('click', () => fileInput.click());

        // File Selection Changed
        fileInput.addEventListener('change', function() {
            handleFiles(this.files, dropArea, preview);
        });

        // Drag events
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => dropArea.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => dropArea.classList.remove('dragover'), false);
        });

        dropArea.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                // Update file input with dropped files
                fileInput.files = dt.files;
                handleFiles(files, dropArea, preview);
            }
        }, false);
    }

    function handleFiles(files, dropArea, preview) {
        if (files.length === 0) return;
        const file = files[0];
        
        const icon = dropArea.querySelector('.upload-icon');
        const text = dropArea.querySelector('.preview-text');
        
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => {
                preview.src = reader.result;
                preview.classList.remove('d-none');
                
                if(icon) icon.classList.add('d-none');
                if(text) text.classList.add('d-none');
                
                const docPreview = dropArea.querySelector('.doc-preview');
                if(docPreview) docPreview.remove();
            };
        } else {
            // Document or Video preview
            preview.classList.add('d-none');
            if(icon) icon.classList.add('d-none');
            if(text) text.classList.add('d-none');
            
            const existingDoc = dropArea.querySelector('.doc-preview');
            if(existingDoc) existingDoc.remove();
            
            let iconClass = 'bi-file-earmark-text-fill';
            if(file.type.startsWith('video/')) iconClass = 'bi-camera-video-fill';
            else if(file.type.includes('pdf')) iconClass = 'bi-file-earmark-pdf-fill';
            
            dropArea.insertAdjacentHTML('beforeend', `
                <div class="doc-preview text-center w-100 d-flex flex-column align-items-center justify-content-center">
                    <i class="bi ${iconClass} display-3 text-primary mb-3"></i>
                    <h5 class="outfit-font text-white mb-2 text-truncate" style="max-width: 90%;">${file.name}</h5>
                    <small class="text-muted bg-dark px-2 py-1 rounded border border-secondary">${(file.size / (1024*1024)).toFixed(2)} MB</small>
                </div>
            `);
        }
    }

    function resetPreview(areaId, previewId) {
        const dropArea = document.getElementById(areaId);
        const preview = document.getElementById(previewId);
        
        preview.src = '';
        preview.classList.add('d-none');
        
        const docPreview = dropArea.querySelector('.doc-preview');
        if(docPreview) docPreview.remove();
        
        const icon = dropArea.querySelector('.upload-icon');
        const text = dropArea.querySelector('.preview-text');
        if(icon) icon.classList.remove('d-none');
        if(text) text.classList.remove('d-none');
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function setLoading(btnConfig, isLoading) {
        const spinner = btnConfig.querySelector('.spinner-border');
        const btnText = btnConfig.querySelector('.btn-text');
        
        if (isLoading) {
            btnConfig.disabled = true;
            spinner.classList.remove('d-none');
            btnText.classList.add('opacity-50');
        } else {
            btnConfig.disabled = false;
            spinner.classList.add('d-none');
            btnText.classList.remove('opacity-50');
        }
    }

    function showAlert(alertElement, type, message) {
        alertElement.className = `alert alert-${type} mt-3 mb-0`;
        alertElement.textContent = message;
        alertElement.classList.remove('d-none');
    }
});

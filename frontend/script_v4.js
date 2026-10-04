document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('convertForm');
    const conversionType = document.getElementById('conversionType');
    const targetSizeContainer = document.getElementById('targetSizeContainer');
    const fileInput = document.getElementById('fileInput');
    const dropZone = document.getElementById('dropZone');
    
    const previewSection = document.getElementById('previewSection');
    const fileListContainer = document.getElementById('fileListContainer');
    const fileCountBadge = document.getElementById('fileCountBadge');
    
    const qualitySlider = document.getElementById('qualitySlider');
    const qualityValue = document.getElementById('qualityValue');

    const resizeWidth = document.getElementById('resizeWidth');
    const resizeHeight = document.getElementById('resizeHeight');
    const lockAspectRatio = document.getElementById('lockAspectRatio');
    
    const resultSubtitle = document.getElementById('resultSubtitle');
    const progressText = document.getElementById('progressText');

    let selectedFiles = [];
    let originalAspectRatio = null;
    let totalOriginalBytes = 0;

    // Backend Health Check
    const convertBtn = document.getElementById('convertBtn');
    if (convertBtn) {
        const originalBtnHTML = convertBtn.innerHTML;
        convertBtn.disabled = true;
        convertBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span> Server connecting...';
        
        const checkHealth = async () => {
            try {
                const res = await fetch('/api/health');
                if (res.ok) {
                    convertBtn.disabled = false;
                    convertBtn.innerHTML = originalBtnHTML;
                    return true;
                }
            } catch(e) {}
            return false;
        };

        const pollHealth = async () => {
            if (await checkHealth()) return;
            setTimeout(pollHealth, 2000);
        };
        pollHealth();
    }

    // Quick Tool Handlers (Dropdown & Grid Cards)
    document.querySelectorAll('.quick-tool, .quick-tool-card').forEach(el => {
        el.addEventListener('click', (e) => {
            e.preventDefault();
            const tool = el.getAttribute('data-tool');
            if (tool && conversionType) {
                conversionType.value = tool;
                // Trigger change event to show/hide options
                conversionType.dispatchEvent(new Event('change'));
                // Scroll to upload section
                document.getElementById('convertForm').scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Quality slider sync
    if(qualitySlider) {
        qualitySlider.addEventListener('input', (e) => {
            qualityValue.textContent = e.target.value + '%';
        });
    }
    
    // Aspect Ratio Lock Logic
    resizeWidth.addEventListener('input', (e) => {
        if(lockAspectRatio.checked && originalAspectRatio) {
            resizeHeight.value = Math.round(e.target.value / originalAspectRatio);
        }
    });
    resizeHeight.addEventListener('input', (e) => {
        if(lockAspectRatio.checked && originalAspectRatio) {
            resizeWidth.value = Math.round(e.target.value * originalAspectRatio);
        }
    });

    // Show/hide target size input based on conversion type
    conversionType.addEventListener('change', (e) => {
        const val = e.target.value;
        if (val === 'to_jpg' || val === 'pdf_to_jpg' || val === 'to_webp' || val === 'compress_image') {
            targetSizeContainer.style.display = 'block';
        } else {
            targetSizeContainer.style.display = 'none';
        }
    });

    // Clear Button Handler
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            selectedFiles = [];
            fileInput.value = '';
            previewSection.style.display = 'none';
            form.reset();
            qualityValue.textContent = '80%';
            fileListContainer.innerHTML = '';
            originalAspectRatio = null;
        });
    }

    // Drag and Drop Handlers
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        handleFiles(dt.files);
    });

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function renderFileList() {
        fileListContainer.innerHTML = '';
        totalOriginalBytes = 0;

        if (selectedFiles.length === 0) {
            previewSection.style.display = 'none';
            return;
        }

        previewSection.style.display = 'block';
        fileCountBadge.textContent = selectedFiles.length;

        selectedFiles.forEach((file, index) => {
            totalOriginalBytes += file.size;
            const kbSize = (file.size / 1024).toFixed(1);
            
            const item = document.createElement('div');
            item.className = 'file-item d-flex align-items-center p-2 bg-white rounded border';
            
            // File Icon / Thumb
            let thumbHtml = `<i class="bi bi-file-earmark-text fs-3 text-secondary me-3 px-2"></i>`;
            if (file.type.startsWith('image/')) {
                thumbHtml = `<img src="${URL.createObjectURL(file)}" class="rounded me-3 object-fit-cover" style="width: 40px; height: 40px;">`;
            }
            
            item.innerHTML = `
                ${thumbHtml}
                <div class="flex-grow-1 text-truncate pe-2">
                    <div class="fw-bold small text-truncate">${file.name}</div>
                    <div class="text-muted" style="font-size: 0.75rem;">${kbSize} KB</div>
                </div>
                <div class="file-remove-btn px-2 fs-5" data-index="${index}"><i class="bi bi-x-circle-fill"></i></div>
            `;
            
            fileListContainer.appendChild(item);
        });

        // Set aspect ratio from the first image
        const firstFile = selectedFiles[0];
        if (firstFile && firstFile.type.startsWith('image/')) {
            const img = new Image();
            img.onload = () => {
                originalAspectRatio = img.width / img.height;
                // Don't auto-fill inputs to avoid confusing user, just store the ratio
            };
            img.src = URL.createObjectURL(firstFile);
        } else {
            originalAspectRatio = null;
        }

        // Add remove handlers
        document.querySelectorAll('.file-remove-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const idx = parseInt(this.getAttribute('data-index'));
                selectedFiles.splice(idx, 1);
                renderFileList();
            });
        });
    }

    function handleFiles(files) {
        if(files.length === 0) return;
        selectedFiles = [...selectedFiles, ...Array.from(files)];
        renderFileList();
    }
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const type = conversionType.value;
        const size = document.getElementById('targetSize').value;
        const quality = document.getElementById('qualitySlider').value;
        
        const width = resizeWidth.value;
        const height = resizeHeight.value;
        const rotate = document.getElementById('rotateAngle').value;
        const flipH = document.getElementById('flipH').checked;
        const flipV = document.getElementById('flipV').checked;
        
        if (selectedFiles.length === 0) {
            alert("Please select at least one file to convert.");
            return;
        }
        
        // Frontend Validation
        for (let file of selectedFiles) {
            const fileName = file.name.toLowerCase();
            if (type.startsWith('pdf_') && !fileName.endsWith('.pdf')) {
                alert("Error: You chose a 'From PDF' format but uploaded a non-PDF file.");
                return;
            }
            if ((type.startsWith('to_') || type === 'image_to_pdf' || type === 'svg_to_png') && fileName.endsWith('.pdf')) {
                alert("Error: You chose an Image format or Image to PDF but uploaded a PDF file. Please select image files.");
                return;
            }
            if ((type === 'merge_pdf' || type === 'compress_pdf' || type === 'split_pdf') && !fileName.endsWith('.pdf')) {
                alert("Error: Please select PDF files for PDF tools.");
                return;
            }
            if (type === 'docx_to_pdf' && !(fileName.endsWith('.docx') || fileName.endsWith('.doc'))) {
                alert("Error: Please select a Word (.docx or .doc) file.");
                return;
            }
        }

        const formData = new FormData();
        let totalOriginalBytes = 0;
        selectedFiles.forEach(file => {
            formData.append('file', file);
            totalOriginalBytes += file.size;
        });
        formData.append('conversion_type', type);
        formData.append('quality', quality);
        
        if (size) formData.append('target_size', size);
        if (width) formData.append('width', width);
        if (height) formData.append('height', height);
        if (rotate) formData.append('rotate', rotate);
        if (flipH) formData.append('flip_h', 'true');
        if (flipV) formData.append('flip_v', 'true');
        
        const convertBtn = document.getElementById('convertBtn');
        const loading = document.getElementById('loading');
        const result = document.getElementById('result');
        const error = document.getElementById('error');
        const errorMessage = document.getElementById('errorMessage');
        
        // Reset state
        convertBtn.disabled = true;
        convertBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i> Converting...';
        loading.style.display = 'block';
        result.style.display = 'none';
        error.style.display = 'none';
        progressText.textContent = "Uploading & Processing...";
        
        try {
            const response = await fetch('/api/convert', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                let errData;
                try {
                    errData = await response.json();
                } catch(e) {
                    errData = { error: 'Unknown server error.' };
                }
                throw new Error(errData.error || 'Conversion failed. Please check file format.');
            }
            
            // Handle successful file download
            progressText.textContent = "Finalizing Download...";
            const blob = await response.blob();
            
            // Calculate size reduction
            const newBytes = blob.size;
            let sizeMsg = '';
            if(newBytes < totalOriginalBytes) {
                const percent = Math.round((1 - (newBytes / totalOriginalBytes)) * 100);
                sizeMsg = `File size reduced by ${percent}%! `;
            }
            resultSubtitle.textContent = sizeMsg + "Your file has been downloaded automatically.";

            const url = window.URL.createObjectURL(blob);
            
            const downloadLink = document.getElementById('downloadLink');
            const previewBtn = document.getElementById('previewBtn');
            const previewContent = document.getElementById('previewContent');
            
            downloadLink.href = url;
            
            // Determine filename from header or fallback
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'converted_file';
            
            if (contentDisposition && contentDisposition.includes('filename=')) {
                let matches = /filename="([^"]+)"/.exec(contentDisposition);
                if (matches && matches[1]) {
                    filename = matches[1];
                } else {
                    filename = contentDisposition.split('filename=')[1];
                }
            } else {
                if (response.type === 'application/zip' || selectedFiles.length > 1) {
                    filename = 'converted_files.zip';
                } else if (type.includes('docx')) {
                    filename = 'converted.docx';
                } else if (type.includes('pdf')) {
                    filename = 'converted.pdf';
                } else if (type.includes('png')) {
                    filename = 'converted.png';
                } else if (type.includes('jpg')) {
                    filename = 'converted.jpg';
                } else if (type.includes('webp')) {
                    filename = 'converted.webp';
                }
            }
            
            downloadLink.download = filename;
            
            // Setup Preview Modal Content
            if (response.type.startsWith('image/') || filename.match(/\.(jpg|jpeg|png|webp|gif|bmp)$/i)) {
                previewBtn.style.display = 'block';
                previewContent.innerHTML = `<img src="${url}" class="img-fluid rounded shadow-sm" alt="Preview" style="max-height: 70vh;">`;
            } else if (response.type === 'application/pdf' || filename.endsWith('.pdf')) {
                previewBtn.style.display = 'block';
                previewContent.innerHTML = `<iframe src="${url}" width="100%" height="600px" class="border-0 rounded shadow-sm"></iframe>`;
            } else if (filename.endsWith('.zip')) {
                previewBtn.style.display = 'block';
                previewContent.innerHTML = `
                    <div class="alert alert-info d-flex align-items-center">
                        <i class="bi bi-file-zip fs-1 me-3"></i>
                        <div>
                            <h5 class="mb-1">Multiple Files Generated</h5>
                            <p class="mb-0">Aapki PDF me ek se jyada pages the (ya aapne multiple files select ki thi), isliye saari images ko ek <b>.zip</b> folder me pack kar diya gaya hai. Kripya <b>Download File</b> par click karke zip file save karein aur use extract (unzip) karke dekhein.</p>
                        </div>
                    </div>
                `;
            } else {
                previewBtn.style.display = 'block';
                previewContent.innerHTML = `
                    <div class="alert alert-secondary">
                        <i class="bi bi-info-circle me-2"></i> Preview is not available for this file format (<strong>${filename}</strong>). Please download the file to view it.
                    </div>
                `;
            }
            
            previewBtn.onclick = () => {
                const modal = new bootstrap.Modal(document.getElementById('previewModal'));
                modal.show();
            };
            
            loading.style.display = 'none';
            result.style.display = 'block';
            
            // Auto download (Some browsers block this if it takes too long, so Download button is clearly visible)
            setTimeout(() => { downloadLink.click(); }, 100);
            
        } catch (err) {
            console.error(err);
            loading.style.display = 'none';
            error.style.display = 'block';
            
            if (err.message === 'Failed to fetch') {
                errorMessage.innerHTML = '<strong>Connection Error:</strong> Backend server is not running!<br>Please run <code>python app.py</code> in the backend folder.';
            } else {
                errorMessage.innerHTML = `<strong>Error:</strong> ${err.message}`;
            }
        } finally {
            convertBtn.disabled = false;
            convertBtn.innerHTML = '<i class="bi bi-magic me-2"></i> Convert File(s)';
        }
    });
});

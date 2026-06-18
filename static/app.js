function runIngest() {
    const btn = document.getElementById('ingestBtn');
    const loading = document.getElementById('loading');
    const loadingText = loading.querySelector('p');
    btn.disabled = true;
    loading.style.display = 'block';
    loadingText.textContent = 'Ingesting data...';

    fetch('/api/v1/ingest', {
        method: 'POST'
    })
    .then(res => {
        if (res.ok) {
            loadingText.textContent = 'Data ingestion complete! Refreshing page...';
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            throw new Error('Ingestion failed');
        }
    })
    .catch(err => {
        console.error(err);
        loadingText.textContent = 'Ingestion failed. Please try again.';
        btn.disabled = false;
        setTimeout(() => {
            loading.style.display = 'none';
        }, 2000);
    });
}

function runScoring() {
    const btn = document.getElementById('scoreBtn');
    const loading = document.getElementById('loading');
    const loadingText = loading.querySelector('p');
    btn.disabled = true;
    loading.style.display = 'block';

    fetch('/api/v1/score', {
        method: 'POST'
    })
    .then(res => {
        if (res.ok) {
            loadingText.textContent = 'Scoring complete! Loading results...';
            setTimeout(() => {
                window.location.href = '/priorities';
            }, 1000);
        } else {
            throw new Error('Scoring failed');
        }
    })
    .catch(err => {
        console.error(err);
        loadingText.textContent = 'Scoring failed. Please try again.';
        btn.disabled = false;
        setTimeout(() => {
            loading.style.display = 'none';
        }, 2000);
    });
}

function deploy(button, scoreId) {
    const row = button.closest('tr');
    const statusCell = row.querySelector('.status');
    const progressBar = row.querySelector('.progress-bar');
    const progressFill = progressBar.querySelector('.progress-fill');

    button.disabled = true;
    button.textContent = 'Deploying...';
    statusCell.textContent = 'Deploying...';
    progressBar.style.display = 'block';

    let progress = 0;
    const interval = setInterval(() => {
        progress = Math.min(progress + 8, 95);
        progressFill.style.width = `${progress}%`;
    }, 100);

    fetch(`/api/v1/deploy/${scoreId}`, {
        method: 'POST'
    })
    .then(res => {
        clearInterval(interval);
        if (!res.ok) throw new Error('Deploy failed');
        progressFill.style.width = '100%';
        return res.json();
    })
    .then(() => {
        statusCell.textContent = 'Completed';
        row.classList.add('deployed-row');
        button.textContent = 'Patched';
        button.classList.add('deployed-button');
        progressFill.style.width = '100%';
        setTimeout(() => {
            progressBar.style.display = 'none';
        }, 500);
        showToast('Deployment complete for ' + row.querySelector('td:nth-child(6)').textContent);
    })
    .catch(err => {
        console.error(err);
        statusCell.textContent = 'Failed';
        button.textContent = 'Retry';
        button.disabled = false;
        progressBar.style.display = 'none';
        showToast('Deployment failed. Please try again.', true);
    });
}

function showToast(message, isError = false) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = 'toast' + (isError ? ' toast-error' : ' toast-success');
    toast.style.opacity = '1';
    setTimeout(() => {
        toast.style.opacity = '0';
    }, 3200);
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.progress-track-fill[data-fill]').forEach(fill => {
        const width = fill.dataset.fill;
        if (width !== undefined) {
            fill.style.width = `${width}%`;
        }
    });
    
    // Animate score values
    animateScores();
});

// Animate score values from 0 to final value
function animateScores() {
    const scoreCells = document.querySelectorAll('table td:first-child');
    const animationDuration = 2000; // 2 seconds
    
    scoreCells.forEach(cell => {
        const finalValue = parseFloat(cell.textContent);
        if (isNaN(finalValue)) return;
        
        let startTime = null;
        const startValue = 0;
        
        function animate(currentTime) {
            if (startTime === null) startTime = currentTime;
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / animationDuration, 1);
            const currentValue = startValue + (finalValue - startValue) * progress;
            
            cell.textContent = currentValue.toFixed(1);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        }
        
        requestAnimationFrame(animate);
    });
}

// Modal functions for vulnerability details
function showDetail(scoreId) {
    const modal = document.getElementById('detailModal');
    const modalBody = document.getElementById('modalBody');
    
    modalBody.innerHTML = '<p>Loading...</p>';
    modal.style.display = 'block';
    
    fetch(`/api/v1/priorities/${scoreId}`)
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                modalBody.innerHTML = '<p>Error loading details</p>';
                return;
            }
            
            // Format the modal content
            modalBody.innerHTML = `
                <div style="line-height: 1.8;">
                    <p><strong>Hostname:</strong> ${data.hostname}</p>
                    <p><strong>Device ID:</strong> ${data.device_id}</p>
                    <p><strong>Device Criticality:</strong> ${data.criticality}</p>
                    <p><strong>CVE ID:</strong> ${data.cve_id}</p>
                    <p><strong>Severity:</strong> ${data.severity}</p>
                    <p><strong>CVSS Score:</strong> ${data.cvss}</p>
                    <p><strong>Description:</strong> ${data.description || 'N/A'}</p>
                    <hr style="margin: 15px 0;">
                    <p><strong>Priority Score:</strong> ${data.score_value.toFixed(1)}</p>
                    <p><strong>Priority:</strong> <span class="priority ${data.priority.toLowerCase()}">${data.priority}</span></p>
                    <p><strong>Scoring Breakdown:</strong> ${data.score_reason}</p>
                    <p><strong>Status:</strong> ${data.action_status}</p>
                </div>
            `;
        })
        .catch(err => {
            console.error(err);
            modalBody.innerHTML = '<p>Error loading details</p>';
        });
}

function closeDetail() {
    const modal = document.getElementById('detailModal');
    modal.style.display = 'none';
}

// Close modal when clicking outside of it
window.onclick = function(event) {
    const modal = document.getElementById('detailModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

// CSV Export function
function exportCSV() {
    fetch('/api/v1/export-csv')
        .then(res => {
            if (!res.ok) throw new Error('Export failed');
            return res.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'priorities.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showToast('CSV exported successfully');
        })
        .catch(err => {
            console.error(err);
            showToast('Export failed', true);
        });
}
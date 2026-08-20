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

// UI Color-coding notes:
// - Priority CSS classes map to colors in `styles.css`.
// - Score ranges: Critical (≥8) red, High (6-8) orange, Medium (4-6) yellow, Low (<4) green.
// This mapping is produced server-side when computing `priority` and the UI applies
// the corresponding CSS class (e.g. `priority critical`) so colors remain consistent.

function deploy(button, scoreId) {
    // Open approval modal instead of using prompt(); modal validates input.
    document.getElementById('approveScoreId').value = scoreId;
    document.getElementById('approverName').value = '';
    document.getElementById('approveError').style.display = 'none';
    document.getElementById('approveModal').style.display = 'block';
}

function closeApprove() {
    document.getElementById('approveModal').style.display = 'none';
}

function submitApproval() {
    const scoreId = document.getElementById('approveScoreId').value;
    const approver = document.getElementById('approverName').value.trim();
    const errDiv = document.getElementById('approveError');
    if (!approver) {
        errDiv.textContent = 'Approver name is required';
        errDiv.style.display = 'block';
        return;
    }

    errDiv.style.display = 'none';
    // Record approval then call deploy endpoint
    fetch(`/api/v1/deploy/${scoreId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approver })
    })
    .then(res => {
        if (!res.ok) return res.json().then(j => { throw new Error(j.detail || 'Approval failed') });
        return res.json();
    })
    .then(() => {
        // Close modal
        closeApprove();
        // Now call deploy to complete
        return fetch(`/api/v1/deploy/${scoreId}`, { method: 'POST' });
    })
    .then(res => {
        if (!res.ok) return res.json().then(j => { throw new Error(j.detail || 'Deploy failed') });
        // refresh the page to show updated status
        showToast('Deployment completed');
        setTimeout(() => window.location.reload(), 600);
    })
    .catch(err => {
        errDiv.textContent = err.message || 'Approval or deploy failed';
        errDiv.style.display = 'block';
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
            
            // Format the modal content and show approver/timestamp when available
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
                    <p><strong>Approver:</strong> ${data.approver || 'N/A'}</p>
                    <p><strong>Action Timestamp:</strong> ${data.timestamp || 'N/A'}</p>
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
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
});
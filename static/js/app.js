// MuhasebeDiyarı - Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle for mobile
    const menuToggle = document.getElementById('menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            const sidebar = document.getElementById('sidebar-wrapper');
            sidebar.classList.toggle('d-none');
            sidebar.classList.toggle('d-md-block');
        });
    }

    // Privacy mask toggle
    const privacyToggle = document.getElementById('privacy-toggle');
    if (privacyToggle) {
        // Default: masked (true). Load stored preference, default to true.
        let isMasked = localStorage.getItem('privacyMasked');
        if (isMasked === null) {
            isMasked = true; // default: sansürlü
        } else {
            isMasked = (isMasked === 'true');
        }
        applyPrivacyMask(isMasked);

        privacyToggle.addEventListener('click', function() {
            isMasked = !isMasked;
            localStorage.setItem('privacyMasked', isMasked);
            applyPrivacyMask(isMasked);
        });
    }
});

function applyPrivacyMask(masked) {
    const body = document.body;
    const btn = document.getElementById('privacy-toggle');
    const icon = btn ? btn.querySelector('i') : null;

    if (masked) {
        body.classList.add('privacy-mask');
        if (icon) { icon.className = 'bi bi-eye-slash'; }
        if (btn) { btn.title = 'Sansürlü - Tıklayarak göster'; }
    } else {
        body.classList.remove('privacy-mask');
        if (icon) { icon.className = 'bi bi-eye'; }
        if (btn) { btn.title = 'Sansürsüz - Tıklayarak gizle'; }
    }
}

// Auto-close alerts after 5 seconds
setTimeout(function() {
    document.querySelectorAll('.alert-dismissible').forEach(function(alert) {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}, 5000);

// Format numbers with Turkish locale
function formatCurrency(amount) {
    return new Intl.NumberFormat('tr-TR', { 
        style: 'currency', 
        currency: 'TRY',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

// Date formatting helper
function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString('tr-TR');
}

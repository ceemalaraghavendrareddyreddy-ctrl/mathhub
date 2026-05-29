// Highlight active sidebar link
document.querySelectorAll('.sidebar-link').forEach(link => {
    if (link.href === window.location.href) {
        link.classList.add('active');
    }
});

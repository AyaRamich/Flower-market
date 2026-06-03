


document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        document.querySelectorAll('.message').forEach(m => m.remove());
    }, 4000);
});


// Vérifier toutes les 10 secondes
if (document.getElementById('msg-badge')) {
    updateBadge();
    setInterval(updateBadge, 10000);
}
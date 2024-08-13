document.addEventListener("DOMContentLoaded", function() {
    const container = document.querySelector('.container');
    setInterval(() => {
        container.style.opacity = (container.style.opacity == 0.9 ? 1 : 0.9);
    }, 200);
});


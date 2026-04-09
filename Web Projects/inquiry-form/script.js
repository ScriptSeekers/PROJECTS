document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('inquiry-form');

    form.onsubmit = (e) => {
        e.preventDefault();
        const btn = form.querySelector('.cta-btn');
        const originalText = btn.innerText;
        
        btn.innerText = 'Sending...';
        btn.disabled = true;

        setTimeout(() => {
            alert('Your inquiry has been sent successfully. We will be in touch soon!');
            form.reset();
            btn.innerText = originalText;
            btn.disabled = false;
        }, 1500);
    };
});

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('pw-input');
    const toggleBtn = document.getElementById('toggle-visibility');
    const fill = document.getElementById('strength-fill');
    const text = document.getElementById('strength-text');
    const percent = document.getElementById('strength-percent');
    const insightList = document.getElementById('insight-list');

    const criteria = {
        length: document.getElementById('crit-length'),
        upper: document.getElementById('crit-upper'),
        number: document.getElementById('crit-number'),
        symbol: document.getElementById('crit-symbol')
    };

    toggleBtn.onclick = () => {
        const isPw = input.type === 'password';
        input.type = isPw ? 'text' : 'password';
        toggleBtn.innerHTML = isPw ? 
            `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>` : 
            `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
    };

    input.oninput = () => {
        const val = input.value;
        const results = analyzePassword(val);
        updateUI(results);
    };

    function analyzePassword(pw) {
        if (!pw) return { score: 0, checks: {}, insights: ["Awaiting your secret passphrase..."] };

        let score = 0;
        const checks = {
            length: pw.length >= 8,
            upper: /[A-Z]/.test(pw),
            number: /[0-9]/.test(pw),
            symbol: /[^A-Za-z0-9]/.test(pw)
        };

        if (checks.length) score += 25;
        if (checks.upper) score += 25;
        if (checks.number) score += 25;
        if (checks.symbol) score += 25;

        // Bonus for length
        if (pw.length >= 12) score = Math.min(100, score + 10);
        if (pw.length >= 16) score = Math.min(100, score + 10);

        const insights = [];
        if (pw.length < 8) insights.push("Too short. Aim for at least 12 characters.");
        if (!checks.symbol) insights.push("Add a special character like ! or @.");
        if (!checks.number) insights.push("Include numbers for complexity.");
        if (score >= 90) insights.push("Excellent! This password is very secure.");
        else if (score >= 50) insights.push("Decent, but could be stronger.");

        return { score, checks, insights };
    }

    function updateUI({ score, checks, insights }) {
        // Update bar
        fill.style.width = `${score}%`;
        percent.textContent = `${score}%`;

        // Update colors
        let color = 'var(--error)';
        let status = 'Weak';
        if (score >= 80) { color = 'var(--success)'; status = 'Strong'; }
        else if (score >= 50) { color = 'var(--warning)'; status = 'Medium'; }
        
        fill.style.backgroundColor = color;
        fill.style.color = color; // For box-shadow
        text.textContent = status;
        text.style.color = color;

        // Update indicators
        Object.keys(criteria).forEach(key => {
            criteria[key].classList.toggle('valid', checks[key]);
        });

        // Update insights
        insightList.innerHTML = insights.map(i => `<li>${i}</li>`).join('');
    }
});

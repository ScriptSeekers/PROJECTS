document.addEventListener('DOMContentLoaded', () => {
    const calculateBtn = document.getElementById('calculate-btn');
    const resetBtn = document.getElementById('reset-btn');
    const inputSection = document.querySelector('.input-section');
    const resultSection = document.getElementById('result-view');
    const heightInputs = document.getElementById('height-inputs');
    const heightToggle = document.getElementById('height-unit-toggle');
    const weightToggle = document.getElementById('weight-unit-toggle');
    
    let currentHeightUnit = 'cm';
    let currentWeightUnit = 'kg';

    // Unit Toggles
    heightToggle.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.onclick = () => {
            heightToggle.querySelector('.active').classList.remove('active');
            btn.classList.add('active');
            currentHeightUnit = btn.dataset.unit;
            renderHeightInputs();
        };
    });

    weightToggle.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.onclick = () => {
            weightToggle.querySelector('.active').classList.remove('active');
            btn.classList.add('active');
            currentWeightUnit = btn.dataset.unit;
        };
    });

    function renderHeightInputs() {
        if (currentHeightUnit === 'cm') {
            heightInputs.innerHTML = `
                <div class="form-group">
                    <label>Height (cm)</label>
                    <input type="number" id="height" placeholder="175">
                </div>
            `;
        } else {
            heightInputs.innerHTML = `
                <div class="form-group">
                    <label>Feet</label>
                    <input type="number" id="height-ft" placeholder="5">
                </div>
                <div class="form-group">
                    <label>Inches</label>
                    <input type="number" id="height-in" placeholder="9">
                </div>
            `;
            heightInputs.style.display = 'grid';
            heightInputs.style.gridTemplateColumns = '1fr 1fr';
            heightInputs.style.gap = '20px';
        }
    }

    calculateBtn.onclick = () => {
        let h, w;
        
        // Handle height
        if (currentHeightUnit === 'cm') {
            h = parseFloat(document.getElementById('height').value) / 100;
        } else {
            const ft = parseFloat(document.getElementById('height-ft').value || 0);
            const inc = parseFloat(document.getElementById('height-in').value || 0);
            h = (ft * 12 + inc) * 0.0254;
        }

        // Handle weight
        w = parseFloat(document.getElementById('weight').value);
        if (currentWeightUnit === 'lbs') w *= 0.453592;

        if (!h || !w || h <= 0 || w <= 0) return alert('Please enter valid measurements');

        const bmi = w / (h * h);
        showResult(bmi);
    };

    function showResult(bmi) {
        inputSection.classList.add('hidden');
        resultSection.classList.remove('hidden');

        const displayBmi = bmi.toFixed(1);
        document.getElementById('bmi-value').textContent = displayBmi;

        // Needle rotation logic
        // Range: 15 to 40 (approx)
        // Deg range: -90 (under) to 90 (obese)
        let deg = ((bmi - 15) / (40 - 15)) * 180 - 90;
        deg = Math.max(-90, Math.min(90, deg));
        document.getElementById('needle').style.transform = `rotate(${deg}deg)`;

        const categoryEl = document.getElementById('bmi-category');
        const tipEl = document.getElementById('health-tip');

        if (bmi < 18.5) {
            categoryEl.textContent = 'Underweight';
            categoryEl.style.color = 'var(--accent)';
            categoryEl.style.background = 'rgba(6, 182, 212, 0.1)';
            tipEl.textContent = 'Try to include more nutrient-dense foods in your diet to reach a healthy weight for your height.';
        } else if (bmi < 25) {
            categoryEl.textContent = 'Healthy Weight';
            categoryEl.style.color = 'var(--success)';
            categoryEl.style.background = 'rgba(16, 185, 129, 0.1)';
            tipEl.textContent = "You're in the healthy range! Maintain your lifestyle with a balanced diet and regular exercise.";
        } else if (bmi < 30) {
            categoryEl.textContent = 'Overweight';
            categoryEl.style.color = 'var(--warning)';
            categoryEl.style.background = 'rgba(245, 158, 11, 0.1)';
            tipEl.textContent = 'Consider making small adjustments to your activity level and diet to improve your wellness score.';
        } else {
            categoryEl.textContent = 'Obese';
            categoryEl.style.color = 'var(--error)';
            categoryEl.style.background = 'rgba(239, 68, 68, 0.1)';
            tipEl.textContent = 'Consult with a health professional to create a sustainable plan for achieving your health goals.';
        }
    }

    resetBtn.onclick = () => {
        resultSection.classList.add('hidden');
        inputSection.classList.remove('hidden');
    };
});

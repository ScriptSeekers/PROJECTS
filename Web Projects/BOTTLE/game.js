document.addEventListener('DOMContentLoaded', () => {
    const bottle = document.getElementById('bottle');
    const spinBtn = document.getElementById('spin-btn');
    const slots = document.querySelectorAll('.slot');
    
    let currentRotation = 0;

    spinBtn.onclick = () => {
        // Randomize rotation: at least 5 full spins + random degree
        const extraDegrees = Math.floor(Math.random() * 360);
        const spins = (Math.floor(Math.random() * 5) + 5) * 360;
        
        currentRotation += spins + extraDegrees;
        bottle.style.transform = `rotate(${currentRotation}deg)`;

        spinBtn.disabled = true;
        spinBtn.innerText = 'SPINNING...';

        setTimeout(() => {
            spinBtn.disabled = false;
            spinBtn.innerText = 'SPIN AGAIN';
            
            // Highlight player logic could go here
            highlightWinner(currentRotation % 360);
        }, 3000);
    };

    function highlightWinner(deg) {
        slots.forEach(s => s.classList.remove('active'));
        
        // P1: 0 (360), P2: 90, P3: 180, P4: 270
        let winnerIndex;
        if (deg >= 315 || deg < 45) winnerIndex = 0;
        else if (deg >= 45 && deg < 135) winnerIndex = 1;
        else if (deg >= 135 && deg < 225) winnerIndex = 2;
        else winnerIndex = 3;

        slots[winnerIndex].classList.add('active');
    }
});

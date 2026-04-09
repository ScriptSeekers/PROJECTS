document.addEventListener('DOMContentLoaded', () => {
    const cityInput = document.getElementById('city-input');
    const searchBtn = document.getElementById('search-btn');
    const display = document.getElementById('weather-display');
    const loading = document.getElementById('loading');
    const bg = document.getElementById('weather-bg');

    searchBtn.onclick = () => {
        const city = cityInput.value;
        if (!city) return;

        display.classList.add('hidden');
        loading.innerHTML = '<h2>Fetching...</h2>';
        loading.classList.remove('hidden');

        setTimeout(() => {
            updateWeather(city);
        }, 1000);
    };

    function updateWeather(city) {
        loading.classList.add('hidden');
        display.classList.remove('hidden');
        
        document.getElementById('city-name').textContent = city;
        document.getElementById('current-date').textContent = new Date().toLocaleDateString('en-US', { weekday: 'long', day: 'numeric', month: 'long' });
        
        // Mock randomized weather
        const temp = Math.floor(Math.random() * (35 - 10) + 10);
        document.getElementById('temp-val').textContent = temp;
        
        const conditions = ['Clear Sky', 'Mostly Cloudy', 'Rainy', 'Thunderstorm', 'Snowy'];
        constIcons = ['☀️', '⛅', '🌧️', '⛈️', '❄️'];
        const gradients = [
            'radial-gradient(circle at 20% 30%, #3b82f6 0%, #1d4ed8 100%)', // Blue
            'linear-gradient(135deg, #64748b 0%, #334155 100%)', // Slate
            'radial-gradient(circle at top right, #475569 0%, #0f172a 100%)', // Dark Slate
            'linear-gradient(45deg, #1e1b4b 0%, #020617 100%)', // Indigo Deep
            'radial-gradient(circle at 50% 50%, #94a3b8 0%, #475569 100%)'  // Stormy
        ];

        const idx = Math.floor(Math.random() * conditions.length);
        document.getElementById('weather-desc').textContent = conditions[idx];
        document.getElementById('main-icon').textContent = constIcons[idx];
        bg.style.background = gradients[idx];

        document.getElementById('humidity').textContent = `${Math.floor(Math.random() * 50 + 40)}%`;
        document.getElementById('wind').textContent = `${Math.floor(Math.random() * 20 + 5)} km/h`;

        renderForecast();
    }

    function renderForecast() {
        const container = document.getElementById('forecast-container');
        container.innerHTML = '';
        const days = ['Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Mon'];
        
        days.forEach(day => {
            const item = document.createElement('div');
            item.className = 'forecast-item';
            item.innerHTML = `
                <p>${day}</p>
                <div class="icon">⛅</div>
                <div class="temp">22°</div>
            `;
            container.appendChild(item);
        });
    }

    cityInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchBtn.click();
    });
});

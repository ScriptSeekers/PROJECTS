// Add this to your existing script.js

// Function to parse study plan and extract tasks
function parseStudyPlan(planText) {
    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    const dailyTasks = {};
    
    days.forEach(day => {
        dailyTasks[day] = [];
        const dayRegex = new RegExp(`${day}:\\s*([\\s\\S]*?)(?=${days[days.indexOf(day) + 1]}|$)`, 'i');
        const match = planText.match(dayRegex);
        
        if (match && match[1]) {
            const tasks = match[1].split('\n').filter(line => line.trim() && !line.match(/^\s*$/));
            dailyTasks[day] = tasks.map(task => task.replace(/^-\s*/, '').trim());
        }
    });
    
    return dailyTasks;
}

// Function to create visual calendar
function createVisualCalendar(dailyTasks) {
    const calendarEl = document.getElementById('visual-calendar');
    if (!calendarEl) return;
    
    let calendarHTML = '<div class="visual-week">';
    
    for (const day in dailyTasks) {
        calendarHTML += `
            <div class="visual-day">
                <h4>${day}</h4>
                <div class="visual-tasks">
        `;
        
        if (dailyTasks[day].length > 0) {
            dailyTasks[day].forEach(task => {
                calendarHTML += `<div class="visual-task">${task}</div>`;
            });
        } else {
            calendarHTML += `<p>No tasks scheduled</p>`;
        }
        
        calendarHTML += `
                </div>
            </div>
        `;
    }
    
    calendarHTML += '</div>';
    calendarEl.innerHTML = calendarHTML;
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    const planText = document.querySelector('pre')?.innerText;
    if (planText) {
        const dailyTasks = parseStudyPlan(planText);
        createVisualCalendar(dailyTasks);
    }
    
    // Gradient animation code (keep your existing code)
    let angle = 100;
    let speed = 2;
    let direction = 1;
    let animationId = null;
    const angleDisplay = document.getElementById('angleDisplay');

    function updateGradient() {
        angle = (angle + speed * direction) % 360;
        if (angle < 0) angle += 360;

        document.body.style.background = `linear-gradient(${angle}deg, #03dbf8, #d507dc)`;

        if (angleDisplay) {
            angleDisplay.textContent = `Angle: ${Math.round(angle)}°`;
        }

        animationId = requestAnimationFrame(updateGradient);
    }

    updateGradient();
});
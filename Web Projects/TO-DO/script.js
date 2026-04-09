document.addEventListener('DOMContentLoaded', () => {
    const taskInput = document.getElementById('task-input');
    const addBtn = document.getElementById('add-btn');
    const todoList = document.getElementById('todo-list');
    const tasksLeft = document.getElementById('tasks-left');
    const clearBtn = document.getElementById('clear-completed');
    const progressPercent = document.getElementById('progress-percent');
    const canvas = document.getElementById('progress-ring');
    const ctx = canvas.getContext('2d');

    let tasks = JSON.parse(localStorage.getItem('zenith_tasks')) || [];

    function save() {
        localStorage.setItem('zenith_tasks', JSON.stringify(tasks));
        render();
    }

    function render() {
        todoList.innerHTML = '';
        tasks.forEach((task, index) => {
            const item = document.createElement('div');
            item.className = `todo-item ${task.completed ? 'completed' : ''}`;
            item.innerHTML = `
                <div class="check-box ${task.completed ? 'checked' : ''}" onclick="toggleTask(${index})"></div>
                <span>${task.text}</span>
                <button class="delete-btn" onclick="deleteTask(${index})">×</button>
            `;
            todoList.appendChild(item);
        });

        const activeCount = tasks.filter(t => !t.completed).length;
        tasksLeft.textContent = activeCount;

        const percent = tasks.length > 0 ? Math.round((tasks.filter(t => t.completed).length / tasks.length) * 100) : 0;
        progressPercent.textContent = `${percent}%`;
        drawProgress(percent);
    }

    function drawProgress(percent) {
        const x = canvas.width / 2;
        const y = canvas.height / 2;
        const radius = 25;
        const startAngle = -0.5 * Math.PI;
        const endAngle = (percent / 100) * 2 * Math.PI + startAngle;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Background track
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, 2 * Math.PI);
        ctx.strokeStyle = 'rgba(255,255,255,0.05)';
        ctx.lineWidth = 5;
        ctx.stroke();

        // Progress bar
        if (percent > 0) {
            ctx.beginPath();
            ctx.arc(x, y, radius, startAngle, endAngle);
            ctx.strokeStyle = '#f43f5e';
            ctx.lineWidth = 5;
            ctx.lineCap = 'round';
            ctx.stroke();
        }
    }

    addBtn.onclick = () => {
        const text = taskInput.value.trim();
        if (text) {
            tasks.push({ text, completed: false, category: 'personal' });
            taskInput.value = '';
            save();
        }
    };

    taskInput.onkeypress = (e) => { if (e.key === 'Enter') addBtn.click(); };

    window.toggleTask = (index) => {
        tasks[index].completed = !tasks[index].completed;
        save();
    };

    window.deleteTask = (index) => {
        tasks.splice(index, 1);
        save();
    };

    clearBtn.onclick = () => {
        tasks = tasks.filter(t => !t.completed);
        save();
    };

    // Date setup
    const now = new Date();
    const optionsDay = { weekday: 'long' };
    const optionsDate = { day: 'numeric', month: 'long', year: 'numeric' };
    
    document.getElementById('current-day').textContent = now.toLocaleDateString('en-US', optionsDay);
    
    // Add ordinal suffix to day (e.g. 8th)
    const day = now.getDate();
    const suffix = (day % 10 === 1 && day !== 11) ? 'st' :
                   (day % 10 === 2 && day !== 12) ? 'nd' :
                   (day % 10 === 3 && day !== 13) ? 'rd' : 'th';
    
    const month = now.toLocaleDateString('en-US', { month: 'long' });
    const year = now.getFullYear();
    document.getElementById('current-date').textContent = `${day}${suffix} ${month}, ${year}`;

    render();
});

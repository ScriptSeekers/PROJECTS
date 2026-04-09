// Initialize the report
document.addEventListener('DOMContentLoaded', function() {
    // Set current date
    document.getElementById('report-date').textContent = new Date().toLocaleString();
    
    // Load and display data
    loadUsers();
    loadHistory();
});

// Get all users from the database
function getUsers() {
    return JSON.parse(localStorage.getItem('users') || '[]');
}

// Get all assessment history
function getHistory() {
    return JSON.parse(localStorage.getItem('assessmentHistory') || '{}');
}

// Load and display users
function loadUsers() {
    const users = getUsers();
    const usersContainer = document.getElementById('users-container');
    
    usersContainer.innerHTML = '<h2>Registered Users (' + users.length + ')</h2>';
    
    if (users.length === 0) {
        usersContainer.innerHTML += '<div class="no-data">No users found in the database.</div>';
        return;
    }
    
    let usersTable = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Registration Date</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    users.forEach(user => {
        const regDate = new Date(user.createdAt).toLocaleDateString();
        usersTable += `
            <tr>
                <td>${user.id}</td>
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td>${regDate}</td>
            </tr>
        `;
    });
    
    usersTable += '</tbody></table>';
    usersContainer.innerHTML += usersTable;
}

// Load and display assessment history
function loadHistory() {
    const history = getHistory();
    const users = getUsers();
    const historyContainer = document.getElementById('history-container');
    
    // Count total assessments
    let totalAssessments = 0;
    for (const userId in history) {
        totalAssessments += history[userId].length;
    }
    
    historyContainer.innerHTML = '<h2>Assessment History (' + totalAssessments + ' assessments)</h2>';
    
    if (totalAssessments === 0) {
        historyContainer.innerHTML += '<div class="no-data">No assessment history found.</div>';
        return;
    }
    
    // Career paths reference (simplified for printing)
    const careerPaths = {
        science: "Science and Technology Fields",
        commerce: "Business and Commerce Fields",
        arts: "Arts and Humanities Fields",
        engineering: "Engineering Fields",
        medical: "Medical and Healthcare Fields",
        business: "Business Management Fields",
        law: "Legal Fields",
        design: "Design and Creative Fields",
        unsure: "Multiple Career Options"
    };
    
    for (const userId in history) {
        const userAssessments = history[userId];
        const user = users.find(u => u.id == userId) || {name: "Unknown User", email: "N/A"};
        
        historyContainer.innerHTML += `
            <h3>User: ${user.name} (${user.email})</h3>
            <p><strong>Total Assessments:</strong> ${userAssessments.length}</p>
        `;
        
        userAssessments.forEach((assessment, index) => {
            const date = new Date(assessment.date).toLocaleDateString();
            const careerTitle = careerPaths[assessment.careerPath] || assessment.careerPath;
            
            historyContainer.innerHTML += `
                <div class="history-item">
                    <h4>Assessment #${userAssessments.length - index}</h4>
                    <p><strong>Date:</strong> ${date}</p>
                    <p><strong>Recommended Career:</strong> ${careerTitle}</p>
                    <p><strong>Match Score:</strong> ${assessment.score}</p>
                </div>
            `;
        });
    }
}
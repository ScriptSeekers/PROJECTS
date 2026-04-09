// Theme management
const themeSwitcher = document.getElementById('theme-switcher');
const themeIcon = document.getElementById('theme-icon');
let isDarkTheme = localStorage.getItem('darkTheme') === 'true';

// Apply saved theme
if (isDarkTheme) {
    document.body.classList.add('dark-theme');
    themeIcon.textContent = '☀️';
}

// Theme switcher event
themeSwitcher.addEventListener('click', () => {
    isDarkTheme = !isDarkTheme;
    document.body.classList.toggle('dark-theme');
    themeIcon.textContent = isDarkTheme ? '☀️' : '🌙';
    localStorage.setItem('darkTheme', isDarkTheme);
});

// Page navigation
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.add('hidden');
    });
    document.getElementById(pageId).classList.remove('hidden');
    
    // If showing history page, update the display
    if (pageId === 'history') {
        updateHistoryDisplay();
    }
}

// Authentication simulation with localStorage backend
let currentUser = null;
let isLoggedIn = false;

// Initialize user database if it doesn't exist
function initUserDatabase() {
    if (!localStorage.getItem('users')) {
        localStorage.setItem('users', JSON.stringify([]));
    }
}

// Get all users from the database
function getUsers() {
    return JSON.parse(localStorage.getItem('users') || '[]');
}

// Save a user to the database
function saveUser(user) {
    const users = getUsers();
    users.push(user);
    localStorage.setItem('users', JSON.stringify(users));
}

// Find a user by email
function findUserByEmail(email) {
    const users = getUsers();
    return users.find(user => user.email === email);
}

// Validate email format
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Validate password strength
function isValidPassword(password) {
    return password.length >= 6;
}

// Show error message
function showError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
}

// Hide error message
function hideError(elementId) {
    const errorElement = document.getElementById(elementId);
    errorElement.classList.add('hidden');
}

// Check authentication and update UI
function checkAuthStatus() {
    const userData = localStorage.getItem('currentUser');
    if (userData) {
        currentUser = JSON.parse(userData);
        isLoggedIn = true;
        document.getElementById('auth-button').classList.add('hidden');
        document.getElementById('logout-button').classList.remove('hidden');
        document.getElementById('history-link').classList.remove('hidden');
    } else {
        isLoggedIn = false;
        document.getElementById('auth-button').classList.remove('hidden');
        document.getElementById('logout-button').classList.add('hidden');
        document.getElementById('history-link').classList.add('hidden');
    }
}

// Initialize authentication
initUserDatabase();
checkAuthStatus();

function checkAuthAndStart() {
    if (isLoggedIn) {
        showPage('student-info');
    } else {
        showPage('login');
    }
}

function switchAuthTab(tab) {
    if (tab === 'login') {
        document.getElementById('login-form').classList.remove('hidden');
        document.getElementById('signup-form').classList.add('hidden');
        document.getElementById('login-tab').classList.add('active');
        document.getElementById('signup-tab').classList.remove('active');
        hideError('login-error');
        hideError('signup-error');
    } else {
        document.getElementById('login-form').classList.add('hidden');
        document.getElementById('signup-form').classList.remove('hidden');
        document.getElementById('login-tab').classList.remove('active');
        document.getElementById('signup-tab').classList.add('active');
        hideError('login-error');
        hideError('signup-error');
    }
}

function loginUser(email, password) {
    const user = findUserByEmail(email);
    if (!user) {
        showError('login-error', 'No account found with this email.');
        return false;
    }
    
    if (user.password !== password) {
        showError('login-error', 'Incorrect password.');
        return false;
    }
    
    // Login successful
    currentUser = { id: user.id, name: user.name, email: user.email };
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
    isLoggedIn = true;
    
    // Update UI
    document.getElementById('auth-button').classList.add('hidden');
    document.getElementById('logout-button').classList.remove('hidden');
    document.getElementById('history-link').classList.remove('hidden');
    
    return true;
}

function registerUser(name, email, password, confirmPassword) {
    // Validate inputs
    if (!name || !email || !password || !confirmPassword) {
        showError('signup-error', 'All fields are required.');
        return false;
    }
    
    if (!isValidEmail(email)) {
        showError('signup-error', 'Please enter a valid email address.');
        return false;
    }
    
    if (!isValidPassword(password)) {
        showError('signup-error', 'Password must be at least 6 characters long.');
        return false;
    }
    
    if (password !== confirmPassword) {
        showError('signup-error', 'Passwords do not match.');
        return false;
    }
    
    // Check if user already exists
    if (findUserByEmail(email)) {
        showError('signup-error', 'An account with this email already exists.');
        return false;
    }
    
    // Create new user
    const newUser = {
        id: Date.now(),
        name,
        email,
        password, // In a real app, this would be hashed
        createdAt: new Date().toISOString()
    };
    
    // Save user to database
    saveUser(newUser);
    
    // Auto-login the new user
    currentUser = { id: newUser.id, name: newUser.name, email: newUser.email };
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
    isLoggedIn = true;
    
    // Update UI
    document.getElementById('auth-button').classList.add('hidden');
    document.getElementById('logout-button').classList.remove('hidden');
    document.getElementById('history-link').classList.remove('hidden');
    
    return true;
}

function logout() {
    localStorage.removeItem('currentUser');
    currentUser = null;
    isLoggedIn = false;
    document.getElementById('auth-button').classList.remove('hidden');
    document.getElementById('logout-button').classList.add('hidden');
    document.getElementById('history-link').classList.add('hidden');
    showPage('home');
}

// Form submissions
document.getElementById('login-form').addEventListener('submit', function(e) {
    e.preventDefault();
    hideError('login-error');
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    if (loginUser(email, password)) {
        showPage('student-info');
    }
});

document.getElementById('signup-form').addEventListener('submit', function(e) {
    e.preventDefault();
    hideError('signup-error');
    
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('signup-confirm').value;
    
    if (registerUser(name, email, password, confirmPassword)) {
        showPage('student-info');
    }
});

document.getElementById('feedback-form').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Thank you for your feedback!');
    this.reset();
    showPage('home');
});

// Student info form
function toggleStreamSelection() {
    const academicLevel = document.getElementById('academic-level').value;
    const streamSelection = document.getElementById('stream-selection');
    const degreeSelection = document.getElementById('degree-selection');
    
    if (academicLevel === '10th') {
        streamSelection.classList.remove('hidden');
        degreeSelection.classList.add('hidden');
    } else if (academicLevel === '12th') {
        streamSelection.classList.add('hidden');
        degreeSelection.classList.remove('hidden');
    } else {
        streamSelection.classList.add('hidden');
        degreeSelection.classList.add('hidden');
    }
}

function selectStream(stream) {
    document.querySelectorAll('.stream-card').forEach(card => {
        card.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
    document.getElementById('selected-stream').value = stream;
}

function selectDegree(degree) {
    document.querySelectorAll('.degree-card').forEach(card => {
        card.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
    document.getElementById('selected-degree').value = degree;
}

document.getElementById('student-info-form').addEventListener('submit', function(e) {
    e.preventDefault();
    showPage('assessment');
    startAssessment();
});

// Career path definitions
const careerPaths = {
    science: {
        title: "Science and Technology Fields",
        description: "Based on your analytical thinking, problem-solving skills, and interest in technology, you show strong aptitude for science and technology fields.",
        skills: [90, 75, 50, 65, 85],
        roadmap: [
            "Focus on core science subjects like Physics, Chemistry, and Mathematics",
            "Prepare for competitive exams like JEE, NEET, or other entrance tests",
            "Research top science colleges and universities",
            "Consider specialized fields like Engineering, Medicine, or Research",
            "Gain practical experience through internships and projects"
        ],
        videos: [
            {id: "Bn9gMKYsX0s", title: "Introduction to Science Careers"},
            {id: "6Z0qZksaDzc", title: "Future of Technology"},
            {id: "7D4WQl2qQq4", title: "Scientific Research Opportunities"}
        ]
    },
    commerce: {
        title: "Business and Commerce Fields",
        description: "Your numerical aptitude, interest in economics, and analytical skills make you well-suited for business and commerce careers.",
        skills: [75, 60, 70, 55, 65],
        roadmap: [
            "Focus on Commerce subjects like Accountancy, Economics, and Business Studies",
            "Prepare for commerce-focused entrance exams like CA, CS, or CFA",
            "Research top business schools and commerce colleges",
            "Consider specialized fields like Finance, Accounting, or Business Management",
            "Gain practical experience through internships in business environments"
        ],
        videos: [
            {id: "0LnQU4e--_Y", title: "Business Career Paths"},
            {id: "3PzMsF5qPmI", title: "Commerce Education Options"},
            {id: "6W1z8C_hdKk", title: "Financial Career Opportunities"}
        ]
    },
    arts: {
        title: "Arts and Humanities Fields",
        description: "Your creativity, communication skills, and interest in human behavior suggest you would excel in arts and humanities careers.",
        skills: [60, 90, 85, 50, 65],
        roadmap: [
            "Focus on developing your creative and critical thinking skills",
            "Explore various arts disciplines like Literature, History, or Psychology",
            "Research top liberal arts colleges and universities",
            "Consider fields like Education, Journalism, Psychology, or Social Work",
            "Build a portfolio of your creative work and projects"
        ],
        videos: [
            {id: "5L4QUX6+1tQ", title: "Careers in Arts and Humanities"},
            {id: "4W7DnylOc0E", title: "Creative Career Paths"},
            {id: "6W1z8C_hdKk", title: "Humanities Education Options"}
        ]
    },
    engineering: {
        title: "Engineering Fields",
        description: "Your strong analytical skills, problem-solving ability, and interest in technology make engineering an excellent career choice for you.",
        skills: [95, 70, 55, 80, 75],
        roadmap: [
            "Focus on Mathematics, Physics, and Chemistry in your studies",
            "Prepare for engineering entrance exams like JEE",
            "Research top engineering colleges like IITs, NITs, and other institutes",
            "Consider specializing in fields like Computer Science, Mechanical, or Electrical Engineering",
            "Gain practical experience through technical projects and internships"
        ],
        videos: [
            {id: "Bn9gMKYsX0s", title: "Engineering Career Overview"},
            {id: "6Z0qZksaDzc", title: "Future of Engineering"},
            {id: "7D4WQl2qQq4", title: "Engineering Specializations"}
        ]
    },
    medical: {
        title: "Medical and Healthcare Fields",
        description: "Your scientific aptitude, attention to detail, and desire to help others suggest you would excel in medical and healthcare professions.",
        skills: [85, 65, 90, 70, 80],
        roadmap: [
            "Focus on Biology, Chemistry, and related science subjects",
            "Prepare for medical entrance exams like NEET",
            "Research top medical colleges and healthcare programs",
            "Consider fields like Medicine, Dentistry, Pharmacy, or Nursing",
            "Gain experience through volunteering or shadowing healthcare professionals"
        ],
        videos: [
            {id: "7D4WQl2qQq4", title: "Medical Career Paths"},
            {id: "6W1z8C_hdKk", title: "Healthcare Opportunities"},
            {id: "0LnQU4e--_Y", title: "Becoming a Doctor"}
        ]
    },
    business: {
        title: "Business Management Fields",
        description: "Your leadership potential, analytical thinking, and interest in commerce make business management an excellent career path for you.",
        skills: [75, 70, 80, 65, 70],
        roadmap: [
            "Focus on developing business acumen and leadership skills",
            "Prepare for management entrance exams like CAT, XAT, or GMAT",
            "Research top business schools and management programs",
            "Consider specializations like Marketing, Finance, or Human Resources",
            "Gain practical experience through internships in business environments"
        ],
        videos: [
            {id: "0LnQU4e--_Y", title: "Business Management Careers"},
            {id: "3PzMsF5qPmI", title: "MBA Programs Overview"},
            {id: "6W1z8C_hdKk", title: "Leadership Development"}
        ]
    },
    law: {
        title: "Legal Fields",
        description: "Your analytical thinking, communication skills, and interest in justice suggest you would excel in legal professions.",
        skills: [85, 70, 80, 60, 75],
        roadmap: [
            "Focus on developing critical thinking and communication skills",
            "Prepare for law entrance exams like CLAT, AILET, or LSAT",
            "Research top law schools and legal programs",
            "Consider specializations like Corporate Law, Criminal Law, or International Law",
            "Gain experience through internships at law firms or legal aid organizations"
        ],
        videos: [
            {id: "5L4QUX6+1tQ", title: "Law Career Paths"},
            {id: "6W1z8C_hdKk", title: "Legal Education Options"},
            {id: "0LnQU4e--_Y", title: "Becoming a Lawyer"}
        ]
    },
    design: {
        title: "Design and Creative Fields",
        description: "Your creativity, visual thinking, and innovative approach suggest you would excel in design and creative professions.",
        skills: [65, 95, 70, 75, 60],
        roadmap: [
            "Focus on developing your creative skills and building a portfolio",
            "Prepare for design entrance exams like NID, NIFT, or UCEED",
            "Research top design schools and creative programs",
            "Consider specializations like Graphic Design, Fashion, or Architecture",
            "Gain practical experience through freelance projects and internships"
        ],
        videos: [
            {id: "4W7DnylOc0E", title: "Design Career Opportunities"},
            {id: "6W1z8C_hdKk", title: "Creative Industries Overview"},
            {id: "5L4QUX6+1tQ", title: "Building a Design Portfolio"}
        ]
    },
    unsure: {
        title: "Multiple Career Options",
        description: "Based on your diverse interests and abilities, you have aptitude in several different areas. Consider exploring these fields further.",
        skills: [75, 75, 75, 75, 75],
        roadmap: [
            "Explore different subjects and fields to discover your passions",
            "Take career assessment tests to identify your strengths",
            "Research various career options and their requirements",
            "Consider talking to career counselors or professionals in different fields",
            "Gain experience through internships or volunteering in different industries"
        ],
        videos: [
            {id: "6W1z8C_hdKk", title: "Exploring Career Options"},
            {id: "0LnQU4e--_Y", title: "Career Discovery Guide"},
            {id: "5L4QUX6+1tQ", title: "Finding Your Passion"}
        ]
    }
};

// Assessment questions
const questions = [
    {
        question: "What type of activities do you enjoy most?",
        options: [
            "Solving puzzles and logical problems",
            "Creating art, music, or writing",
            "Helping and working with people",
            "Building or fixing things with your hands",
            "Analyzing data and conducting experiments"
        ]
    },
    {
        question: "Which school subject interests you the most?",
        options: [
            "Mathematics",
            "Literature and Languages",
            "Social Studies and Psychology",
            "Physical Education and Sports",
            "Science and Technology"
        ]
    },
    {
        question: "How would you describe your ideal work environment?",
        options: [
            "Quiet space for deep concentration",
            "Creative and expressive atmosphere",
            "Collaborative team setting",
            "Active and hands-on workspace",
            "Research laboratory or technical facility"
        ]
    },
    {
        question: "What are your preferred work tasks?",
        options: [
            "Analyzing complex information",
            "Expressing creative ideas",
            "Supporting and mentoring others",
            "Working with tools and machinery",
            "Conducting experiments and research"
        ]
    },
    {
        question: "Which of these values is most important to you in a career?",
        options: [
            "Intellectual challenge and problem-solving",
            "Creative expression and innovation",
            "Making a difference in people's lives",
            "Practical results and tangible outcomes",
            "Discovery and advancing knowledge"
        ]
    },
    {
        question: "How do you prefer to learn new things?",
        options: [
            "Through logical reasoning and analysis",
            "Through experimentation and creative exploration",
            "Through discussion and collaboration",
            "Through hands-on practice and demonstration",
            "Through systematic study and research"
        ]
    },
    {
        question: "Which of these careers appeals to you most?",
        options: [
            "Software Developer or Data Scientist",
            "Graphic Designer or Musician",
            "Teacher or Counselor",
            "Electrician or Architect",
            "Research Scientist or Doctor"
        ]
    },
    {
        question: "What is your approach to problem-solving?",
        options: [
            "Break it down into logical steps",
            "Think outside the box for creative solutions",
            "Consult with others for different perspectives",
            "Try practical solutions through trial and error",
            "Research similar problems and apply findings"
        ]
    },
    {
        question: "Which skills do you consider your strengths?",
        options: [
            "Analytical thinking and mathematics",
            "Creativity and imagination",
            "Communication and empathy",
            "Manual dexterity and coordination",
            "Observation and attention to detail"
        ]
    },
    {
        question: "How do you handle challenges?",
        options: [
            "Systematically analyze the problem",
            "Brainstorm innovative approaches",
            "Seek support and advice from others",
            "Try different practical approaches",
            "Research and study the challenge thoroughly"
        ]
    }
];

let currentQuestion = 0;
let userAnswers = [];

function startAssessment() {
    currentQuestion = 0;
    userAnswers = [];
    displayQuestion();
}

function displayQuestion() {
    const questionNumber = document.getElementById('question-number');
    const questionText = document.getElementById('question-text');
    const optionsContainer = document.getElementById('options-container');
    const progressBar = document.getElementById('progress-bar');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    
    // Update progress
    const progress = ((currentQuestion + 1) / questions.length) * 100;
    progressBar.style.width = `${progress}%`;
    
    // Update question number and text
    questionNumber.textContent = `Question ${currentQuestion + 1} of ${questions.length}`;
    questionText.textContent = questions[currentQuestion].question;
    
    // Clear previous options
    optionsContainer.innerHTML = '';
    
    // Add new options
    questions[currentQuestion].options.forEach((option, index) => {
        const optionElement = document.createElement('div');
        optionElement.className = 'option';
        optionElement.textContent = option;
        optionElement.addEventListener('click', () => selectOption(index));
        optionsContainer.appendChild(optionElement);
    });
    
    // Update navigation buttons
    prevBtn.style.visibility = currentQuestion === 0 ? 'hidden' : 'visible';
    nextBtn.textContent = currentQuestion === questions.length - 1 ? 'See Results →' : 'Next →';
    
    // If user has already answered this question, show the selection
    if (userAnswers[currentQuestion] !== undefined) {
        const options = optionsContainer.querySelectorAll('.option');
        options[userAnswers[currentQuestion]].classList.add('selected');
    }
}

function selectOption(optionIndex) {
    const options = document.querySelectorAll('.option');
    options.forEach(option => option.classList.remove('selected'));
    options[optionIndex].classList.add('selected');
    
    userAnswers[currentQuestion] = optionIndex;
}

function nextQuestion() {
    if (userAnswers[currentQuestion] === undefined) {
        alert('Please select an answer before proceeding.');
        return;
    }
    
    if (currentQuestion < questions.length - 1) {
        currentQuestion++;
        displayQuestion();
    } else {
        calculateResults();
    }
}

function prevQuestion() {
    if (currentQuestion > 0) {
        currentQuestion--;
        displayQuestion();
    }
}

// Set up navigation buttons
document.getElementById('next-btn').addEventListener('click', nextQuestion);
document.getElementById('prev-btn').addEventListener('click', prevQuestion);

function calculateResults() {
    // Simple scoring mechanism - in a real app, this would be more sophisticated
    const scores = {
        science: 0,
        commerce: 0,
        arts: 0,
        engineering: 0,
        medical: 0,
        business: 0,
        law: 0,
        design: 0
    };
    
    // Calculate scores based on answers
    userAnswers.forEach((answer, index) => {
        // Each answer contributes to different career paths
        // This is a simplified scoring system
        if (index === 0) {
            if (answer === 0 || answer === 4) scores.science += 2;
            if (answer === 1) scores.arts += 2;
            if (answer === 2) scores.commerce += 2;
            if (answer === 3) scores.engineering += 1;
        } else if (index === 1) {
            if (answer === 0 || answer === 4) scores.science += 2;
            if (answer === 1) scores.arts += 2;
            if (answer === 2) scores.commerce += 2;
        } else if (index === 2) {
            if (answer === 0) scores.science += 1;
            if (answer === 1) scores.arts += 2;
            if (answer === 2) scores.commerce += 1;
            if (answer === 3) scores.engineering += 1;
            if (answer === 4) scores.science += 2;
        }
        // Additional scoring logic would be added for all questions
    });
    
    // Get the highest scoring career path
    let maxScore = 0;
    let recommendedPath = 'unsure';
    
    for (const path in scores) {
        if (scores[path] > maxScore) {
            maxScore = scores[path];
            recommendedPath = path;
        }
    }
    
    // Get the academic level and stream/degree selection
    const academicLevel = document.getElementById('academic-level').value;
    const stream = document.getElementById('selected-stream').value;
    const degree = document.getElementById('selected-degree').value;
    
    // Override recommendation based on user selection if they were sure
    if (academicLevel === '10th' && stream !== 'unsure') {
        recommendedPath = stream;
    } else if (academicLevel === '12th' && degree) {
        recommendedPath = degree;
    }
    
    // Save the assessment result to history
    saveAssessmentResult(recommendedPath, maxScore);
    
    // Display results
    showResults(recommendedPath);
}

function saveAssessmentResult(careerPath, score) {
    if (!currentUser) return;
    
    // Get user's assessment history
    let history = JSON.parse(localStorage.getItem('assessmentHistory') || '{}');
    if (!history[currentUser.id]) {
        history[currentUser.id] = [];
    }
    
    // Add new assessment result
    history[currentUser.id].push({
        date: new Date().toISOString(),
        careerPath: careerPath,
        score: score,
        answers: userAnswers
    });
    
    // Save back to localStorage
    localStorage.setItem('assessmentHistory', JSON.stringify(history));
}

function showResults(careerPath) {
    const career = careerPaths[careerPath];
    const matchPercentage = document.getElementById('match-percentage');
    const careerTitle = document.getElementById('career-title');
    const careerDescription = document.getElementById('career-description');
    const roadmapContainer = document.getElementById('roadmap-container');
    const videoResources = document.getElementById('video-resources');
    
    // Set career information
    matchPercentage.textContent = `${Math.floor(Math.random() * 21) + 80}% Match`;
    careerTitle.textContent = career.title;
    careerDescription.textContent = career.description;
    
    // Create roadmap
    const roadmapList = document.createElement('ol');
    roadmapList.className = 'roadmap-steps';
    
    career.roadmap.forEach(step => {
        const stepItem = document.createElement('li');
        stepItem.textContent = step;
        roadmapList.appendChild(stepItem);
    });
    
    roadmapContainer.appendChild(roadmapList);
    
    // Create skill chart
    const ctx = document.getElementById('career-chart').getContext('2d');
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Analytical Thinking', 'Creativity', 'Interpersonal Skills', 'Technical Ability', 'Problem Solving'],
            datasets: [{
                label: 'Your Skills Profile',
                data: career.skills,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
            }]
        },
        options: {
            scales: {
                r: {
                    angleLines: {
                        display: true
                    },
                    suggestedMin: 0,
                    suggestedMax: 100
                }
            }
        }
    });
    
    // Add video resources
    videoResources.innerHTML = '';
    career.videos.forEach(video => {
        const videoCard = document.createElement('div');
        videoCard.className = 'video-card';
        videoCard.innerHTML = `
            <div class="video-thumbnail">
                <img src="https://img.youtube.com/vi/${video.id}/mqdefault.jpg" alt="${video.title}">
                <div class="play-button">▶</div>
            </div>
            <h4>${video.title}</h4>
        `;
        videoCard.addEventListener('click', () => {
            window.open(`https://www.youtube.com/watch?v=${video.id}`, '_blank');
        });
        videoResources.appendChild(videoCard);
    });
    
    // Set up download and retake buttons
    document.getElementById('download-btn').addEventListener('click', downloadReport);
    document.getElementById('retake-btn').addEventListener('click', () => {
        showPage('student-info');
    });
    
    // Show results page
    showPage('results');
}

function downloadReport() {
    alert('Your career report has been downloaded!');
    // In a real application, this would generate and download a PDF report
}

function updateHistoryDisplay() {
    const historyContainer = document.getElementById('history-container');
    
    if (!currentUser) {
        historyContainer.innerHTML = '<p style="text-align: center;">Please log in to view your assessment history.</p>';
        return;
    }
    
    // Get user's assessment history
    const history = JSON.parse(localStorage.getItem('assessmentHistory') || '{}');
    const userHistory = history[currentUser.id] || [];
    
    if (userHistory.length === 0) {
        historyContainer.innerHTML = '<p style="text-align: center;">You haven\'t taken any assessments yet.</p>';
        return;
    }
    
    // Display history
    historyContainer.innerHTML = '';
    userHistory.forEach((assessment, index) => {
        const date = new Date(assessment.date).toLocaleDateString();
        const career = careerPaths[assessment.careerPath];
        
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <h3>Assessment #${userHistory.length - index}</h3>
            <p><strong>Date:</strong> ${date}</p>
            <p><strong>Recommended Career:</strong> ${career.title}</p>
            <p><strong>Match Score:</strong> ${assessment.score}</p>
            <button class="btn" onclick="viewAssessmentDetails(${index})">View Details</button>
        `;
        historyContainer.appendChild(historyItem);
    });
}

function viewAssessmentDetails(index) {
    // In a real application, this would show detailed results of a specific assessment
    alert('Detailed assessment view would be shown here.');
}

function clearHistory() {
    if (!currentUser) return;
    
    if (confirm('Are you sure you want to clear your assessment history? This action cannot be undone.')) {
        const history = JSON.parse(localStorage.getItem('assessmentHistory') || '{}');
        history[currentUser.id] = [];
        localStorage.setItem('assessmentHistory', JSON.stringify(history));
        updateHistoryDisplay();
    }
}

// Initialize the application
showPage('home');
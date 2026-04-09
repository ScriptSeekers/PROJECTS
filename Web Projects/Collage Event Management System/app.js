import DB from './db.js';

// Application State
let currentUser = null;
let currentRole = 'STUDENT';
let currentView = 'dashboard';

// --- Auth Functions ---
window.setRole = (role) => {
    currentRole = role;
    document.querySelectorAll('.auth-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.role === role);
    });
    // Toggle registration based on role (only students can register)
    document.getElementById('reg-toggle').style.display = role === 'STUDENT' ? 'block' : 'none';
};

window.toggleAuth = (isRegister) => {
    document.getElementById('login-form').style.display = isRegister ? 'none' : 'block';
    document.getElementById('register-form').style.display = isRegister ? 'block' : 'none';
};

window.handleLogin = () => {
    const email = document.getElementById('login-email').value;
    const pass = document.getElementById('login-pass').value;

    const user = DB.findUser(email, pass, currentRole);
    if (user) {
        currentUser = user;
        showApp();
    } else {
        alert('Invalid credentials for selected role');
    }
};

window.handleRegister = () => {
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const pass = document.getElementById('reg-pass').value;

    if (!name || !email || !pass) return alert('All fields required');

    const newUser = DB.addUser({ name, email, password: pass, role: 'STUDENT' });
    currentUser = newUser;
    showApp();
};

window.logout = () => {
    currentUser = null;
    document.getElementById('auth-screen').style.display = 'flex';
    document.getElementById('app-screen').style.display = 'none';
    resetAuthForms();
};

function resetAuthForms() {
    document.querySelectorAll('input').forEach(i => i.value = '');
    toggleAuth(false);
}

// --- Navigation & Views ---
function showApp() {
    document.getElementById('auth-screen').style.display = 'none';
    document.getElementById('app-screen').style.display = 'flex';
    document.getElementById('user-welcome').textContent = `Welcome back, ${currentUser.name}`;
    renderSidebar();
    setView('dashboard');
}

function renderSidebar() {
    const nav = document.getElementById('nav-links');
    nav.innerHTML = `
        <div class="nav-item active" onclick="setView('dashboard')">
            <i class="fas fa-th-large"></i> Dashboard
        </div>
    `;

    if (currentUser.role === 'STUDENT') {
        nav.innerHTML += `
            <div class="nav-item" onclick="setView('events')">
                <i class="fas fa-calendar-alt"></i> Available Events
            </div>
            <div class="nav-item" onclick="setView('my-requests')">
                <i class="fas fa-clipboard-list"></i> My Requests
            </div>
        `;
    } else if (currentUser.role === 'LEADER') {
        nav.innerHTML += `
            <div class="nav-item" onclick="setView('create-event')">
                <i class="fas fa-plus-circle"></i> Create Event
            </div>
            <div class="nav-item" onclick="setView('my-events')">
                <i class="fas fa-star"></i> My Managed Events
            </div>
        `;
    } else if (currentUser.role === 'TEACHER') {
        nav.innerHTML += `
            <div class="nav-item" onclick="setView('manage-leaders')">
                <i class="fas fa-users-cog"></i> Add Event Leaders
            </div>
            <div class="nav-item" onclick="setView('requests-approval')">
                <i class="fas fa-check-circle"></i> Approve Participation
            </div>
        `;
    } else if (currentUser.role === 'PRINCIPAL') {
        nav.innerHTML += `
            <div class="nav-item" onclick="setView('manage-teachers')">
                <i class="fas fa-user-tie"></i> Manage Teachers
            </div>
            <div class="nav-item" onclick="setView('manage-leaders')">
                <i class="fas fa-users-cog"></i> Manage Leaders
            </div>
            <div class="nav-item" onclick="setView('event-approvals')">
                <i class="fas fa-tasks"></i> Event Approvals
            </div>
        `;
    }
}

window.setView = (view) => {
    currentView = view;
    const content = document.getElementById('dashboard-content');
    const title = document.getElementById('page-title');
    const actions = document.getElementById('header-actions');
    actions.innerHTML = '';
    
    // Update active nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.textContent.toLowerCase().includes(view.replace('-', ' ')));
    });

    switch(view) {
        case 'dashboard':
            title.textContent = 'Dashboard Overview';
            renderDashboardStats(content);
            break;
        case 'events':
            title.textContent = 'Upcoming Campus Events';
            renderEventsList(content, true);
            break;
        case 'my-requests':
            title.textContent = 'My Participation History';
            renderStudentRequests(content);
            break;
        case 'create-event':
            title.textContent = 'Host New Event';
            renderEventForm(content);
            break;
        case 'my-events':
            title.textContent = 'Manage Your Events';
            renderEventsList(content, false, currentUser.id);
            break;
        case 'event-approvals':
            title.textContent = 'Review Pending Events';
            renderEventReviewList(content);
            break;
        case 'requests-approval':
            title.textContent = 'Verify Student Participations';
            renderParticipationReviewList(content);
            break;
        case 'manage-teachers':
            title.textContent = 'Administrative Staff';
            renderManageUsers(content, 'TEACHER');
            break;
        case 'manage-leaders':
            title.textContent = 'Student Organizations';
            renderManageUsers(content, 'LEADER');
            break;
    }
};

// --- View Renderers ---

function renderDashboardStats(container) {
    const events = DB.getEvents();
    const requests = DB.getRequests();
    
    let stats = [];
    if (currentUser.role === 'STUDENT') {
        stats = [
            { icon: 'fa-calendar-check', label: 'Approved Events', value: events.filter(e => e.status === 'APPROVED').length },
            { icon: 'fa-hourglass-half', label: 'My Pending Requests', value: requests.filter(r => r.student_id === currentUser.id && r.status === 'PENDING').length },
            { icon: 'fa-award', label: 'Reward Points', value: requests.filter(r => r.student_id === currentUser.id && r.status === 'APPROVED').length * 50 }
        ];
    } else if (currentUser.role === 'PRINCIPAL') {
        stats = [
            { icon: 'fa-tasks', label: 'Events to Review', value: events.filter(e => e.status === 'PENDING').length },
            { icon: 'fa-user-tie', label: 'Total Staff', value: DB.getUsers().filter(u => u.role === 'TEACHER').length },
            { icon: 'fa-users', label: 'Active Leaders', value: DB.getUsers().filter(u => u.role === 'LEADER').length }
        ];
    } else if (currentUser.role === 'TEACHER') {
        stats = [
            { icon: 'fa-user-check', label: 'Requests for Review', value: requests.filter(r => r.status === 'PENDING').length },
            { icon: 'fa-calendar-alt', label: 'Assigned Events', value: events.filter(e => e.teacher_id == currentUser.id).length }
        ];
    } else if (currentUser.role === 'LEADER') {
        stats = [
            { icon: 'fa-star', label: 'My Events', value: events.filter(e => e.leader_id === currentUser.id).length },
            { icon: 'fa-check-circle', label: 'Approved Status', value: events.filter(e => e.leader_id === currentUser.id && e.status === 'APPROVED').length }
        ];
    }

    container.innerHTML = `
        <div class="stats-grid">
            ${stats.map(s => `
                <div class="stat-card glass card-hover animate-fade">
                    <i class="fas ${s.icon}"></i>
                    <div class="value">${s.value}</div>
                    <div class="label">${s.label}</div>
                </div>
            `).join('')}
        </div>
        <div class="glass animate-fade" style="padding: 30px;">
            <h3>Quick Announcements</h3>
            <p style="color: var(--text-muted); margin-top: 15px;">Welcome to the new ScriptSeekers system. Please ensure your personal details are updated.</p>
        </div>
    `;
}

function renderEventsList(container, onlyApproved, leaderId = null) {
    let events = DB.getEvents();
    if (onlyApproved) events = events.filter(e => e.status === 'APPROVED');
    if (leaderId) events = events.filter(e => e.leader_id === leaderId);

    container.innerHTML = `
        <div class="table-container glass animate-fade">
            <table>
                <thead>
                    <tr>
                        <th>Event Name</th>
                        <th>Organizer</th>
                        <th>Date & Time</th>
                        <th>Location</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    ${events.map(e => `
                        <tr>
                            <td style="font-weight: 700;">${e.name}</td>
                            <td>${e.host_name || 'Organization'}</td>
                            <td>${new Date(e.date).toLocaleDateString()} at ${e.time}</td>
                            <td>${e.location}</td>
                            <td><span class="status-badge status-${e.status}">${e.status}</span></td>
                            <td>
                                ${currentUser.role === 'STUDENT' ? 
                                    `<button class="btn btn-primary" style="padding: 8px 16px; font-size: 0.8rem;" onclick="openParticipationModal(${e.id})">Join Event</button>` : 
                                    `<button class="btn" style="padding: 8px 16px; font-size: 0.8rem; background: rgba(255,255,255,0.05);">Details</button>`
                                }
                            </td>
                        </tr>
                    `).join('')}
                    ${events.length === 0 ? '<tr><td colspan="6" style="text-align:center; padding: 40px; color:var(--text-muted)">No events found</td></tr>' : ''}
                </tbody>
            </table>
        </div>
    `;
}

function renderEventForm(container) {
    const teachers = DB.getUsers().filter(u => u.role === 'TEACHER');
    
    container.innerHTML = `
        <div class="glass animate-fade" style="max-width: 800px; padding: 40px;">
            <div class="grid-2" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div class="input-group">
                    <label>Event Name</label>
                    <input type="text" id="ev-name" placeholder="Annual Music Fest">
                </div>
                <div class="input-group">
                    <label>Teacher Coordinator</label>
                    <select id="ev-teacher">
                        ${teachers.map(t => `<option value="${t.id}">${t.name} (${t.email})</option>`).join('')}
                    </select>
                </div>
            </div>
            <div class="input-group">
                <label>Description</label>
                <textarea id="ev-desc" style="height: 100px;" placeholder="Tell us about the event..."></textarea>
            </div>
            <div class="grid-2" style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;">
                <div class="input-group">
                    <label>Date</label>
                    <input type="date" id="ev-date">
                </div>
                <div class="input-group">
                    <label>Time</label>
                    <input type="time" id="ev-time">
                </div>
                <div class="input-group">
                    <label>Location</label>
                    <input type="text" id="ev-loc" placeholder="Auditorium">
                </div>
            </div>
            <button class="btn btn-primary" onclick="submitEvent()">Submit for Approval</button>
        </div>
    `;
}

window.submitEvent = () => {
    const event = {
        name: document.getElementById('ev-name').value,
        teacher_id: document.getElementById('ev-teacher').value,
        desc: document.getElementById('ev-desc').value,
        date: document.getElementById('ev-date').value,
        time: document.getElementById('ev-time').value,
        location: document.getElementById('ev-loc').value,
        leader_id: currentUser.id,
        host_name: currentUser.name
    };

    if (!event.name || !event.date) return alert('Name and Date are required');
    
    DB.addEvent(event);
    alert('Event submitted successfully!');
    setView('my-events');
};

function renderEventReviewList(container) {
    const events = DB.getEvents().filter(e => e.status === 'PENDING');
    
    container.innerHTML = `
        <div class="table-container glass animate-fade">
            <table>
                <thead>
                    <tr>
                        <th>Event</th>
                        <th>Leader</th>
                        <th>Teacher</th>
                        <th>Details</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    ${events.map(e => `
                        <tr>
                            <td>${e.name}</td>
                            <td>${e.host_name}</td>
                            <td>${DB.getUsers().find(u => u.id == e.teacher_id)?.name}</td>
                            <td style="font-size: 0.8rem; color: var(--text-muted); max-width: 200px;">${e.date} @ ${e.location}</td>
                            <td>
                                <button class="btn" style="color: var(--success); background: rgba(16, 185, 129, 0.1);" onclick="processEvent(${e.id}, 'APPROVED')">Approve</button>
                                <button class="btn" style="color: var(--danger); background: rgba(239, 68, 68, 0.1);" onclick="processEvent(${e.id}, 'REJECTED')">Reject</button>
                            </td>
                        </tr>
                    `).join('')}
                    ${events.length === 0 ? '<tr><td colspan="5" style="text-align:center; padding: 40px;">No pending approvals</td></tr>' : ''}
                </tbody>
            </table>
        </div>
    `;
}

window.processEvent = (id, status) => {
    DB.updateEventStatus(id, status, currentUser.id);
    setView('event-approvals');
};

function renderManageUsers(container, role) {
    container.innerHTML = `
        <div class="glass animate-fade" style="margin-bottom: 30px; padding: 30px;">
            <h3>Add New ${role === 'TEACHER' ? 'Teacher' : 'Event Leader'}</h3>
            <div style="display: flex; gap: 20px; margin-top: 20px;">
                <input type="text" id="new-u-name" placeholder="Name">
                <input type="email" id="new-u-email" placeholder="Email">
                <input type="password" id="new-u-pass" placeholder="Initial Password">
                <button class="btn btn-primary" onclick="createNewUser('${role}')">Add User</button>
            </div>
        </div>
        <div class="table-container glass animate-fade">
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${DB.getUsers().filter(u => u.role === role).map(u => `
                        <tr>
                            <td>${u.name}</td>
                            <td>${u.email}</td>
                            <td><button class="btn" style="color: var(--danger);">Remove</button></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

window.createNewUser = (role) => {
    const name = document.getElementById('new-u-name').value;
    const email = document.getElementById('new-u-email').value;
    const pass = document.getElementById('new-u-pass').value;

    if (!name || !email || !pass) return alert('All fields required');
    
    DB.addUser({ name, email, password: pass, role });
    alert(`${role} added successfully!`);
    setView(currentView);
};

// --- Participation Modal Logic ---
window.openParticipationModal = (eventId) => {
    const event = DB.getEvents().find(e => e.id === eventId);
    const modal = document.getElementById('modal-container');
    modal.style.display = 'flex';
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal glass animate-fade">
            <h2 class="gradient-text">Join ${event.name}</h2>
            <p style="color: var(--text-muted); margin: 20px 0;">Select how you'd like to participate in this event.</p>
            
            <div class="input-group">
                <label>Role</label>
                <select id="part-type">
                    <option value="AUDIENCE">Audience Member</option>
                    <option value="VOLUNTEER">Event Volunteer</option>
                </select>
            </div>
            
            <div style="display: flex; gap: 15px; margin-top: 30px;">
                <button class="btn btn-primary" style="flex: 1;" onclick="submitParticipation(${eventId})">Submit Request</button>
                <button class="btn" style="flex: 1; background: rgba(255,255,255,0.1);" onclick="closeModal()">Cancel</button>
            </div>
        </div>
    `;
};

window.closeModal = () => {
    document.getElementById('modal-container').style.display = 'none';
};

window.submitParticipation = (eventId) => {
    const type = document.getElementById('part-type').value;
    DB.addRequest({
        student_id: currentUser.id,
        student_name: currentUser.name,
        event_id: eventId,
        event_name: DB.getEvents().find(e => e.id === eventId).name,
        type: type
    });
    alert('Request sent to coordinator!');
    closeModal();
    setView('my-requests');
};

function renderStudentRequests(container) {
    const reqs = DB.getRequests().filter(r => r.student_id === currentUser.id);
    container.innerHTML = `
        <div class="table-container glass animate-fade">
            <table>
                <thead>
                    <tr>
                        <th>Event</th>
                        <th>Type</th>
                        <th>Requested On</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${reqs.map(r => `
                        <tr>
                            <td>${r.event_name}</td>
                            <td>${r.type}</td>
                            <td>${new Date(r.created_at).toLocaleDateString()}</td>
                            <td><span class="status-badge status-${r.status}">${r.status}</span></td>
                        </tr>
                    `).join('')}
                    ${reqs.length === 0 ? '<tr><td colspan="4" style="text-align:center; padding: 40px;">No requests found</td></tr>' : ''}
                </tbody>
            </table>
        </div>
    `;
}

function renderParticipationReviewList(container) {
    const reqs = DB.getRequests().filter(r => r.status === 'PENDING');
    container.innerHTML = `
        <div class="table-container glass animate-fade">
            <table>
                <thead>
                    <tr>
                        <th>Student</th>
                        <th>Event</th>
                        <th>Role</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    ${reqs.map(r => `
                        <tr>
                            <td>${r.student_name}</td>
                            <td>${r.event_name}</td>
                            <td>${r.type}</td>
                            <td>
                                <button class="btn" style="color: var(--success); background: rgba(16, 185, 129, 0.1);" onclick="processRequest(${r.id}, 'APPROVED')">Approve</button>
                                <button class="btn" style="color: var(--danger); background: rgba(239, 68, 68, 0.1);" onclick="processRequest(${r.id}, 'REJECTED')">Reject</button>
                            </td>
                        </tr>
                    `).join('')}
                    ${reqs.length === 0 ? '<tr><td colspan="4" style="text-align:center; padding: 40px;">Clear for now!</td></tr>' : ''}
                </tbody>
            </table>
        </div>
    `;
}

window.processRequest = (id, status) => {
    DB.updateRequestStatus(id, status, currentUser.id);
    setView('requests-approval');
};

// Start with Login Screen
document.addEventListener('DOMContentLoaded', () => {
    resetAuthForms();
});

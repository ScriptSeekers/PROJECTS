/**
 * Mock Database using localStorage
 * Mimics the Java DAO layer
 */
const DB = {
    // Initial Data
    init() {
        if (!localStorage.getItem('ev_users')) {
            const initialUsers = [
                {
                    id: 1,
                    name: 'Dr. Raj Kumar',
                    email: 'principal@college.com',
                    password: 'principal123',
                    role: 'PRINCIPAL'
                }
            ];
            localStorage.setItem('ev_users', JSON.stringify(initialUsers));
        }
        if (!localStorage.getItem('ev_events')) {
            localStorage.setItem('ev_events', JSON.stringify([]));
        }
        if (!localStorage.getItem('ev_requests')) {
            localStorage.setItem('ev_requests', JSON.stringify([]));
        }
    },

    // User Operations
    getUsers() {
        return JSON.parse(localStorage.getItem('ev_users') || '[]');
    },

    addUser(user) {
        const users = this.getUsers();
        user.id = Date.now();
        users.push(user);
        localStorage.setItem('ev_users', JSON.stringify(users));
        return user;
    },

    findUser(email, password, role) {
        const users = this.getUsers();
        return users.find(u => u.email === email && u.password === password && u.role === role);
    },

    // Event Operations
    getEvents() {
        return JSON.parse(localStorage.getItem('ev_events') || '[]');
    },

    addEvent(event) {
        const events = this.getEvents();
        event.id = Date.now();
        event.status = 'PENDING';
        event.created_at = new Date().toISOString();
        events.push(event);
        localStorage.setItem('ev_events', JSON.stringify(events));
        return event;
    },

    updateEventStatus(eventId, status, principalId) {
        let events = this.getEvents();
        events = events.map(e => {
            if (e.id === eventId) {
                return { ...e, status, approved_by: principalId, approval_date: new Date().toISOString() };
            }
            return e;
        });
        localStorage.setItem('ev_events', JSON.stringify(events));
    },

    // Participation Request Operations
    getRequests() {
        return JSON.parse(localStorage.getItem('ev_requests') || '[]');
    },

    addRequest(request) {
        const requests = this.getRequests();
        request.id = Date.now();
        request.status = 'PENDING';
        request.created_at = new Date().toISOString();
        requests.push(request);
        localStorage.setItem('ev_requests', JSON.stringify(requests));
        return request;
    },

    updateRequestStatus(requestId, status, teacherId) {
        let requests = this.getRequests();
        requests = requests.map(r => {
            if (r.id === requestId) {
                return { ...r, status, approved_by: teacherId, approval_date: new Date().toISOString() };
            }
            return r;
        });
        localStorage.setItem('ev_requests', JSON.stringify(requests));
    }
};

DB.init();
export default DB;

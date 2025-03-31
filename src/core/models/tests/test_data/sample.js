/**
 * Sample JavaScript file for testing code understanding capabilities.
 */

// User class definition
class User {
    /**
     * Create a new user.
     * @param {string} name - The user's name
     * @param {string} email - The user's email
     * @param {number} [age] - The user's age (optional)
     * @param {Object} [preferences] - User preferences (optional)
     */
    constructor(name, email, age = null, preferences = {}) {
        this.name = name;
        this.email = email;
        this.age = age;
        this.preferences = preferences;
    }
}

// UserManager class definition
class UserManager {
    /**
     * Create a new user manager.
     * @param {string} dataFile - Path to the JSON file storing user data
     */
    constructor(dataFile) {
        this.dataFile = dataFile;
        this.users = new Map();
        this.logger = console;
        this.loadUsers();
    }
    
    /**
     * Load users from the data file.
     * @private
     */
    async loadUsers() {
        try {
            const response = await fetch(this.dataFile);
            const data = await response.json();
            data.forEach(userData => {
                const user = new User(
                    userData.name,
                    userData.email,
                    userData.age,
                    userData.preferences
                );
                this.users.set(user.email, user);
            });
        } catch (error) {
            this.logger.error(`Error loading users: ${error}`);
            throw error;
        }
    }
    
    /**
     * Add a new user to the system.
     * @param {User} user - User object to add
     * @returns {boolean} True if user was added successfully
     */
    addUser(user) {
        try {
            if (this.users.has(user.email)) {
                return false;
            }
            this.users.set(user.email, user);
            this.saveUsers();
            return true;
        } catch (error) {
            this.logger.error(`Error adding user: ${error}`);
            return false;
        }
    }
    
    /**
     * Get a user by email.
     * @param {string} email - Email address of the user
     * @returns {User|null} User object if found, null otherwise
     */
    getUser(email) {
        return this.users.get(email) || null;
    }
    
    /**
     * Update user information.
     * @param {string} email - Email address of the user to update
     * @param {Object} updates - Fields to update
     * @returns {boolean} True if update was successful
     */
    updateUser(email, updates) {
        try {
            if (!this.users.has(email)) {
                return false;
            }
            const user = this.users.get(email);
            Object.entries(updates).forEach(([key, value]) => {
                if (user.hasOwnProperty(key)) {
                    user[key] = value;
                }
            });
            this.saveUsers();
            return true;
        } catch (error) {
            this.logger.error(`Error updating user: ${error}`);
            return false;
        }
    }
    
    /**
     * Delete a user from the system.
     * @param {string} email - Email address of the user to delete
     * @returns {boolean} True if deletion was successful
     */
    deleteUser(email) {
        try {
            if (!this.users.has(email)) {
                return false;
            }
            this.users.delete(email);
            this.saveUsers();
            return true;
        } catch (error) {
            this.logger.error(`Error deleting user: ${error}`);
            return false;
        }
    }
    
    /**
     * Get a list of all users.
     * @returns {User[]} List of all users
     */
    listUsers() {
        return Array.from(this.users.values());
    }
    
    /**
     * Save users to the data file.
     * @private
     */
    async saveUsers() {
        try {
            const data = Array.from(this.users.values()).map(user => ({
                name: user.name,
                email: user.email,
                age: user.age,
                preferences: user.preferences
            }));
            
            await fetch(this.dataFile, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data, null, 2)
            });
        } catch (error) {
            this.logger.error(`Error saving users: ${error}`);
            throw error;
        }
    }
    
    /**
     * Search users by name or email.
     * @param {string} query - Search query string
     * @returns {User[]} List of matching users
     */
    searchUsers(query) {
        query = query.toLowerCase();
        return Array.from(this.users.values()).filter(user =>
            user.name.toLowerCase().includes(query) ||
            user.email.toLowerCase().includes(query)
        );
    }
    
    /**
     * Get statistics about users.
     * @returns {Object} Dictionary containing user statistics
     */
    getUserStats() {
        return {
            totalUsers: this.users.size,
            usersWithAge: Array.from(this.users.values())
                .filter(user => user.age !== null).length,
            usersWithPreferences: Array.from(this.users.values())
                .filter(user => Object.keys(user.preferences).length > 0).length
        };
    }
}

// Example usage
const userManager = new UserManager('users.json');

// Add event listeners for user management
document.addEventListener('DOMContentLoaded', () => {
    const addUserForm = document.getElementById('addUserForm');
    const searchInput = document.getElementById('searchInput');
    const userList = document.getElementById('userList');
    
    if (addUserForm) {
        addUserForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(addUserForm);
            const user = new User(
                formData.get('name'),
                formData.get('email'),
                parseInt(formData.get('age')) || null,
                JSON.parse(formData.get('preferences') || '{}')
            );
            
            if (userManager.addUser(user)) {
                updateUserList();
                addUserForm.reset();
            }
        });
    }
    
    if (searchInput) {
        searchInput.addEventListener('input', (event) => {
            const query = event.target.value;
            const results = userManager.searchUsers(query);
            updateUserList(results);
        });
    }
});

// Update user list display
function updateUserList(users = null) {
    const userList = document.getElementById('userList');
    if (!userList) return;
    
    const displayUsers = users || userManager.listUsers();
    userList.innerHTML = displayUsers.map(user => `
        <div class="user-card">
            <h3>${user.name}</h3>
            <p>Email: ${user.email}</p>
            ${user.age ? `<p>Age: ${user.age}</p>` : ''}
            ${Object.keys(user.preferences).length > 0 ? 
                `<p>Preferences: ${JSON.stringify(user.preferences)}</p>` : ''}
            <button onclick="editUser('${user.email}')">Edit</button>
            <button onclick="deleteUser('${user.email}')">Delete</button>
        </div>
    `).join('');
}

// Export for use in other modules
export { User, UserManager }; 
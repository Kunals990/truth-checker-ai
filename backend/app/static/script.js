
class AuthApp {
    constructor() {
        this.token = this.getTokenFromURL() || localStorage.getItem('access_token');
        this.user = null;
        this.init();
    }

    init() {
        // Clean URL if token is present
        if (this.getTokenFromURL()) {
            localStorage.setItem('access_token', this.token);
            // Clean URL
            window.history.replaceState({}, document.title, '/');
        }

        this.bindEvents();
        this.checkAuthStatus();
    }

    getTokenFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('access_token');
    }

    bindEvents() {
        // Login button
        document.getElementById('loginBtn').addEventListener('click', () => {
            this.initiateLogin();
        });

        // Logout button
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });

        // Update profile button
        document.getElementById('updateProfileBtn').addEventListener('click', () => {
            this.showUpdateModal();
        });

        // View profile button
        document.getElementById('viewProfileBtn').addEventListener('click', () => {
            this.viewProfile();
        });

        // Update form
        document.getElementById('updateForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.updateProfile();
        });

        // Modal close
        document.querySelector('.close').addEventListener('click', () => {
            this.closeModal();
        });

        // Close modal on outside click
        window.addEventListener('click', (e) => {
            const modal = document.getElementById('updateModal');
            if (e.target === modal) {
                this.closeModal();
            }
        });
    }

    async checkAuthStatus() {
        if (this.token) {
            try {
                const response = await fetch('/auth/me', {
                    headers: {
                        'Authorization': `Bearer ${this.token}`
                    }
                });

                if (response.ok) {
                    this.user = await response.json();
                    this.showDashboard();
                } else {
                    this.clearAuth();
                    this.showLogin();
                }
            } catch (error) {
                console.error('Auth check failed:', error);
                this.clearAuth();
                this.showLogin();
            }
        } else {
            this.showLogin();
        }
    }

    async initiateLogin() {
        try {
            const response = await fetch('/auth/login');
            const data = await response.json();
            
            // Redirect to Google OAuth
            window.location.href = data.auth_url;
        } catch (error) {
            console.error('Login initiation failed:', error);
            alert('Login failed. Please try again.');
        }
    }

    async logout() {
        try {
            await fetch('/auth/logout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });
        } catch (error) {
            console.error('Logout request failed:', error);
        }

        this.clearAuth();
        this.showLogin();
    }

    clearAuth() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('access_token');
    }

    showLogin() {
        document.getElementById('loginSection').style.display = 'block';
        document.getElementById('dashboardSection').style.display = 'none';
    }

    showDashboard() {
        document.getElementById('loginSection').style.display = 'none';
        document.getElementById('dashboardSection').style.display = 'block';
        this.populateUserInfo();
    }

    populateUserInfo() {
        if (!this.user) return;

        document.getElementById('userName').textContent = this.user.name;
        document.getElementById('userEmail').textContent = this.user.email;
        
        // Handle user picture
        const userPicture = document.getElementById('userPicture');
        if (this.user.picture) {
            userPicture.src = this.user.picture;
            userPicture.style.display = 'block';
        } else {
            userPicture.style.display = 'none';
        }
        
        document.getElementById('profileStatus').textContent = this.user.is_active ? 'Active' : 'Inactive';
        
        // Format date
        const createdDate = new Date(this.user.created_at);
        document.getElementById('memberSince').textContent = createdDate.toLocaleDateString();
    }

    showUpdateModal() {
        if (!this.user) return;

        document.getElementById('updateName').value = this.user.name;
        document.getElementById('updatePicture').value = this.user.picture || '';
        document.getElementById('updateModal').style.display = 'block';
    }

    closeModal() {
        document.getElementById('updateModal').style.display = 'none';
    }

    async updateProfile() {
        const name = document.getElementById('updateName').value.trim();
        const picture = document.getElementById('updatePicture').value.trim();

        const updateData = {};
        if (name && name !== this.user.name) updateData.name = name;
        if (picture !== (this.user.picture || '')) updateData.picture = picture || null;

        if (Object.keys(updateData).length === 0) {
            alert('No changes to update');
            return;
        }

        try {
            const response = await fetch('/users/profile', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(updateData)
            });

            if (response.ok) {
                this.user = await response.json();
                this.populateUserInfo();
                this.closeModal();
                this.showNotification('Profile updated successfully!', 'success');
            } else {
                const error = await response.json();
                this.showNotification(`Update failed: ${error.detail}`, 'error');
            }
        } catch (error) {
            console.error('Update failed:', error);
            this.showNotification('Update failed. Please try again.', 'error');
        }
    }

    async viewProfile() {
        try {
            const response = await fetch('/users/profile', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                const profile = await response.json();
                const profileInfo = `
Name: ${profile.name}
Email: ${profile.email}
Status: ${profile.is_active ? 'Active' : 'Inactive'}
Member Since: ${new Date(profile.created_at).toLocaleDateString()}
                `.trim();
                alert(profileInfo);
            }
        } catch (error) {
            console.error('Failed to fetch profile:', error);
            this.showNotification('Failed to fetch profile', 'error');
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AuthApp();
});
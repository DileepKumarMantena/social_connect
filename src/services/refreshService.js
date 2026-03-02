/**
 * Auto-Refresh Service for Real-time Updates
 * Listens for backend refresh triggers
 */

class RefreshService {
    constructor() {
        this.listeners = new Map();
        this.setupRefreshListener();
    }

    setupRefreshListener() {
        // Listen for custom refresh events
        window.addEventListener('refresh', (event) => {
            console.log('Refresh event received:', event.detail);
            this.notifyListeners(event.detail.type, event.detail.data);
        });

        // Poll for refresh triggers (fallback method)
        this.startPolling();
    }

    startPolling() {
        // Poll backend every 5 seconds for refresh triggers
        setInterval(async () => {
            try {
                const response = await fetch(`${process.env.REACT_APP_API_LINKS}/api/v1/check-refresh`, {
                    method: 'GET',
                    credentials: 'include'
                });
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.type === 'refresh_needed') {
                        this.notifyListeners('auto_refresh', data.data);
                    }
                }
            } catch (error) {
                console.log('Refresh polling error:', error);
            }
        }, 5000); // 5 seconds
    }

    addListener(type, callback) {
        if (!this.listeners.has(type)) {
            this.listeners.set(type, []);
        }
        this.listeners.get(type).push(callback);
    }

    notifyListeners(type, data) {
        if (this.listeners.has(type)) {
            this.listeners.get(type).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('Error in refresh listener:', error);
                }
            });
        }
    }

    // Manual refresh trigger
    triggerRefresh(type = 'data_update', data = {}) {
        this.notifyListeners(type, data);
    }

    // User created event
    onUserCreated(callback) {
        this.addListener('user_created', callback);
    }

    // User updated event
    onUserUpdated(callback) {
        this.addListener('user_updated', callback);
    }

    // Auto refresh event
    onAutoRefresh(callback) {
        this.addListener('auto_refresh', callback);
    }
}

// Global refresh service instance
const refreshService = new RefreshService();

export default refreshService;

import axios from 'axios';

class ChatAPI {
    constructor() {
        this.baseURL = process.env.REACT_APP_API_LINKS || 'http://localhost:8000';
    }

    getAuthHeaders() {
        const token = localStorage.getItem('token');
        return {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }

    async fetchLeads() {
        try {
            const response = await axios.get(`${this.baseURL}/api/v1/leads`, {
                headers: this.getAuthHeaders(),
                withCredentials: true
            });
            return response.data.leads || [];
        } catch (error) {
            console.error('Error fetching leads:', error);
            if (error.response?.status === 403) {
                throw new Error('You don\'t have permission to access leads data');
            }
            return [];
        }
    }

    async fetchCampaigns() {
        try {
            const response = await axios.get(`${this.baseURL}/api/v1/campaigns`, {
                headers: this.getAuthHeaders(),
                withCredentials: true
            });
            return response.data.campaigns || [];
        } catch (error) {
            console.error('Error fetching campaigns:', error);
            if (error.response?.status === 403) {
                throw new Error('You don\'t have permission to access campaigns data');
            }
            return [];
        }
    }

    async fetchChannels() {
        try {
            const response = await axios.get(`${this.baseURL}/api/v1/channels`, {
                headers: this.getAuthHeaders(),
                withCredentials: true
            });
            return response.data.channels || [];
        } catch (error) {
            console.error('Error fetching channels:', error);
            if (error.response?.status === 403) {
                throw new Error('You don\'t have permission to access channels data');
            }
            return [];
        }
    }

    async fetchAnalytics() {
        try {
            const response = await axios.get(`${this.baseURL}/api/v1/analytics`, {
                headers: this.getAuthHeaders(),
                withCredentials: true
            });
            return response.data.analytics || [];
        } catch (error) {
            console.error('Error fetching analytics:', error);
            if (error.response?.status === 403) {
                throw new Error('You don\'t have permission to access analytics data');
            }
            return [];
        }
    }

    async fetchDashboardStats() {
        try {
            const response = await axios.get(`${this.baseURL}/api/v1/dashboard/stats`, {
                headers: this.getAuthHeaders(),
                withCredentials: true
            });
            return response.data.stats || {};
        } catch (error) {
            console.error('Error fetching dashboard stats:', error);
            return {};
        }
    }

    async createLead(leadData) {
        try {
            const response = await axios.post(`${this.baseURL}/api/v1/leads`, leadData, {
                headers: this.getAuthHeaders(),
                withCredentials: true
            });
            return response.data;
        } catch (error) {
            console.error('Error creating lead:', error);
            if (error.response?.status === 403) {
                throw new Error('You don\'t have permission to create leads');
            }
            throw error;
        }
    }

    async createCampaign(campaignData) {
        try {
            const response = await axios.post(`${this.baseURL}/api/v1/campaigns`, campaignData, {
                headers: this.getAuthHeaders(),
                withCredentials: true
            });
            return response.data;
        } catch (error) {
            console.error('Error creating campaign:', error);
            if (error.response?.status === 403) {
                throw new Error('You don\'t have permission to create campaigns');
            }
            throw error;
        }
    }

    async getUserPermissions() {
        try {
            const response = await axios.get(`${this.baseURL}/api/v1/verify-token`, {
                headers: this.getAuthHeaders(),
                withCredentials: true
            });
            return response.data.data?.permissions || {};
        } catch (error) {
            console.error('Error fetching user permissions:', error);
            return {};
        }
    }
}

export default new ChatAPI();

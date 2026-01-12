const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class API {
    constructor() {
        this.baseURL = API_BASE_URL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            if (response.status === 204) {
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }

    // Wall endpoints
    async getWalls() {
        return this.request('/walls/');
    }

    async getWall(wallId) {
        return this.request(`/walls/${wallId}`);
    }

    async createWall(wallData) {
        return this.request('/walls/', {
            method: 'POST',
            body: JSON.stringify(wallData)
        });
    }

    async updateWall(wallId, wallData) {
        return this.request(`/walls/${wallId}`, {
            method: 'PUT',
            body: JSON.stringify(wallData)
        });
    }

    async deleteWall(wallId) {
        return this.request(`/walls/${wallId}`, {
            method: 'DELETE'
        });
    }

    // Obstacle endpoints
    async getObstacles(wallId) {
        return this.request(`/walls/${wallId}/obstacles`);
    }

    async addObstacle(wallId, obstacleData) {
        return this.request(`/walls/${wallId}/obstacles`, {
            method: 'POST',
            body: JSON.stringify(obstacleData)
        });
    }

    async updateObstacle(obstacleId, obstacleData) {
        return this.request(`/obstacles/${obstacleId}`, {
            method: 'PUT',
            body: JSON.stringify(obstacleData)
        });
    }

    async deleteObstacle(obstacleId) {
        return this.request(`/obstacles/${obstacleId}`, {
            method: 'DELETE'
        });
    }

    // Path planning endpoints
    async planPath(wallId, algorithmType, parameters = {}) {
        return this.request('/paths/plan', {
            method: 'POST',
            body: JSON.stringify({
                wall_id: wallId,
                algorithm_type: algorithmType,
                parameters
            })
        });
    }

    async getTrajectories(wallId = null) {
        const query = wallId ? `?wall_id=${wallId}` : '';
        return this.request(`/paths/trajectories${query}`);
    }

    async getTrajectory(trajectoryId) {
        return this.request(`/paths/trajectories/${trajectoryId}`);
    }

    // Metrics endpoints
    async getSystemStats() {
        return this.request('/metrics/system');
    }

    async getWallMetrics(wallId) {
        return this.request(`/metrics/walls/${wallId}`);
    }
}

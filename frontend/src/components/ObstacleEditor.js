export class ObstacleEditor {
    constructor(api, app) {
        this.api = api;
        this.app = app;
        this.init();
    }

    init() {
        const form = document.getElementById('obstacleForm');
        form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    async handleSubmit(e) {
        e.preventDefault();

        const wallId = parseInt(document.getElementById('wallSelect').value);
        if (!wallId) {
            alert('Please select a wall first!');
            return;
        }

        const type = document.getElementById('obstacleType').value;
        const customName = document.getElementById('obstacleName').value.trim();

        const obstacleData = {
            obstacle_type: type,
            x: parseFloat(document.getElementById('obstacleX').value),
            y: parseFloat(document.getElementById('obstacleY').value),
            name: customName || `${type.charAt(0).toUpperCase() + type.slice(1)} Obstacle`
        };

        if (type === 'rectangle') {
            obstacleData.width = parseFloat(document.getElementById('obstacleWidth').value);
            obstacleData.height = parseFloat(document.getElementById('obstacleHeight').value);
        } else if (type === 'circle') {
            obstacleData.radius = parseFloat(document.getElementById('obstacleRadius').value);
        }

        try {
            const obstacle = await this.api.addObstacle(wallId, obstacleData);
            console.log('Obstacle added:', obstacle);

            // Show success message
            alert('Obstacle added successfully!');

            // Reset form
            e.target.reset();

            // Refresh wall view
            await this.app.selectWall(wallId);

        } catch (error) {
            console.error('Failed to add obstacle:', error);
            alert(`Failed to add obstacle: ${error.message}`);
        }
    }
}

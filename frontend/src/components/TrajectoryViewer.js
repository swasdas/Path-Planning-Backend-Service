export class Canvas {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.scale = 100; // pixels per meter
        this.offsetX = 80;  // Increased for axis labels
        this.offsetY = this.canvas.height - 80;  // Bottom-left origin
        this.currentWall = null;
        this.currentObstacles = [];
        this.currentTrajectory = null;
    }

    clear() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.currentObstacles = [];
        this.currentTrajectory = null;
        this.drawGrid();
        this.drawAxes();
    }

    drawGrid() {
        this.ctx.strokeStyle = '#f0f0f0';
        this.ctx.lineWidth = 1;

        // Vertical lines (every meter)
        for (let x = 0; x < this.canvas.width; x += this.scale) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }

        // Horizontal lines
        for (let y = 0; y < this.canvas.height; y += this.scale) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }

    drawAxes() {
        const originX = this.offsetX;
        const originY = this.offsetY;

        // Determine max ticks based on current wall dimensions, or default to 5
        const maxXTicks = this.currentWall ? Math.ceil(this.currentWall.width) : 5;
        const maxYTicks = this.currentWall ? Math.ceil(this.currentWall.height) : 5;

        // Draw X-axis (horizontal, pointing right)
        this.ctx.strokeStyle = '#FF5722';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(originX, originY);
        this.ctx.lineTo(originX + 150, originY);
        this.ctx.stroke();

        // X-axis arrow
        this.ctx.beginPath();
        this.ctx.moveTo(originX + 150, originY);
        this.ctx.lineTo(originX + 140, originY - 5);
        this.ctx.lineTo(originX + 140, originY + 5);
        this.ctx.closePath();
        this.ctx.fillStyle = '#FF5722';
        this.ctx.fill();

        // X-axis label (below the axis)
        this.ctx.fillStyle = '#FF5722';
        this.ctx.font = 'bold 16px Arial';
        this.ctx.fillText('X', originX + 160, originY + 20);

        // Draw Y-axis (vertical, pointing up - positive Y)
        this.ctx.strokeStyle = '#4CAF50';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(originX, originY);
        this.ctx.lineTo(originX, originY - 150);
        this.ctx.stroke();

        // Y-axis arrow (pointing up)
        this.ctx.beginPath();
        this.ctx.moveTo(originX, originY - 150);
        this.ctx.lineTo(originX - 5, originY - 140);
        this.ctx.lineTo(originX + 5, originY - 140);
        this.ctx.closePath();
        this.ctx.fillStyle = '#4CAF50';
        this.ctx.fill();

        // Y-axis label (to the left of the axis)
        this.ctx.fillStyle = '#4CAF50';
        this.ctx.font = 'bold 16px Arial';
        this.ctx.fillText('Y', originX - 25, originY - 155);

        // Draw origin marker
        this.ctx.fillStyle = '#000';
        this.ctx.beginPath();
        this.ctx.arc(originX, originY, 5, 0, 2 * Math.PI);
        this.ctx.fill();

        // Origin label (below and to the right)
        this.ctx.font = '12px Arial';
        this.ctx.fillText('(0,0)', originX + 10, originY + 15);

        // Draw tick marks on axes
        this.ctx.strokeStyle = '#666';
        this.ctx.lineWidth = 1;
        this.ctx.font = '10px Arial';
        this.ctx.fillStyle = '#666';

        // X-axis ticks (every meter up to wall width)
        for (let i = 1; i <= maxXTicks; i++) {
            const x = originX + i * this.scale;
            this.ctx.beginPath();
            this.ctx.moveTo(x, originY - 3);
            this.ctx.lineTo(x, originY + 3);
            this.ctx.stroke();
            this.ctx.fillText(`${i}m`, x - 8, originY + 15);
        }

        // Y-axis ticks (every meter up to wall height, positive going up)
        for (let i = 1; i <= maxYTicks; i++) {
            const y = originY - i * this.scale;
            this.ctx.beginPath();
            this.ctx.moveTo(originX - 3, y);
            this.ctx.lineTo(originX + 3, y);
            this.ctx.stroke();
            this.ctx.fillText(`${i}m`, originX - 25, y + 4);
        }
    }

    drawWall(wall, clearObstacles = true) {
        this.currentWall = wall;
        if (clearObstacles) {
            this.currentObstacles = [];
        }
        this.clear();

        const width = wall.width * this.scale;
        const height = wall.height * this.scale;

        // Draw wall boundary (Y inverted: going up from origin)
        this.ctx.strokeStyle = '#2196F3';
        this.ctx.lineWidth = 3;
        this.ctx.strokeRect(this.offsetX, this.offsetY - height, width, height);

        // Draw wall label at top center of canvas
        this.ctx.fillStyle = '#2196F3';
        this.ctx.font = 'bold 16px Arial';
        const labelText = `${wall.name} (${wall.width}m × ${wall.height}m)`;
        const textWidth = this.ctx.measureText(labelText).width;
        this.ctx.fillText(
            labelText,
            (this.canvas.width - textWidth) / 2,
            25
        );
    }

    drawObstacle(obstacle) {
        // Convert world coordinates (x, y are CENTER of obstacle)
        const centerX = this.offsetX + obstacle.x * this.scale;
        const centerY = this.offsetY - obstacle.y * this.scale;  // Y inverted: going up

        this.ctx.fillStyle = 'rgba(244, 67, 54, 0.3)';
        this.ctx.strokeStyle = '#F44336';
        this.ctx.lineWidth = 2;

        if (obstacle.obstacle_type === 'rectangle') {
            const width = obstacle.width * this.scale;
            const height = obstacle.height * this.scale;
            // Draw rectangle with CENTER at (centerX, centerY)
            const rectX = centerX - width / 2;
            const rectY = centerY - height / 2;
            this.ctx.fillRect(rectX, rectY, width, height);
            this.ctx.strokeRect(rectX, rectY, width, height);
        } else if (obstacle.obstacle_type === 'circle') {
            const radius = obstacle.radius * this.scale;
            // Draw circle with CENTER at (centerX, centerY)
            this.ctx.beginPath();
            this.ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
            this.ctx.fill();
            this.ctx.stroke();
        }

        // Draw label if it has a name
        if (obstacle.name) {
            this.ctx.fillStyle = '#000';
            this.ctx.font = '10px Arial';
            this.ctx.fillText(obstacle.name, centerX + 5, centerY - 5);
        }

        // Store obstacle for redrawing
        if (!this.currentObstacles.find(o => o.id === obstacle.id)) {
            this.currentObstacles.push(obstacle);
        }
    }

    drawTrajectory(trajectory) {
        this.currentTrajectory = trajectory;

        if (!trajectory.waypoints || trajectory.waypoints.length === 0) {
            return;
        }

        // Clear and redraw wall to remove previous trajectory
        if (this.currentWall) {
            const obstaclesBackup = [...this.currentObstacles];
            this.drawWall(this.currentWall, false);
            // Redraw all obstacles
            obstaclesBackup.forEach(obs => this.drawObstacle(obs));
        }

        // Draw path
        this.ctx.strokeStyle = '#4CAF50';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();

        const firstWp = trajectory.waypoints[0];
        const startX = this.offsetX + firstWp.x * this.scale;
        const startY = this.offsetY - firstWp.y * this.scale;  // Y inverted
        this.ctx.moveTo(startX, startY);

        for (let i = 1; i < trajectory.waypoints.length; i++) {
            const wp = trajectory.waypoints[i];
            const x = this.offsetX + wp.x * this.scale;
            const y = this.offsetY - wp.y * this.scale;  // Y inverted
            this.ctx.lineTo(x, y);
        }

        this.ctx.stroke();

        // Draw waypoints
        trajectory.waypoints.forEach((wp, index) => {
            const x = this.offsetX + wp.x * this.scale;
            const y = this.offsetY - wp.y * this.scale;  // Y inverted

            this.ctx.fillStyle = index === 0 ? '#4CAF50' :
                                index === trajectory.waypoints.length - 1 ? '#F44336' :
                                '#FFC107';
            this.ctx.beginPath();
            this.ctx.arc(x, y, 3, 0, 2 * Math.PI);
            this.ctx.fill();
        });

        // Draw start and end labels
        const start = trajectory.waypoints[0];
        const end = trajectory.waypoints[trajectory.waypoints.length - 1];

        this.ctx.fillStyle = '#000';
        this.ctx.font = '12px Arial';
        this.ctx.fillText('START',
            this.offsetX + start.x * this.scale + 8,
            this.offsetY - start.y * this.scale);
        this.ctx.fillText('END',
            this.offsetX + end.x * this.scale + 8,
            this.offsetY - end.y * this.scale);
    }

    zoom(factor) {
        this.scale *= factor;
        // Update offsetY to maintain bottom-left origin
        this.offsetY = this.canvas.height - 80;
        if (this.currentWall) {
            const obstaclesBackup = [...this.currentObstacles];
            this.drawWall(this.currentWall, false);
            obstaclesBackup.forEach(obs => this.drawObstacle(obs));
            if (this.currentTrajectory) {
                this.drawTrajectory(this.currentTrajectory);
            }
        }
    }
}

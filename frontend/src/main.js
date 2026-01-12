import { API } from './api.js';
import { Canvas } from './components/TrajectoryViewer.js';
import { WallConfigurator } from './components/WallConfigurator.js';
import { ObstacleEditor } from './components/ObstacleEditor.js';
import { ControlPanel } from './components/ControlPanel.js';

class App {
    constructor() {
        this.api = new API();
        this.canvas = new Canvas('canvas');
        this.wallConfigurator = new WallConfigurator(this.api, this);
        this.obstacleEditor = new ObstacleEditor(this.api, this);
        this.controlPanel = new ControlPanel(this.api, this);

        this.currentWall = null;
        this.currentTrajectory = null;

        this.init();
    }

    async init() {
        console.log('🚀 Initializing Wall Finishing Robot Control System...');

        // Load initial data
        await this.loadWalls();
        await this.loadSystemStats();

        // Set up event listeners
        this.setupEventListeners();

        console.log('✅ Application initialized');
    }

    setupEventListeners() {
        // Wall selection
        document.getElementById('wallSelect').addEventListener('change', (e) => {
            const wallId = parseInt(e.target.value);
            if (wallId) {
                this.selectWall(wallId);
            }
        });

        // Canvas controls
        document.getElementById('clearBtn').addEventListener('click', () => {
            this.canvas.clear();
        });

        document.getElementById('zoomInBtn').addEventListener('click', () => {
            this.canvas.zoom(1.2);
        });

        document.getElementById('zoomOutBtn').addEventListener('click', () => {
            this.canvas.zoom(0.8);
        });

        // Obstacle type change
        document.getElementById('obstacleType').addEventListener('change', (e) => {
            const rectDims = document.getElementById('rectDimensions');
            const circleDims = document.getElementById('circleDimensions');

            if (e.target.value === 'circle') {
                rectDims.style.display = 'none';
                circleDims.style.display = 'block';
            } else {
                rectDims.style.display = 'block';
                circleDims.style.display = 'none';
            }
        });
    }

    async loadWalls() {
        try {
            const walls = await this.api.getWalls();
            const select = document.getElementById('wallSelect');

            select.innerHTML = '<option value="">-- Select a Wall --</option>';
            walls.forEach(wall => {
                const option = document.createElement('option');
                option.value = wall.id;
                option.textContent = `${wall.name} (${wall.width}m × ${wall.height}m)`;
                select.appendChild(option);
            });
        } catch (error) {
            console.error('Failed to load walls:', error);
        }
    }

    async selectWall(wallId) {
        try {
            const wall = await this.api.getWall(wallId);
            const obstacles = await this.api.getObstacles(wallId);

            this.currentWall = { ...wall, obstacles };

            // Draw on canvas
            this.canvas.clear();
            this.canvas.drawWall(wall);
            obstacles.forEach(obs => this.canvas.drawObstacle(obs));

            // Update info
            document.getElementById('canvasInfo').innerHTML = `
                <p><strong>${wall.name}</strong></p>
                <p>Dimensions: ${wall.width}m × ${wall.height}m</p>
                <p>Obstacles: ${obstacles.length}</p>
            `;

            // Load metrics
            await this.loadWallMetrics(wallId);
        } catch (error) {
            console.error('Failed to select wall:', error);
        }
    }

    async loadWallMetrics(wallId) {
        try {
            const metrics = await this.api.getWallMetrics(wallId);
            const display = document.getElementById('metricsDisplay');

            display.innerHTML = `
                <div class="metric">
                    <label>Total Paths:</label>
                    <span>${metrics.total_paths}</span>
                </div>
                <div class="metric">
                    <label>Avg Distance:</label>
                    <span>${metrics.avg_distance.toFixed(2)} m</span>
                </div>
                <div class="metric">
                    <label>Avg Coverage:</label>
                    <span>${metrics.avg_coverage.toFixed(1)}%</span>
                </div>
                <div class="metric">
                    <label>Avg Planning Time:</label>
                    <span>${metrics.avg_planning_time.toFixed(3)} s</span>
                </div>
            `;
        } catch (error) {
            console.error('Failed to load metrics:', error);
        }
    }

    async loadSystemStats() {
        try {
            const stats = await this.api.getSystemStats();

            document.getElementById('totalWalls').textContent = stats.total_walls;
            document.getElementById('totalPaths').textContent = stats.total_trajectories;
            document.getElementById('avgCoverage').textContent = `${stats.avg_coverage.toFixed(1)}%`;
        } catch (error) {
            console.error('Failed to load system stats:', error);
        }
    }

    async refresh() {
        await this.loadWalls();
        await this.loadSystemStats();
        if (this.currentWall) {
            await this.selectWall(this.currentWall.id);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});

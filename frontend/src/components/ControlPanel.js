export class ControlPanel {
    constructor(api, app) {
        this.api = api;
        this.app = app;
        this.init();
    }

    init() {
        const form = document.getElementById('pathForm');
        form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    async handleSubmit(e) {
        e.preventDefault();

        const wallId = parseInt(document.getElementById('wallSelect').value);
        if (!wallId) {
            alert('Please select a wall first!');
            return;
        }

        const algorithmType = document.getElementById('algorithmType').value;

        try {
            // Show loading state
            const submitBtn = e.target.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Planning...';
            submitBtn.disabled = true;

            console.log(`Planning path for wall ${wallId} using ${algorithmType}...`);

            const trajectory = await this.api.planPath(wallId, algorithmType);
            console.log('Trajectory planned:', trajectory);

            // Draw trajectory on canvas
            this.app.canvas.drawTrajectory(trajectory);

            // Update canvas info
            document.getElementById('canvasInfo').innerHTML = `
                <p><strong>Path Planned Successfully!</strong></p>
                <p>Algorithm: ${trajectory.algorithm_type}</p>
                <p>Waypoints: ${trajectory.waypoints.length}</p>
                <p>Distance: ${trajectory.total_distance?.toFixed(2)} m</p>
                <p>Coverage: ${trajectory.coverage_percentage?.toFixed(1)}%</p>
                <p>Planning Time: ${trajectory.planning_time?.toFixed(3)} s</p>
            `;

            // Show success message
            alert('Path planned successfully!');

            // Reset button
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;

            // Refresh metrics
            await this.app.loadWallMetrics(wallId);
            await this.app.loadSystemStats();

        } catch (error) {
            console.error('Failed to plan path:', error);
            alert(`Failed to plan path: ${error.message}`);

            // Reset button
            const submitBtn = e.target.querySelector('button[type="submit"]');
            submitBtn.textContent = 'Plan Path';
            submitBtn.disabled = false;
        }
    }
}

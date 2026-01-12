export class WallConfigurator {
    constructor(api, app) {
        this.api = api;
        this.app = app;
        this.init();
    }

    init() {
        const form = document.getElementById('wallForm');
        form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    async handleSubmit(e) {
        e.preventDefault();

        const wallData = {
            name: document.getElementById('wallName').value,
            width: parseFloat(document.getElementById('wallWidth').value),
            height: parseFloat(document.getElementById('wallHeight').value),
            surface_type: 'standard'
        };

        try {
            const wall = await this.api.createWall(wallData);
            console.log('Wall created:', wall);

            // Reset form
            e.target.reset();

            // Refresh app to load new wall list and system stats
            await this.app.refresh();

            // Auto-select new wall
            const wallSelect = document.getElementById('wallSelect');
            console.log('Available wall options:', wallSelect.options.length);
            console.log('Setting wall select to:', wall.id);

            // Verify wall exists in dropdown
            const wallOption = Array.from(wallSelect.options).find(opt => opt.value == wall.id);
            if (!wallOption) {
                console.error('Wall not found in dropdown! Wall ID:', wall.id);
                this.showMessage('Wall created but not found in dropdown. Please refresh the page.', 'error');
                return;
            }

            wallSelect.value = wall.id;
            console.log('Wall select value set to:', wallSelect.value);

            // Trigger change event and select wall
            await this.app.selectWall(wall.id);

            // Show success message after everything is loaded
            this.showMessage('Wall created successfully!', 'success');

        } catch (error) {
            console.error('Failed to create wall:', error);
            this.showMessage(`Failed to create wall: ${error.message}`, 'error');
        }
    }

    showMessage(message, type) {
        // Simple alert for now - could be replaced with a toast notification
        alert(message);
    }
}

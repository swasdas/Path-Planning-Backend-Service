# 🤖 Path Planning Backend Service

A sophisticated autonomous robot path planning and control system for wall finishing tasks. This system uses advanced algorithms (Coverage Planning, A*, Genetic Algorithm) to generate optimal trajectories for robots to cover wall surfaces while avoiding obstacles.

## 🎥 Demo Video

[▶ Watch the walkthrough video](./swastik-demo-recording.mp4)


## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [API Documentation](#api-documentation)
- [Algorithm Overview](#algorithm-overview)
- [Usage Examples](#usage-examples)
- [Development](#development)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- **Multiple Path Planning Algorithms**
  - Boustrophedon Coverage (lawn-mower pattern)
  - A* Pathfinding (shortest path)
  - Genetic Algorithm (optimization)
  - Hybrid approach (combines all three)

- **Complex Obstacle Support**
  - Rectangles (windows, doors, panels)
  - Circles (outlets, pipes)
  - Polygons (custom shapes)

- **Real-time Visualization**
  - HTML5 Canvas-based 2D trajectory viewer
  - Interactive obstacle editor
  - Live path visualization

- **Performance Optimization**
  - Redis caching for path results
  - PostgreSQL for persistent storage

- **RESTful API**
  - Auto-generated Swagger documentation
  - WebSocket support for real-time updates
  - Comprehensive metrics and analytics

## 🛠 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI + Python 3.11 | High-performance async API |
| **Database** | PostgreSQL 15 | Relational data storage |
| **Cache** | Redis 7 | Path caching & pub/sub |
| **Frontend** | Vanilla JS + HTML5 Canvas | Interactive UI |
| **Algorithms** | NumPy + SciPy + Shapely | Path planning logic |
| **Deployment** | Docker + Docker Compose | Containerized services |

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                       │
│          (HTML5 Canvas + JavaScript)                    │
│              http://localhost:3000                      │
└─────────────────┬───────────────────────────────────────┘
                  │ HTTP/REST + WebSocket
                  ▼
┌─────────────────────────────────────────────────────────┐
│                  BACKEND API (FastAPI)                  │
│              http://localhost:8000/docs                 │
├─────────────────────────────────────────────────────────┤
│  API Endpoints: /walls, /obstacles, /paths, /metrics    │
│  Services: Wall, Path Planning, Metrics                 │
│  Algorithms: Coverage, A*, Genetic, Hybrid              │
└───┬─────────────────┬───────────────────────────────────┘
    │                 │
    ▼                 ▼
┌──────────┐    ┌──────────┐
│PostgreSQL│    │  Redis   │
│ Port:5432│    │ Port:6379│
└──────────┘    └──────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed
- At least 4GB RAM available
- Ports 3000, 5432, 6379, 8000 available

### 1. Clone & Start

```bash
# Clone the repository
cd wall-finishing-rcs

# Start all services
make up
```

### 2. Access the Application

- **Frontend UI**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

### 3. Seed Sample Data (Optional)

```bash
make seed
```

This creates:
- 2 sample walls
- 5 obstacles
- 1 sample trajectory

### 4. Start Using!

1. Open http://localhost:3000
2. Create a new wall or select an existing one
3. Add obstacles (windows, outlets, etc.)
4. Click "Plan Path" to generate trajectory
5. View the optimized path on the canvas

## 📖 Detailed Setup

### Build from Source

```bash
# Build all Docker images
make build

# Start services
make up

# View logs
make logs

# Stop services
make down

# Clean everything (including volumes)
make clean
```

### Manual Setup (Without Docker)

#### Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis locally (on default ports)

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

## 📚 API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

#### Walls

```bash
# Create wall
POST /walls/
{
  "name": "Living Room Wall",
  "width": 5.0,
  "height": 3.0,
  "surface_type": "drywall"
}

# Get all walls
GET /walls/

# Get specific wall
GET /walls/{wall_id}
```

#### Obstacles

```bash
# Add rectangle obstacle
POST /walls/{wall_id}/obstacles
{
  "obstacle_type": "rectangle",
  "x": 1.0,
  "y": 1.0,
  "width": 1.2,
  "height": 0.8,
  "name": "Window"
}

# Add circle obstacle
POST /walls/{wall_id}/obstacles
{
  "obstacle_type": "circle",
  "x": 4.0,
  "y": 1.5,
  "radius": 0.15,
  "name": "Outlet"
}
```

#### Path Planning

```bash
# Plan path
POST /paths/plan
{
  "wall_id": 1,
  "algorithm_type": "hybrid",
  "parameters": {
    "grid_resolution": 0.1,
    "population_size": 50,
    "generations": 30
  }
}

# Get trajectory
GET /paths/trajectories/{trajectory_id}
```

## 🧠 Algorithm Overview

### 1. Coverage Planning (Boustrophedon)

Simple lawn-mower pattern that guarantees full coverage.

**Pros**: Fast, predictable, guaranteed coverage
**Cons**: May not be the most efficient

### 2. A* Pathfinding

Finds shortest path between two points while avoiding obstacles.

**Pros**: Optimal shortest path, very fast
**Cons**: Doesn't ensure full coverage

### 3. Genetic Algorithm

Evolutionary optimization to find the best path order.

**Pros**: Can find very optimal solutions
**Cons**: Slower, results may vary

### 4. Hybrid (Recommended)

Combines all three:
1. Coverage planner generates full coverage
2. A* connects disconnected sections
3. Genetic algorithm optimizes the order

**Best for**: Most real-world scenarios

## 💡 Usage Examples

### Example 1: Simple Wall with Window

```python
import requests

API = "http://localhost:8000"

# Create wall
wall = requests.post(f"{API}/walls/", json={
    "name": "Bedroom Wall",
    "width": 4.0,
    "height": 2.8
}).json()

# Add window obstacle
obstacle = requests.post(f"{API}/walls/{wall['id']}/obstacles", json={
    "obstacle_type": "rectangle",
    "x": 1.5,
    "y": 1.0,
    "width": 1.2,
    "height": 1.0,
    "name": "Window"
}).json()

# Plan path
trajectory = requests.post(f"{API}/paths/plan", json={
    "wall_id": wall['id'],
    "algorithm_type": "hybrid"
}).json()

print(f"Path planned with {len(trajectory['waypoints'])} waypoints")
print(f"Total distance: {trajectory['total_distance']:.2f} meters")
print(f"Coverage: {trajectory['coverage_percentage']:.1f}%")
```

### Example 2: Complex Wall with Multiple Obstacles

See `scripts/seed_data.py` for a complete example.

## 🔧 Development

### Project Structure

```
wall-finishing-rcs/
├── backend/
│   ├── app/
│   │   ├── algorithms/     # Path planning algorithms
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── cache/          # Redis client
│   └── tests/              # Unit & integration tests
├── frontend/
│   └── src/
│       ├── components/     # UI components
│       └── styles/         # CSS styles
├── scripts/                # Utility scripts
└── docker-compose.yml      # Service orchestration
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
docker-compose exec backend pytest tests/test_algorithms.py -v

# Run with coverage
docker-compose exec backend pytest --cov=app --cov-report=html
```

### Adding a New Algorithm

1. Create `backend/app/algorithms/my_algorithm.py`
2. Implement the algorithm class
3. Register in `backend/app/algorithms/__init__.py`
4. Add to `AlgorithmType` enum in `models/trajectory.py`
5. Update `path_service.py` to handle the new type

## 🧪 Testing

### Test Wall Configuration

```bash
curl -X POST http://localhost:8000/walls/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Wall",
    "width": 5.0,
    "height": 3.0
  }'
```

### Test Path Planning

```bash
curl -X POST http://localhost:8000/paths/plan \
  -H "Content-Type: application/json" \
  -d '{
    "wall_id": 1,
    "algorithm_type": "hybrid"
  }'
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in docker-compose.yml
```

### Database Connection Error

```bash
# Restart PostgreSQL container
docker-compose restart postgres

# Check if database is ready
docker-compose exec postgres pg_isready -U robot
```

### Redis Connection Error

```bash
# Restart Redis container
docker-compose restart redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

### Frontend Not Loading

```bash
# Rebuild frontend
cd frontend
npm install
npm run dev
```

### Clear All Data

```bash
make clean
make build
make up
make seed
```

## 📊 Performance Tips

1. **Adjust Grid Resolution**: Lower resolution = faster planning but less precision
   ```json
   {
     "parameters": {
       "grid_resolution": 0.05  // 5cm (default: 0.1m)
     }
   }
   ```

2. **Tune Genetic Algorithm**: Reduce population/generations for faster results
   ```json
   {
     "parameters": {
       "population_size": 30,  // default: 50
       "generations": 20       // default: 30
     }
   }
   ```

3. **Use Coverage for Simple Walls**: Fastest algorithm for walls without obstacles
   ```json
   {
     "algorithm_type": "coverage"
   }
   ```


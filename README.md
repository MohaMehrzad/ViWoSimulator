# ViWO Token Economy Simulator

A full-featured token economy simulator for the ViWO Protocol with Next.js frontend and Python FastAPI backend, supporting deterministic calculations, Monte Carlo simulations, and Agent-Based modeling with WebSocket streaming for real-time results.

## Features

### Simulation Types
- **Deterministic**: Real-time calculations with same inputs producing same outputs
- **Monte Carlo**: Run 1,000-10,000 simulations with randomized parameters to understand probability distributions
- **Agent-Based**: Simulate individual user behaviors (creators, consumers, whales, bots) with market dynamics

### Revenue Modules
- **Identity**: User tiers, verification, profile transfers, marketplace sales
- **Content**: Post fees, NFT minting, premium content, content sales
- **Community**: Community subscriptions, events, verification, analytics
- **Advertising**: Banner/video ads, promoted posts, campaigns, analytics
- **Messaging**: Encrypted DMs, group chats, file transfers, voice/video calls

### Token Economics
- Token burn mechanics
- Buyback programs
- Staking incentives
- Treasury accumulation
- Reward recapture tracking

## Tech Stack

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Recharts for visualizations
- WebSocket for real-time updates

### Backend
- Python 3.11
- FastAPI
- NumPy/SciPy for simulations
- WebSocket support
- Pydantic for validation

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- npm or yarn

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`

### Docker Setup (Alternative)

```bash
docker-compose up
```

## API Endpoints

### REST Endpoints
- `GET /api/health` - Health check
- `POST /api/simulate/deterministic` - Run deterministic simulation
- `POST /api/simulate/monte-carlo` - Run Monte Carlo simulation
- `POST /api/simulate/agent-based` - Run agent-based simulation
- `GET /api/presets` - Get preset configurations
- `POST /api/export` - Export results (JSON/CSV)

### WebSocket
- `WS /ws/simulation/{job_id}` - Stream simulation progress

## Usage

1. **Adjust Parameters**: Use the interactive controls to set token price, marketing budget, fees, and other parameters.

2. **Select Simulation Type**:
   - Deterministic for quick calculations
   - Monte Carlo for risk analysis
   - Agent-Based for behavior simulation

3. **View Results**: 
   - Module-by-module revenue breakdown
   - Recapture flow visualization
   - Token velocity metrics
   - Distribution charts (Monte Carlo)
   - Agent behavior analysis

4. **Export**: Save parameters and results as JSON or CSV

## Preset Configurations

- **Lean Bootstrap ($50K/yr)**: Conservative growth with minimal marketing
- **Base Case ($150K/yr)**: Balanced growth strategy
- **Growth Phase ($250K/yr)**: Aggressive user acquisition
- **Year 2+ Scale ($400K/yr)**: Established brand with strong growth

## Project Structure

```
Simulator/
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js pages
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   ├── lib/           # Utilities
│   │   └── types/         # TypeScript types
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── core/          # Simulation engines
│   │   ├── models/        # Pydantic models
│   │   ├── routers/       # API endpoints
│   │   └── services/      # Background services
│   └── requirements.txt
│
└── docker-compose.yml
```

## License

MIT License


















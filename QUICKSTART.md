# Quick Start Guide

Get the SRE Tier-0 Monitoring Dashboard running in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- Terminal/Command Prompt access

## Option 1: Using Run Scripts (Easiest)

### Linux/Mac:
```bash
./run.sh
```

### Windows:
```bash
run.bat
```

The script will automatically:
- Create virtual environment
- Install dependencies
- Create .env file
- Start the server

## Option 2: Manual Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env if needed (optional)
```

### 5. Run Application
```bash
python backend/main.py
```

## Access the Dashboard

1. Open browser: http://localhost:8000
2. Login with:
   - **Username**: `admin`
   - **Password**: `secret`

## What You'll See

### Dashboard Overview
- 100,000 simulated IoT devices
- 10 sites across 2 regions
- Real-time metrics and health status

### Key Features to Try

#### 1. View System Metrics
- Total devices, online/offline counts
- Health percentage
- Device type distribution

#### 2. Monitor Sites
- Scroll to "Sites Overview" table
- See per-site device counts
- Check average temperature and efficiency

#### 3. Simulate Failover
- Click "Simulate Failover" button
- Watch region status change from Region 1 to Region 2
- Observe latency changes

#### 4. Analyze Logs
- Click "Generate Sample Logs" (first time only)
- Click "Analyze Logs"
- View top error IPs in the table

#### 5. Use AI Assistant
- Type a question like: "What is the system health?"
- Click "Ask AI"
- See AI-generated response

## API Documentation

Interactive API docs: http://localhost:8000/api/docs

## Troubleshooting

### Port 8000 Already in Use
Edit `.env` and change:
```
PORT=8080
```

### Import Errors
Make sure to run from project root:
```bash
# Correct:
python backend/main.py

# Wrong:
cd backend && python main.py
```

### Redis Not Available
Set in `.env`:
```
USE_REDIS=false
```

### Cohere API Not Working
- System works without Cohere API key
- AI features use mock responses
- Add `COHERE_API_KEY` in `.env` for real AI

## Testing the System

### 1. Authentication
- Login/logout works
- JWT tokens are generated
- Session management active

### 2. Device Monitoring
- Dashboard shows 100,000 devices
- Metrics update every 10 seconds
- Sites table populated

### 3. Failover
- Region switching works
- Status indicators update
- Latency values change

### 4. Log Analysis
- Sample logs can be generated
- Top error IPs are identified
- Error rates calculated

### 5. AI Features
- Natural language queries work
- Mock responses provided
- Ready for Cohere integration

## Architecture Highlights

### Backend (FastAPI)
- REST API with JWT authentication
- MQTT device simulation
- Redis caching (optional)
- Cohere AI integration
- Log analysis engine

### Frontend (Vanilla JS)
- No frameworks, pure JavaScript
- Responsive design
- Real-time updates
- Clean, professional UI

### Scale
- **100,000** simulated devices
- **10** sites
- **2** regions with failover
- **4** device types

## Demo Flow (For Presentation)

1. **Start** → Open dashboard, show login
2. **Overview** → Highlight 100K devices, health metrics
3. **Sites** → Scroll through site table
4. **Failover** → Click button, show region switch
5. **Logs** → Generate logs, analyze, show top IPs
6. **AI** → Ask "What's the system status?"
7. **API** → Show Swagger docs at /api/docs

## Next Steps

- Add your Cohere API key to `.env`
- Place device images in `images/` folder
- Add your actual log file as `sample_log.txt`
- Customize device schemas in `templates/`

## Support

For issues:
- Check README.md for detailed docs
- Review API docs at /api/docs
- Check browser console for errors
- Verify Python version is 3.8+

---

**Happy Hacking! 🚀**

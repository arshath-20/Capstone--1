# ⚡ Quick Start Guide

Get your Cyber Intrusion Detection System up and running in minutes!

## 📋 Prerequisites

- Python 3.9+
- pip (Python package manager)
- 4GB+ RAM
- 2GB disk space

## 🚀 Installation & Setup (5 minutes)

### Option 1: Using Quick Start Script (Linux/macOS)

```bash
# Navigate to project directory
cd /workspaces/Capstone--1

# Make script executable
chmod +x start.sh

# Run startup script (trains models + starts both servers)
./start.sh
```

### Option 2: Manual Setup (Windows/Linux/macOS)

#### Step 1: Create Virtual Environment
```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Train Models
```bash
cd backend/model
python train.py
# Wait for training to complete (~2-5 minutes)
cd ../..
```

#### Step 4: Start Backend
```bash
# Terminal 1
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 5: Start Frontend
```bash
# Terminal 2 (make sure venv is activated)
cd frontend
streamlit run app.py --server.port 8501
```

## 🌐 Access the Application

| Component | URL | Purpose |
|-----------|-----|---------|
| **Streamlit App** | http://localhost:8501 | Main UI Dashboard |
| **API Docs (Swagger)** | http://localhost:8000/docs | API Documentation |
| **API Docs (ReDoc)** | http://localhost:8000/redoc | Alternative API Docs |
| **API Health Check** | http://localhost:8000/api/health | Backend Status |

## 📊 Using the Application

### 1. Dashboard
- View KPIs (total analyzed, attacks detected, accuracy)
- See feature importance charts
- Check recent predictions

### 2. Live Prediction
- Enter 82 network features
- Click "Predict" to get instant classification
- View confidence score and probabilities

### 3. Batch Analysis
- Upload CSV file with network flows
- System processes all samples
- Download results as CSV

### 4. Reports
- View model performance metrics
- See confusion matrix
- Compare all trained models
- Get production recommendations

### 5. About
- Learn about the project
- Understand the dataset (CICIDS2017)
- See technology stack

## 🧪 Quick Test

### Test Live Prediction
```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [3306, 15050.6, 47, 10, 4272, 3492, 1102, 92, 714, 187, 1172, 33, 530, 199, 658, 36.3, 4698, 10.7, 9929, 62.1, 30971, 134.6, 32.8, 5722, 40.5, 1876, 4871, 240.4, 1815, 62.2, 1, 0, 0, 0, 22, 56, 6.1, 1.7, 48, 1273, 887, 188, 44323, 1, 0, 0, 1, 4, 0, 0, 0, 0.95, 552, 885, 739, 47, 4457, 6.9, 5002, 220, 18.2, 1330, 8, 3173, 6, 2663, 29801, 57141, 4, 37, 3898, 940, 9053, 60.1, 9226, 186, 10603, 5.4]
  }'
```

### Test Health Check
```bash
curl -X GET "http://localhost:8000/api/health"
```

## ⚙️ Configuration

### Environment Variables (.env)
```
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DATABASE_URL=sqlite:///./intrusion_detection.db
LOG_LEVEL=INFO
CONFIDENCE_THRESHOLD=0.75
```

## 🐛 Troubleshooting

### Issue: "Model not found"
```bash
# Solution: Train models first
cd backend/model
python train.py
cd ../..
```

### Issue: "Address already in use"
```bash
# Kill process using port 8000 (Linux/macOS)
lsof -ti:8000 | xargs kill -9

# Kill process using port 8501 (Linux/macOS)
lsof -ti:8501 | xargs kill -9
```

### Issue: "Cannot connect to backend"
```bash
# Check if backend is running
curl http://localhost:8000/api/health

# Or check backend terminal for errors
```

## 📚 Documentation

- **README.md**: Complete documentation
- **config.py**: Configuration options
- **API Routes**: backend/api/routes.py
- **Frontend Pages**: frontend/pages/*.py
- **Models**: backend/model/train.py

## 🚀 Next Steps

1. ✅ Explore dashboard with real predictions
2. ✅ Try batch analysis with CSV files
3. ✅ Check reports and analytics
4. ✅ Review model performance metrics
5. ✅ Deploy to production (see README.md)

## 💡 Tips

- **First Time Setup**: Training models takes 2-5 minutes, but only once
- **Performance**: Models are cached after first load, predictions are < 100ms
- **Batch Processing**: Can handle 1000s of samples efficiently
- **API Documentation**: Visit http://localhost:8000/docs for interactive API testing

## 📱 Sample CSV Format

For batch analysis, prepare CSV with these columns (no label needed):
```
Destination Port,Flow Duration,Total Fwd Packets,...[82 features total]
3306,15050.607,47,10,4272,...
5432,2460.651,22,26,4493,...
```

## 🎓 Learn More

- **CICIDS2017 Dataset**: Canadian Institute for Cybersecurity network intrusion dataset
- **Random Forest**: Ensemble of decision trees
- **FastAPI**: Modern Python web framework
- **Streamlit**: Rapid interactive app development

## 🤝 Support

Need help?
- Check README.md for detailed documentation
- Review code comments for implementation details
- Check API documentation at http://localhost:8000/docs
- Review example notebooks in `/notebooks`

---

**Happy Intrusion Detection! 🛡️**

# AI Resume Parser Setup Guide (Hugging Face Tranformer)

## ✅ Changes Made

1. **Replaced OpenAI with Hugging Face Transformers**
   - No API key or credits required
   - Runs locally on your machine
   - Default model: Mistralai Mistral-7B-Instruct

2. **Updated Files**
   - `requirements.txt` - Added transformers, torch, accelerate
   - `.env` - Replaced OpenAI config with Hugging Face config
   - `src/config.py` - Updated settings for HF models
   - `src/services/ai_service.py` - Complete rewrite using Transformers

3. **Fallback Parser**
   - If AI model fails, regex-based parser extracts basic info
   - Ensures system always returns results

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# For GPU support (optional but recommended)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install Tesseract for OCR (optional)
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# macOS:
brew install tesseract

# Windows:
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### Step 2: Start PostgreSQL Database

```bash
# Start database using Docker Compose
docker-compose up -d

# Verify database is running
docker ps
```

### Step 3: Configure Environment

```bash
# Copy .env file
cp .env.example .env

# Edit .env and set:
# - HF_DEVICE=cuda (if you have GPU) or cpu
# - HF_MODEL_NAME (use smaller model if low on RAM)
```

### Step 4: Run the Application

```bash
# Start the API server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or use the direct Python command
python src/main.py
```

### Step 5: Test the API

```bash
# Open your browser
http://localhost:8000/docs

# Or test with curl
curl -X POST "http://localhost:8000/api/v1/resumes/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_resume.pdf"
```

## 🎯 Model Options

### For CPU Users (Limited RAM < 8GB)
```bash
# In .env, set:
HF_MODEL_NAME=google/flan-t5-large
HF_DEVICE=cpu
```

### For CPU Users (Good RAM 16GB+)
```bash
HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
HF_DEVICE=cpu
```

### For GPU Users (NVIDIA)
```bash
HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
HF_DEVICE=cuda
```

### For Mac M1/M2/M3 Users
```bash
HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
HF_DEVICE=mps
```

## 📊 Expected Performance

| Model | RAM Required | Speed (CPU) | Accuracy |
|-------|-------------|-------------|----------|
| flan-t5-large | 4GB | Fast (5-10s) | Good |
| Mistral-7B | 16GB | Moderate (15-30s) | Excellent |
| Llama-2-7B | 16GB | Moderate (15-30s) | Excellent |

## 🔧 Troubleshooting

### Issue: Model download takes too long
```bash
# Download model manually first
python -c "from transformers import AutoModelForCausalLM, AutoTokenizer; \
           AutoTokenizer.from_pretrained('google/flan-t5-large'); \
           AutoModelForCausalLM.from_pretrained('google/flan-t5-large')"
```

### Issue: Out of memory error
```bash
# Use smaller model
HF_MODEL_NAME=google/flan-t5-base

# Or reduce max length
HF_MAX_LENGTH=1024
```

### Issue: CUDA not available
```bash
# Install CUDA-enabled PyTorch
pip uninstall torch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Issue: Slow inference on CPU
```bash
# The fallback parser will activate if AI takes too long
# Or use quantized models for faster inference
```

## 🎉 Features That Still Work

✅ Multi-format support (PDF, DOCX, TXT, Images)  
✅ OCR for scanned documents  
✅ Structured data extraction  
✅ Job matching with scoring  
✅ AI enhancements and insights  
✅ Fallback parser for reliability  
✅ All API endpoints functional  

## 📝 API Endpoints

- `POST /api/v1/resumes/upload` - Upload and parse resume
- `GET /api/v1/resumes/{id}` - Get parsed resume
- `PUT /api/v1/resumes/{id}` - Update resume
- `DELETE /api/v1/resumes/{id}` - Delete resume
- `GET /api/v1/resumes/{id}/status` - Get processing status
- `POST /api/v1/match` - Match resume with job
- `GET /api/v1/health` - Health check

## 🆘 Need Help?

1. Check logs in `logs/api_*.log`
2. Verify database connection: `docker logs resume_postgres`
3. Test model loading separately
4. Use fallback model if primary fails

## 🔐 No API Keys Required!

Unlike OpenAI, Hugging Face models run locally:
- ✅ No API costs
- ✅ No rate limits
- ✅ Complete privacy
- ✅ Works offline (after initial download)

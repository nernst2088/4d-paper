\# 4D-Paper: Dynamic Academic Paper System

## Project Origin

This project idea was first mentioned during a post-lunch walk and chat with my daughter in the spring of 2023. She thought it was somewhat interesting but not necessarily essential. Today, seeing the rapid development of Agents, I decide to share it anyway. I hope the tech or publishing industry might give it a try, and also hope we can abandon some of the current evaluation practices—some things are somewhat unnecessary.

This public project is just an idea, a demo. It doesn't matter too much whether anyone likes it or not.

## About the System

A full-stack system for managing **dynamic, versioned, 4D academic papers** (3D data + time dimension).

## Features

- 4D data ingestion & encryption (AES-256)
- Automatic paper version control
- Spatial-temporal data tracking (10k+ years support)
- Reader-author discussion forum
- View/download statistics with author permission control
- PDF/Markdown export
- RESTful API with FastAPI

## Quick Start

### 1. Local Run

```bash
# Create virtual environment
python -m venv venv

source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run API server
uvicorn src.api.main:app --reload
```

### 2. Docker Run

```bash
docker-compose up -d
```

### 3. Access API

Interactive docs: http://localhost:8000/docs
API root: http://localhost:8000

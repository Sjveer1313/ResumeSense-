# ResumeSense - AI-Powered Resume Feedback Engine

ResumeSense is a comprehensive web application that analyzes resumes using AI and machine learning to provide actionable feedback. It helps job seekers optimize their resumes for ATS (Applicant Tracking Systems) and improve their chances of landing interviews.

## 🚀 Features

- **PDF Resume Parsing**: Extract and parse text from PDF resumes using PyMuPDF
- **JD-Resume Matching**: Compute match scores between resumes and job descriptions
- **ATS Compliance Checking**: Identify ATS issues and provide recommendations
- **Power Verb Suggestions**: Find weak verbs and suggest stronger alternatives
- **ML Quality Scoring**: Machine learning-based resume quality scoring (0-100)
- **Analysis History**: Store and view past resume analyses
- **Modern Web UI**: Clean, responsive interface built with vanilla HTML/CSS/JS

## 📁 Project Structure

```
resumesense/
├── backend/
│   ├── api/                 # Flask API endpoints
│   │   ├── __init__.py
│   │   └── routes.py        # API route handlers
│   ├── ml/                  # ML model scripts
│   │   ├── __init__.py
│   │   ├── feature_extractor.py  # Feature extraction for ML
│   │   ├── resume_scorer.py      # Resume quality scorer
│   │   └── train_model.py        # Model training script
│   ├── nlp/                 # NLP processing modules
│   │   ├── __init__.py
│   │   ├── pdf_parser.py         # PDF text extraction
│   │   ├── jd_matcher.py         # JD-Resume matching
│   │   ├── ats_checker.py        # ATS compliance checker
│   │   └── power_verbs.py        # Power verb suggestions
│   ├── db/                  # Database models and connection
│   │   ├── __init__.py
│   │   └── database.py           # MySQL database operations
│   ├── tests/               # Unit tests
│   │   ├── __init__.py
│   │   ├── test_pdf_parser.py
│   │   ├── test_jd_matcher.py
│   │   ├── test_ats_checker.py
│   │   └── test_power_verbs.py
│   ├── __init__.py
│   └── config.py            # Configuration settings
├── frontend/
│   ├── static/              # Static assets
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       ├── main.js
│   │       └── history.js
│   └── templates/           # HTML templates
│       ├── index.html
│       └── history.html
├── data/
│   ├── resumes/             # Sample resumes
│   └── jds/                 # Sample job descriptions
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher (or MariaDB)
- pip (Python package manager)

### Step 1: Clone and Navigate

```bash
cd ResumeSense
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up MySQL Database

1. Start MySQL server:
```bash
# On macOS with Homebrew
brew services start mysql

# On Linux
sudo systemctl start mysql

# On Windows, start MySQL service from Services
```

2. Create database (optional - will be created automatically if user has permissions):
```sql
CREATE DATABASE resumesense;
```

### Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production

# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_DATABASE=resumesense

# File Upload Configuration
UPLOAD_FOLDER=data/resumes

# ML Model Configuration
ML_MODEL_PATH=backend/ml/resume_quality_model.pkl
```

### Step 6: Train ML Model (Optional)

The application will use a rule-based scorer if the model doesn't exist. To train the model:

```bash
python backend/ml/train_model.py
```

This will create `backend/ml/resume_quality_model.pkl`.

### Step 7: Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## 📖 API Documentation

### POST /api/analyze

Analyze a resume against a job description.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Parameters:
  - `resume_file` (file, optional): PDF file of resume
  - `resume_text` (text, optional): Plain text resume (if no file uploaded)
  - `job_description` (text, optional): Job description text

**Response:**
```json
{
  "match_score": 85.5,
  "ats_score": 92.3,
  "quality_score": 88.7,
  "match_details": {
    "common_keywords": ["Python", "JavaScript", "Flask"],
    "missing_keywords": ["Docker", "Kubernetes"],
    "important_keywords_matched": 8,
    "important_keywords_total": 10
  },
  "ats_report": {
    "issues": [],
    "recommendations": ["Use bullet points", "Include phone number"],
    "section_checks": {
      "education": true,
      "experience": true,
      "skills": true
    }
  },
  "power_verbs": {
    "findings": [
      {
        "weak_verb": "did",
        "suggestions": ["executed", "implemented", "accomplished"],
        "context": "..."
      }
    ],
    "stats": {
      "weak_verb_count": 3,
      "strong_verb_count": 15,
      "power_verb_score": 83.3
    }
  },
  "analysis_id": 1,
  "resume_id": 1,
  "job_id": 1
}
```

### GET /api/history

Get analysis history.

**Query Parameters:**
- `limit` (int, optional): Maximum number of results (default: 20)

**Response:**
```json
[
  {
    "id": 1,
    "resume_id": 1,
    "job_id": 1,
    "match_score": 85.5,
    "ats_score": 92.3,
    "quality_score": 88.7,
    "created_at": "2024-01-15T10:30:00",
    "resume_preview": "...",
    "jd_preview": "..."
  }
]
```

### GET /api/resume/<id>

Get resume by ID.

**Response:**
```json
{
  "id": 1,
  "resume_text": "...",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### GET /api/analysis/<id>

Get analysis result by ID.

**Response:**
```json
{
  "id": 1,
  "resume_id": 1,
  "job_id": 1,
  "match_score": 85.5,
  "ats_score": 92.3,
  "quality_score": 88.7,
  "ats_flags": {...},
  "power_verb_suggestions": {...},
  "match_details": {...},
  "created_at": "2024-01-15T10:30:00",
  "resume_text": "...",
  "job_description": "..."
}
```

## 🧪 Testing

Run unit tests:

```bash
python -m pytest backend/tests/
```

Or run specific test file:

```bash
python -m pytest backend/tests/test_pdf_parser.py
```

## 🔧 Development

### Git Workflow (2-Member Team)

1. **Main Branch**: Production-ready code
2. **Dev Branch**: Development integration
3. **Feature Branches**: Individual features

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Description of changes"

# Push to remote
git push origin feature/your-feature-name

# Create pull request to dev branch
# After review, merge to dev, then to main
```

### Code Structure Guidelines

- **Backend**: Follow PEP 8 style guide
- **Frontend**: Use semantic HTML, modern CSS, vanilla JavaScript
- **Database**: Use ORM methods in `backend/db/database.py`
- **Tests**: Write tests for all new features

## 🚀 Deployment

### Local Deployment

Follow setup instructions above.

### Cloud Deployment (Example: Heroku)

1. Install Heroku CLI
2. Create `Procfile`:
```
web: gunicorn run:app
```
3. Set environment variables in Heroku dashboard
4. Deploy:
```bash
git push heroku main
```

### Environment Variables for Production

- Set `SECRET_KEY` to a strong random value
- Configure production MySQL database
- Set `FLASK_ENV=production`
- Use production WSGI server (gunicorn, uWSGI)

## 📝 Features Explained

### 1. PDF Parsing
- Uses PyMuPDF (fitz) to extract text from PDF files
- Cleans and normalizes extracted text
- Handles multi-page resumes

### 2. JD Matching
- Tokenizes and extracts keywords from both texts
- Computes keyword overlap score
- Identifies important keywords from JD
- Provides missing keywords list

### 3. ATS Compliance
- Checks for required sections (Education, Experience, Skills)
- Validates contact information (email, phone)
- Flags problematic formatting (tables, excessive special chars)
- Provides actionable recommendations

### 4. Power Verb Suggestions
- Maintains dictionary of weak → strong verb mappings
- Finds weak verbs in resume text
- Provides context-aware suggestions
- Calculates power verb score

### 5. ML Quality Scoring
- Extracts 22 features from resume
- Uses Random Forest Regressor (or rule-based fallback)
- Scores resume quality (0-100)
- Considers ATS compliance, keywords, metrics, etc.


## 🐛 Troubleshooting

### Database Connection Issues
- Verify MySQL is running: `mysql -u root -p`
- Check `.env` file has correct credentials
- Ensure database exists or user has CREATE DATABASE permission

### PDF Parsing Errors
- Ensure PDF contains readable text (not just images)
- Check file size is within limits
- Verify PyMuPDF is installed correctly

### Model Not Found
- Application will use rule-based scoring as fallback
- Train model: `python backend/ml/train_model.py`
- Check `ML_MODEL_PATH` in `.env`

### Import Errors
- Ensure virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python path includes project root

## 📞 Support

For issues or questions, please check:
1. This README
2. Code comments in source files
3. Test files for usage examples

## 🎯 Future Enhancements

- [ ] Support for DOCX resume files
- [ ] Advanced ML models (neural networks)
- [ ] Resume templates and builder
- [ ] Export analysis as PDF report
- [ ] Multi-language support
- [ ] Real-time collaboration features
- [ ] Integration with job boards

---

**Built with ❤️ for job seekers everywhere**



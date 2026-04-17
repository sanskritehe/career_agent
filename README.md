# Career AI Assistant

Career AI Assistant is a comprehensive Streamlit-based web application designed to help users navigate their career paths using advanced Artificial Intelligence. Built with Groq's high-speed LLM APIs, Vector Databases (ChromaDB), and a robust MySQL backend, this platform provides personalized career guidance, technical preparation, and resume analysis.

## Features

- **Resume & Job Matching:** Upload your PDF resume, specify a target role, and let the AI analyze your profile. Under the hood, a Retrieval-Augmented Generation (RAG) pipeline grounds the analysis against real job descriptions to provide you with actionable skills gap analysis and a readiness score.
- **DSA Tutor:** A dedicated tutor for Data Structures and Algorithms that tracks your progress and gives personalized learning paths and practice problems.
- **Interview Prep:** Dynamic mock interviews customizable by role, interview type (e.g., technical or behavioral), and difficulty level. Get real-time AI feedback on your answers.
- **Readiness Report (Coordinator Agent):** Synthesizes your resume analysis, DSA progress, and interview performance to give a unified readiness verdict to conquer the job market.
- **AI Tools Suite:**
  - *Resume Builder:* Automatically rewrites your resume incorporating necessary ATS keywords.
  - *Learning Roadmap:* Maps your identified skill gaps to an actionable learning roadmap with estimated timelines.
  - *Answer Coach:* Rewrites your interview answers using proven frameworks like STAR.
- **My Profile:** A user dashboard that saves your history, tracks your resume analyses over time, and manages your interview session scores.

## Architecture & Tech Stack

- **Frontend:** Streamlit (Python UI framework)
- **AI / LLM:** Groq API (High inference speed AI models)
- **RAG & Vector Search:** ChromaDB, `sentence-transformers`
- **Text Processing & Extraction:** `pdfplumber`, `pypdf`
- **Database Backend:** MySQL (User details, interview history, metadata)
- **Data Analysis / Visualization:** Pandas, Plotly

## Prerequisitess

Make sure you have the following installed:
- Python 3.8+
- MySQL Server

## Setup & Installation

**1. Clone the repository and navigate to the project directory**
```bash
git clone <repository_url>
cd career_agent
```

**2. Create a virtual environment and activate it**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

**3. Install the dependencies**
```bash
pip install -r requirements.txt
```

**4. Environment Variables**
Create a `.env` file in the root directory (`career_agent/.env`) and add the necessary environment variables:
```env
GROQ_API_KEY=your_groq_api_key

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=career_ai
```

**5. Database Initialization**
The application is set up to automatically create the required database tables (`users`, `interview_sessions`, `resume_history`) upon start-up, provided your MySQL instance is running and the credentials are correct.
*Note: Make sure to create the `career_ai` database manually in your MySQL shell if it doesn't auto-create the database itself: `CREATE DATABASE career_ai;`*

**6. Run the Application**
```bash
streamlit run app.py
```

## Usage Notes

1. **Authentication:** You will be prompted to create an account or sign in. This ensures your interview history and resume analysis are saved to your profile.
2. **Knowledge Base:** Upon logging in, go to the **Resume & Job Match** page to build the RAG Index. This will index job descriptions into the Vector DB to empower the AI's analysis.
3. **Tracking Progress:** Interview metrics and resume reviews are continually tracked and visible within the **My Profile** tab.

## Structure Overview

- `app.py` - Main Streamlit application and entry point.
- `agents/` - Logical boundaries for LLM behaviors (co-ordinator, job matching, resume builder, etc.).
- `auth/` - Authentication logic, Session state management, Login/Register UI.
- `utils/` - Utility functions including the database connections, vector indexing, and PDF parsing modules.
- `requirements.txt` - Project dependencies.

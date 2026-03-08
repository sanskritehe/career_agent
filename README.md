# 🎯 Career AI Assistant - Multi-Agent System

A comprehensive AI-powered career assistant that helps you with resume analysis, job matching, and DSA learning preparation using advanced multi-agent architecture with Llama 3.3.

## Features

### 1. 💼 Resume Analysis Agent
- Extracts and analyzes resume content
- Identifies technical and soft skills
- Estimates experience level
- Highlights strengths and gaps
- Provides professional summary

### 2. 🎯 Job Matching Agent
- Matches your resume against target job roles
- Calculates readiness scores (0-100%)
- Provides detailed matching reasoning
- Suggests skill improvements
- Focuses on specific role requirements

### 3. 🎓 DSA Tutor Agent ⭐ NEW
A complete Data Structures & Algorithms learning system featuring:
- **Personalized Roadmap**: 3, 6, or 9-month learning plans based on your level
- **200+ Curated Problems**: Organized across 18+ DSA topics
- **AI-Powered Solutions**: Detailed explanations with code and complexity analysis
- **Progress Tracking**: Checkbox system for problem completion with statistics
- **Smart Learning**: Week-by-week schedules with milestone checkpoints
- **Interview Prep**: Readiness evaluation and focus area recommendations

## Project Structure

```
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── agents/
│   ├── resume_agent.py            # Resume analysis logic
│   ├── job_match_agent.py         # Job matching logic
│   ├── weighted_scorer.py         # Scoring utilities
│   └── dsa/                       # DSA TUTOR MODULE
│       ├── __init__.py
│       ├── dsa_topics_db.py       # 200+ problems, 18 topics
│       ├── dsa_tutor_agent.py     # AI agents for roadmap & solutions
│       ├── progress_tracker.py    # Progress management
│       ├── streamlit_ui.py        # UI components
│       └── README.md              # Detailed DSA documentation
├── utils/
│   ├── llm.py                     # LLM integration (Groq)
│   ├── pdf_parser.py              # Resume PDF parsing
│   ├── vector_db.py               # Vector database utilities
│   └── market_intel.py             # Market insights
```

## Installation

### Prerequisites
- Python 3.8+
- Groq API Key (get one free at https://console.groq.com)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd multi-agent-career-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Usage

### Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Module Selection

Use the sidebar to navigate between:
- **Resume & Job Match**: Upload resume and analyze job fit
- **🎯 DSA Tutor**: Start your personalized DSA learning journey

### Quick Start - DSA Tutor

1. Go to "🎯 DSA Tutor"
2. Navigate to "📋 Roadmap Generator"
3. Select your experience level (Beginner/Intermediate/Advanced)
4. Choose available time (3/6/9 months)
5. Generate your personalized roadmap
6. Start solving problems from "📚 Topics & Problems"
7. Track your progress in "📊 Progress Tracking"

## Technology Stack

- **Frontend**: Streamlit
- **LLM**: Groq - Llama 3.3 (free API)
- **Vector DB**: ChromaDB
- **Embeddings**: Sentence Transformers
- **PDF Processing**: pdfplumber
- **Data**: pandas
- **Backend**: Python

## Features Details

### Resume Analysis
- Extracts text from PDF resumes
- Uses AI to analyze skills and experience
- Provides structured JSON output
- Identifies missing skills for target role

### Job Matching
- Compares resume against specific roles
- Uses scoring rubric (0-100%)
- Provides reasoning for scores
- Makes actionable recommendations

### DSA Learning
- 200+ LeetCode-style problems
- 18 different DSA topics
- Difficulty levels: Easy, Medium, Hard
- Time estimates for each problem
- AI-generated explanations and solutions
- Progress tracking with checkboxes
- Topic-wise completion statistics

## API Keys & Configuration

### Groq API
Get your free API key at: https://console.groq.com/keys
- Free tier includes Llama 3.3 70B access
- Rate limited but suitable for learning

### .env File Template
```
GROQ_API_KEY=your_key_here
```

## Progress Tracking

Your DSA learning progress is saved automatically in `dsa_progress.json`:
- Problems solved
- Time spent on each problem
- Revision attempts
- Notes for each problem
- Overall completion statistics

## Contributing

To add new DSA problems or topics:
1. Edit `agents/dsa/dsa_topics_db.py`
2. Follow the existing problem format
3. Include all required fields (id, name, difficulty, links, etc.)
4. Restart the app to see changes

## Troubleshooting

### API Key Issues
```
Error: API key invalid or not set
```
- Verify `.env` file exists in project root
- Check API key is valid at https://console.groq.com

### PDF Upload Issues
```
Error: Could not extract text from PDF
```
- Ensure PDF is text-based (not scanned image)
- Try with a different PDF
- Check file size is reasonable

### Progress Not Saving
- Verify `dsa_progress.json` exists
- Check file write permissions
- Restart Streamlit app

## Roadmap

- [ ] Interview question simulator
- [ ] Code execution environment
- [ ] Timed problem contests
- [ ] Community leaderboards
- [ ] Mobile app
- [ ] Advanced analytics
- [ ] Peer discussion forums

## License

This project uses OpenSource tools and free APIs.

## Support

For issues and questions:
1. Check relevant README files in each module
2. Review code comments for implementation details
3. Open an issue on GitHub

---

**Built with ❤️ using AI-powered multi-agent architecture**

**Happy Learning & Best of Luck with your Career Goals! 🚀**

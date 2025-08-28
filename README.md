# AOG Family Devotionals RAG Application

A RAG (Retrieval-Augmented Generation) application that generates age-appropriate Assemblies of God devotionals for different family members using your existing Pinecone index and GPT-4o-mini.

## Features

- **Age-Specific Content**: Generates devotionals tailored for Children, Teens, Young Adults, and Adults
- **Topic-Based Generation**: Optional topic specification for focused devotionals  
- **RAG Integration**: Uses your existing "aog-devo" Pinecone index for content retrieval
- **Simple Web Interface**: Clean, family-friendly frontend
- **Print Functionality**: Easy printing of generated devotionals

## Architecture

- **Backend**: FastAPI with Pinecone and OpenAI integration
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **AI Model**: GPT-4o-mini for content generation
- **Vector Database**: Your existing Pinecone "aog-devo" index

## Prerequisites

1. **Python 3.8+** installed
2. **Environment Variables** in `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   ```
3. **Pinecone Index**: Your existing "aog-devo" index with devotional content

## Setup Instructions

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the project root with your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
```

### 3. Run the Backend Server

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

### 4. Serve the Frontend

You can serve the frontend using any web server. For development:

```bash
# Using Python's built-in server
cd frontend
python -m http.server 3000

# Or using Node.js http-server
cd frontend
npx http-server -p 3000
```

The frontend will be available at `http://localhost:3000`

### 5. Open the Application

Navigate to `http://localhost:3000` in your browser to use the application.

## Usage

1. **Select Age Group**: Choose from Children, Teens, Young Adults, or Adults
2. **Optional Topic**: Enter a specific topic or use suggested topics
3. **Generate**: Click "Generate Devotional" to create content
4. **View Results**: Read the generated devotional with Scripture, reflection, and prayer
5. **Print**: Use the print button to create a physical copy

## Age Group Characteristics

- **Children (5-12)**: Simple language, concrete examples, short content
- **Teens (13-17)**: Relatable scenarios, practical applications for school/friends  
- **Young Adults (18-25)**: Independence themes, career/relationship guidance
- **Adults (26+)**: Mature concepts, family/work balance, deeper theology

## API Endpoints

- `GET /` - Health check
- `POST /generate-devotional` - Generate age-specific devotional
- `GET /topics` - Get suggested topics
- `GET /health` - Server health status

## File Structure

```
aog-devo/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── rag_service.py       # RAG logic and OpenAI integration
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html          # Main web interface
│   ├── style.css           # Styling
│   └── script.js           # Frontend logic
├── devo.ipynb              # Original Pinecone setup notebook
└── .env                    # Environment variables (create this)
```

## Troubleshooting

1. **API Connection Issues**: Ensure backend is running on port 8000
2. **CORS Errors**: Make sure the frontend is served from a web server
3. **Authentication Errors**: Verify your OpenAI and Pinecone API keys
4. **Empty Results**: Check that your Pinecone index "aog-devo" contains data

## Customization

- **Modify Age Groups**: Edit the `age_group_prompts` in `rag_service.py`
- **Change Topics**: Update the topics list in `main.py`
- **Styling**: Customize the appearance in `frontend/style.css`
- **Content Length**: Adjust `max_length` values in age group configurations

## Free Deployment on Railway

### 1. Prepare for Deployment
```bash
# Make sure all files are ready
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. Deploy on Railway
1. Visit [railway.app](https://railway.app) and sign up
2. Click "Start a New Project" → "Deploy from GitHub repo"
3. Select your `aog-devo` repository
4. Railway will automatically detect and deploy your app

### 3. Set Environment Variables
In Railway dashboard:
- Go to Variables tab
- Add: `OPENAI_API_KEY=your_key_here`
- Add: `PINECONE_API_KEY=your_key_here`

### 4. Access Your App
- Railway will provide a public URL (e.g., `https://aog-devo-production.up.railway.app`)
- Your app will be live and accessible worldwide!

### Alternative: Render Deployment
1. Visit [render.com](https://render.com) and sign up
2. Create "New Web Service" from GitHub
3. Set environment variables in dashboard
4. App will be available at your Render URL

## Support

For issues or questions, please check:
1. API keys are correctly set in environment variables
2. Deployment logs for any errors
3. Pinecone index "aog-devo" exists and contains data
4. Internet connection for API calls

## Deployment Features
- ✅ Single deployment (backend + frontend combined)
- ✅ Environment variable configuration
- ✅ Automatic scaling
- ✅ HTTPS enabled
- ✅ Global CDN
import json
import logging
import os
import random
import re
from flask import Flask, render_template_string, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import pinecone

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize services
openai_client = OpenAI()

# Initialize Pinecone
pinecone_index = None
try:
    pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws"))
    pinecone_index = pinecone.Index("aog-devo")
    logger.info("✅ Pinecone initialized successfully")
except Exception as e:
    logger.warning(f"⚠️ Pinecone initialization failed: {e}. Will use fallback content.")
    pinecone_index = None

# Bible verses for random selection when none provided
RANDOM_BIBLE_VERSES = [
    {"reference": "John 3:16", "text": "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life."},
    {"reference": "Philippians 4:13", "text": "I can do all this through him who gives me strength."},
    {"reference": "Jeremiah 29:11", "text": "For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you, to give you hope and a future."},
    {"reference": "Romans 8:28", "text": "And we know that in all things God works for the good of those who love him, who have been called according to his purpose."},
    {"reference": "Proverbs 3:5-6", "text": "Trust in the Lord with all your heart and lean not on your own understanding; in all your ways submit to him, and he will make your paths straight."},
    {"reference": "Isaiah 40:31", "text": "But those who hope in the Lord will renew their strength. They will soar on wings like eagles; they will run and not grow weary, they will walk and not be faint."},
    {"reference": "Matthew 28:20", "text": "And surely I am with you always, to the very end of the age."},
    {"reference": "Psalm 23:1", "text": "The Lord is my shepherd, I lack nothing."},
    {"reference": "1 Corinthians 13:4-5", "text": "Love is patient, love is kind. It does not envy, it does not boast, it is not proud. It does not dishonor others, it is not self-seeking, it is not easily angered, it keeps no record of wrongs."},
    {"reference": "Ephesians 2:8-9", "text": "For it is by grace you have been saved, through faith—and this is not from yourselves, it is the gift of God—not by works, so that no one can boast."}
]

# Age group configurations
AGE_GROUP_PROMPTS = {
    "children": {
        "system_prompt": "You are creating a devotional for children (ages 5-12). Use simple language, short sentences, concrete examples, and include fun applications. Keep the devotional short and engaging. Include a simple prayer they can understand and repeat.",
        "max_length": 300
    },
    "teens": {
        "system_prompt": "You are creating a devotional for teenagers (ages 13-17). Use relatable language, address real-life situations teens face, include practical applications for school and friendships. Make it relevant to their daily struggles and victories.",
        "max_length": 500
    },
    "young_adults": {
        "system_prompt": "You are creating a devotional for young adults (ages 18-25). Address themes of independence, career decisions, relationships, and spiritual growth. Use mature but accessible language with practical applications for this transitional life stage.",
        "max_length": 600
    },
    "adults": {
        "system_prompt": "You are creating a devotional for adults (ages 26+). Address mature spiritual concepts, family responsibilities, work-life balance, and deeper theological insights. Include practical applications for family life and community involvement.",
        "max_length": 700
    }
}

def extract_scripture_reference(text):
    """Extract scripture reference from text using regex patterns"""
    # Common scripture reference patterns
    patterns = [
        r'\b(\d?\s*[A-Z][a-z]+(?:\s+\d+)?)\s+(\d+):(\d+(?:-\d+)?)\b',  # John 3:16, 1 John 2:1-5
        r'\b([A-Z][a-z]+)\s+(\d+):(\d+(?:-\d+)?)\b',  # John 3:16-17
        r'\b(\d?\s*[A-Z][a-z]+)\s+(\d+)\b'  # Psalm 23 (whole chapter)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            if len(match.groups()) == 3:
                book, chapter, verse = match.groups()
                return f"{book.strip()} {chapter}:{verse}"
            elif len(match.groups()) == 2:
                book, chapter = match.groups()
                return f"{book.strip()} {chapter}"
    
    return None

def detect_age_group(text):
    """Detect age group from the user's prompt"""
    text_lower = text.lower()
    
    age_keywords = {
        "children": ["children", "child", "kids", "kid", "young children", "5-12", "elementary"],
        "teens": ["teens", "teen", "teenagers", "teenager", "youth", "13-17", "high school", "adolescent"],
        "young_adults": ["young adults", "young adult", "college", "18-25", "university", "emerging adults"],
        "adults": ["adults", "adult", "grown-ups", "grown up", "parents", "26+", "mature"]
    }
    
    for age_group, keywords in age_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return age_group
    
    return "adults"  # Default to adults if no specific age group detected

def get_relevant_content_from_pinecone(query, top_k=3):
    """Retrieve relevant content from Pinecone index"""
    # Check if Pinecone is available
    if pinecone_index is None:
        logger.info("Using fallback content (Pinecone not available)")
        return """
        The Bible teaches us that faith is the foundation of our relationship with God. 
        Through prayer and reading His Word, we can strengthen our faith daily.
        Living by faith means taking steps of obedience even when the path ahead seems unclear.
        God honors those who trust in Him with all their heart.
        When we face challenges in life, our faith becomes our anchor. It keeps us grounded 
        in God's love and helps us remember that He has a plan for our lives.
        """
    
    try:
        # Create embedding for the query
        query_response = openai_client.embeddings.create(
            input=query,
            model="text-embedding-3-large"
        )
        query_embedding = query_response.data[0].embedding
        
        # Search Pinecone for similar content
        search_response = pinecone_index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            include_values=False
        )
        
        # Extract content from matches
        relevant_content = []
        for match in search_response.matches:
            if match.metadata and 'text' in match.metadata:
                relevant_content.append(match.metadata['text'])
        
        if relevant_content:
            return '\n\n'.join(relevant_content)
        else:
            logger.info("No relevant content found in Pinecone, using fallback")
            return """
            The Bible teaches us that faith is the foundation of our relationship with God. 
            Through prayer and reading His Word, we can strengthen our faith daily.
            Living by faith means taking steps of obedience even when the path ahead seems unclear.
            God honors those who trust in Him with all their heart.
            """
        
    except Exception as e:
        logger.error(f"Error retrieving content from Pinecone: {str(e)}")
        # Return fallback content
        return """
        The Bible teaches us that faith is the foundation of our relationship with God. 
        Through prayer and reading His Word, we can strengthen our faith daily.
        Living by faith means taking steps of obedience even when the path ahead seems unclear.
        God honors those who trust in Him with all their heart.
        """

def generate_devotional(user_prompt):
    """Generate a devotional based on user prompt"""
    try:
        # Extract scripture reference from prompt
        scripture_ref = extract_scripture_reference(user_prompt)
        
        # If no scripture found, use a random one
        if not scripture_ref:
            random_verse = random.choice(RANDOM_BIBLE_VERSES)
            scripture_ref = random_verse["reference"]
        
        # Detect age group from prompt
        age_group = detect_age_group(user_prompt)
        age_config = AGE_GROUP_PROMPTS[age_group]
        
        # Get relevant content from Pinecone
        search_query = f"{user_prompt} {scripture_ref}"
        relevant_content = get_relevant_content_from_pinecone(search_query)
        
        # Generate devotional using OpenAI
        prompt = f"""
        {age_config['system_prompt']}
        
        User Request: {user_prompt}
        Scripture Reference: {scripture_ref}
        Age Group Detected: {age_group}
        
        Based on the following Assemblies of God devotional content and the scripture reference provided, 
        create an original devotional appropriate for the {age_group} age group.
        
        Relevant AOG Content:
        {relevant_content}
        
        Create a devotional following the official AOG Family Devotions format:
        
        STRUCTURE:
        - Question of the Day (central theme question)
        - LISTEN to God through His Word (Scripture reading with context)
        - LEARN from God's Word (deeper understanding with Q&A)
        - LIVE God's Word (practical application with Q&A)
        - PRAY about It (closing prayer)
        
        Use the scripture reference: {scripture_ref}
        Keep the content age-appropriate and under {age_config['max_length']} words total.
        Make it engaging, biblically sound, and interactive with questions.
        
        Return the response in this exact JSON format:
        {{
            "title": "Day X—FAMILY DEVOTIONS",
            "question_of_day": "Question of the Day: [your question here]",
            "listen_scripture": "{scripture_ref}",
            "listen_content": "Pray and ask God to speak to you before you read today's Scripture.\\n\\nRead {scripture_ref}.\\n\\n[Context paragraph]\\n\\nQuestion\\n[Question about passage]\\nAnswer: [Answer]",
            "learn_content": "Question\\n[Deeper question]\\nAnswer: [Answer]\\n\\n[Additional explanation if needed]",
            "live_content": "[Application paragraph]\\n\\nQuestion\\n[Personal application question]\\nAnswer: Answers will vary.\\n\\nQuestion\\n[Follow-up practical question]\\nAnswer: Answers will vary.",
            "prayer": "Dear God, [prayer addressing the day's theme]. I love You, God. Amen.",
            "age_group": "{age_group}",
            "scripture_reference": "{scripture_ref}"
        }}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Christian devotional writer specializing in age-appropriate spiritual content using Assemblies of God format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse the JSON response
        content = response.choices[0].message.content.strip()
        
        # Extract JSON from the response
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            json_str = content[start:end]
            devotional_data = json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            devotional_data = {
                "title": "Family Devotional",
                "question_of_day": "Question of the Day: How can we grow closer to God today?",
                "listen_scripture": scripture_ref,
                "listen_content": f"Pray and ask God to speak to you before you read today's Scripture.\n\nRead {scripture_ref}.\n\nGod's Word is powerful and speaks to our hearts. This passage reminds us of God's love and faithfulness.\n\nQuestion\nWhat does this scripture teach us about God?\nAnswer: God is loving and faithful to His people.",
                "learn_content": "Question\nHow can we apply this teaching in our lives?\nAnswer: By trusting in God's goodness and following His ways.\n\nWhen we study God's Word, we learn more about His character and His plans for us.",
                "live_content": "Living out God's Word means putting what we learn into practice in our daily lives.\n\nQuestion\nWhat is one way you can live out this scripture today?\nAnswer: Answers will vary.\n\nQuestion\nHow can you share God's love with others?\nAnswer: Answers will vary.",
                "prayer": f"Dear God, thank You for Your Word and the lessons it teaches us. Help us to live according to Your will. I love You, God. Amen.",
                "age_group": age_group,
                "scripture_reference": scripture_ref
            }
        
        return devotional_data
        
    except Exception as e:
        logger.error(f"Error generating devotional: {str(e)}")
        raise e

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AOG Devotional Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Georgia, serif;
            line-height: 1.6;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            font-weight: 300;
        }
        
        header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        main {
            padding: 2rem;
        }
        
        .form-section {
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        .examples {
            background: #e3f2fd;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
        }
        
        .examples h3 {
            color: #1976d2;
            margin-bottom: 0.5rem;
            font-size: 1rem;
        }
        
        .examples ul {
            list-style: none;
            font-size: 0.9rem;
        }
        
        .examples li {
            margin-bottom: 0.3rem;
            color: #555;
            font-style: italic;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #333;
        }
        
        textarea {
            width: 100%;
            min-height: 120px;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 16px;
            font-family: inherit;
            resize: vertical;
            transition: border-color 0.3s ease;
        }
        
        textarea:focus {
            outline: none;
            border-color: #4facfe;
        }
        
        button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.3s ease;
        }
        
        button:hover {
            transform: translateY(-2px);
        }
        
        button:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }
        
        .spinner {
            display: none;
            width: 20px;
            height: 20px;
            border: 2px solid #ffffff33;
            border-top: 2px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .result {
            display: none;
            animation: fadeIn 0.5s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .devotional-card {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            border-radius: 15px;
            padding: 2rem;
        }
        
        .devotional-card h2 {
            font-size: 2rem;
            color: #333;
            margin-bottom: 1.5rem;
            text-align: center;
            border-bottom: 2px solid #fff;
            padding-bottom: 1rem;
        }
        
        .question-day {
            font-size: 1.4rem;
            color: #667eea;
            font-weight: 600;
            margin-bottom: 2rem;
            text-align: center;
            font-style: italic;
        }
        
        .devotional-section {
            margin-bottom: 2rem;
        }
        
        .devotional-section h3 {
            font-size: 1.3rem;
            color: #555;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(255,255,255,0.8);
            padding: 0.8rem;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .devotional-content {
            background: rgba(255,255,255,0.7);
            padding: 1.5rem;
            border-radius: 8px;
            font-size: 1.1rem;
            line-height: 1.7;
            white-space: pre-line;
        }
        
        .metadata {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 1rem;
            justify-content: center;
        }
        
        .metadata span {
            background: rgba(255,255,255,0.8);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            color: #666;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #f5c6cb;
            margin-bottom: 1rem;
        }
        
        .actions {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-top: 2rem;
        }
        
        .actions button {
            width: auto;
            background: #fff;
            border: 2px solid #667eea;
            color: #667eea;
        }
        
        .actions button:hover {
            background: #667eea;
            color: white;
        }
        
        footer {
            background: #333;
            color: white;
            padding: 1rem;
            text-align: center;
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            body { padding: 10px; }
            header h1 { font-size: 2rem; }
            main { padding: 1rem; }
            .form-section { padding: 1rem; }
            .devotional-card { padding: 1.5rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🙏 AOG Devotional Generator</h1>
            <p>AI-powered devotionals from scripture using Assemblies of God format</p>
        </header>
        
        <main>
            <div class="form-section">
                <div class="examples">
                    <h3>💡 Example Requests:</h3>
                    <ul>
                        <li>"Create a devotional for children about God's love using John 3:16"</li>
                        <li>"Make a teen devotional on faith and trust"</li>
                        <li>"Generate an adult devotional about forgiveness using Matthew 6:14-15"</li>
                        <li>"Write a devotional for young adults on perseverance"</li>
                        <li>"Create a children's devotional about kindness"</li>
                    </ul>
                </div>
                
                <form id="devotionalForm">
                    <label for="prompt">Enter your devotional request:</label>
                    <textarea 
                        id="prompt" 
                        name="prompt" 
                        placeholder="Describe what kind of devotional you'd like... Include the age group (children, teens, young adults, adults) and optionally a specific scripture reference or topic."
                        required
                    ></textarea>
                    
                    <button type="submit" id="generateBtn">
                        <span>Generate Devotional</span>
                        <div class="spinner" id="spinner"></div>
                    </button>
                </form>
            </div>
            
            <div id="error" class="error" style="display: none;"></div>
            
            <div id="result" class="result">
                <!-- Devotional content will be inserted here -->
            </div>
        </main>
        
        <footer>
            <p>Powered by OpenAI GPT-4 • Assemblies of God Content • Pinecone Vector Database</p>
        </footer>
    </div>
    
    <script>
        document.getElementById('devotionalForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const prompt = document.getElementById('prompt').value.trim();
            const button = document.getElementById('generateBtn');
            const spinner = document.getElementById('spinner');
            const errorDiv = document.getElementById('error');
            const resultDiv = document.getElementById('result');
            
            if (!prompt) {
                showError('Please enter a devotional request.');
                return;
            }
            
            // Show loading state
            button.disabled = true;
            spinner.style.display = 'inline-block';
            errorDiv.style.display = 'none';
            resultDiv.style.display = 'none';
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ prompt: prompt })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    displayDevotional(data);
                } else {
                    showError(data.error || 'An error occurred. Please try again.');
                }
                
            } catch (error) {
                console.error('Error:', error);
                showError('Network error. Please check your connection and try again.');
            } finally {
                button.disabled = false;
                spinner.style.display = 'none';
            }
        });
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            errorDiv.scrollIntoView({ behavior: 'smooth' });
        }
        
        function displayDevotional(devotional) {
            const resultDiv = document.getElementById('result');
            
            const ageGroupMap = {
                'children': 'Children (5-12 years)',
                'teens': 'Teens (13-17 years)',
                'young_adults': 'Young Adults (18-25 years)',
                'adults': 'Adults (26+ years)'
            };
            
            resultDiv.innerHTML = `
                <div class="devotional-card">
                    <h2>${devotional.title}</h2>
                    <div class="question-day">${devotional.question_of_day}</div>
                    
                    <div class="devotional-section">
                        <h3>👂 LISTEN to God through His Word</h3>
                        <div class="devotional-content">${devotional.listen_content}</div>
                    </div>
                    
                    <div class="devotional-section">
                        <h3>🎓 LEARN from God's Word</h3>
                        <div class="devotional-content">${devotional.learn_content}</div>
                    </div>
                    
                    <div class="devotional-section">
                        <h3>💡 LIVE God's Word</h3>
                        <div class="devotional-content">${devotional.live_content}</div>
                    </div>
                    
                    <div class="devotional-section">
                        <h3>🙏 PRAY about It</h3>
                        <div class="devotional-content">${devotional.prayer}</div>
                    </div>
                    
                    <div class="metadata">
                        <span>Age Group: ${ageGroupMap[devotional.age_group] || devotional.age_group}</span>
                        <span>Scripture: ${devotional.scripture_reference}</span>
                    </div>
                </div>
                
                <div class="actions">
                    <button type="button" onclick="window.print()">Print Devotional</button>
                    <button type="button" onclick="document.getElementById('devotionalForm').reset(); document.getElementById('result').style.display='none'; document.getElementById('prompt').focus();">Create Another</button>
                </div>
            `;
            
            resultDiv.style.display = 'block';
            resultDiv.scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Main application page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    """Generate devotional endpoint"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'error': 'Please provide a devotional request.'}), 400
        
        # Check if prompt is clear enough (basic validation)
        if len(prompt) < 10:
            return jsonify({'error': 'Please provide a more detailed request. Include the age group and what kind of devotional you would like.'}), 400
        
        # Generate devotional
        devotional = generate_devotional(prompt)
        return jsonify(devotional)
        
    except Exception as e:
        logger.error(f"Error in /generate endpoint: {str(e)}")
        return jsonify({'error': 'Sorry, there was an error generating your devotional. Please try again.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
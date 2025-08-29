# AOG Devotional Generator

A simple Flask RAG (Retrieval-Augmented Generation) application that generates age-appropriate Assemblies of God devotionals from scripture passages using AI and your existing Pinecone vector database.

## Features

- **Single-File Application**: Everything contained in one `app.py` file for simplicity
- **Scripture-Based**: Generate devotionals from any Bible verse or passage
- **Age-Appropriate Content**: Automatically detects and creates content for Children, Teens, Young Adults, and Adults
- **RAG Integration**: Uses your existing "aog-devo" Pinecone index for relevant AOG content
- **AOG Format**: Follows the official Assemblies of God Family Devotions format:
  - Question of the Day
  - LISTEN to God through His Word
  - LEARN from God's Word  
  - LIVE God's Word
  - PRAY about It
- **Smart Scripture Detection**: Automatically extracts Bible references from user prompts
- **Random Scripture Fallback**: Uses random Bible verses when none are specified
- **Clean Interface**: Simple, responsive web interface with examples

## How It Works

1. User enters a request like "Create a devotional for teens about faith using John 3:16"
2. App detects age group (teens) and scripture reference (John 3:16)
3. Retrieves relevant content from your Pinecone "aog-devo" index
4. Uses OpenAI GPT-4o-mini to generate age-appropriate devotional in AOG format
5. Displays formatted devotional with print functionality

## Prerequisites

1. **Python 3.8+** installed
2. **Environment Variables** in `.env` file:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   ```
3. **Pinecone Index**: Your existing "aog-devo" index with devotional content

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1-aws
```

### 3. Run the Application
```bash
python app.py
```

Visit: **http://localhost:5000**

## Usage Examples

### With Scripture Reference:
- "Create a devotional for children about God's love using John 3:16"
- "Make an adult devotional on forgiveness using Matthew 6:14-15"
- "Generate a teen devotional about perseverance using Philippians 4:13"

### Without Scripture Reference:
- "Write a devotional for young adults on faith and trust"
- "Create a children's devotional about kindness"  
- "Make a teen devotional on prayer"

The app will automatically choose an appropriate Bible verse when none is specified.

## Age Group Keywords

The app automatically detects age groups from your prompt:

- **Children**: children, child, kids, kid, 5-12, elementary
- **Teens**: teens, teen, teenagers, youth, 13-17, high school
- **Young Adults**: young adults, college, 18-25, university  
- **Adults**: adults, adult, parents, 26+, mature (default)

## File Structure

```
aog-devo/
├── app.py              # Complete Flask application (single file)
├── requirements.txt    # Python dependencies  
├── devo.ipynb         # Original Pinecone setup notebook
├── .env               # Environment variables (create this)
└── README.md          # This file
```

## API Endpoints

- `GET /` - Main application interface
- `POST /generate` - Generate devotional from prompt

## Dependencies

- **Flask**: Web framework
- **OpenAI**: AI content generation  
- **Pinecone**: Vector database for RAG
- **python-dotenv**: Environment variable management

## Customization

### Modify Age Group Prompts
Edit the `AGE_GROUP_PROMPTS` dictionary in `app.py` to change how devotionals are generated for each age group.

### Add More Random Bible Verses  
Update the `RANDOM_BIBLE_VERSES` list in `app.py` to include more scripture options.

### Change Styling
The HTML template is embedded in `app.py`. Modify the CSS in the `HTML_TEMPLATE` variable to customize appearance.

## Troubleshooting

1. **API Errors**: Verify your OpenAI and Pinecone API keys in the `.env` file
2. **Empty Results**: Check that your Pinecone index "aog-devo" contains data
3. **Port Conflicts**: If port 5000 is in use, change it in the last line of `app.py`
4. **Scripture Detection Issues**: The app uses regex patterns - you may need to adjust these for unusual scripture formats

## Example Output

The generated devotionals follow the AOG format:

```
Day 1—FAMILY DEVOTIONS

Question of the Day: How does God show His love for us?

👂 LISTEN to God through His Word
Pray and ask God to speak to you before you read today's Scripture.

Read John 3:16.
[Scripture context and explanation...]

🎓 LEARN from God's Word  
[Deeper questions and biblical insights...]

💡 LIVE God's Word
[Practical applications and reflection questions...]

🙏 PRAY about It
Dear God, [age-appropriate prayer]. I love You, God. Amen.
```

## Support

For issues with the application:
1. Check that your API keys are correctly set
2. Verify your Pinecone index "aog-devo" exists and contains data  
3. Review the console/logs for error messages
4. Try simpler prompts if generation fails

---

*Powered by OpenAI GPT-4 • Assemblies of God Content • Pinecone Vector Database*
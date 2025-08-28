import os
import json
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
import pinecone

load_dotenv()

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.openai_client = OpenAI()
        pinecone.config.api_key = os.getenv("PINECONE_API_KEY")
        self.index = pinecone.Index("aog-devo")
        self.embedding_model = "text-embedding-3-large"
        
        self.age_group_prompts = {
            "children": {
                "system_prompt": """You are creating a devotional for children (ages 5-12). Use simple language, 
                short sentences, concrete examples, and include fun applications. Keep the devotional short and engaging.
                Include a simple prayer they can understand and repeat.""",
                "max_length": 300
            },
            "teens": {
                "system_prompt": """You are creating a devotional for teenagers (ages 13-17). Use relatable language,
                address real-life situations teens face, include practical applications for school and friendships.
                Make it relevant to their daily struggles and victories.""",
                "max_length": 500
            },
            "young_adults": {
                "system_prompt": """You are creating a devotional for young adults (ages 18-25). Address themes of 
                independence, career decisions, relationships, and spiritual growth. Use mature but accessible language
                with practical applications for this transitional life stage.""",
                "max_length": 600
            },
            "adults": {
                "system_prompt": """You are creating a devotional for adults (ages 26+). Address mature spiritual concepts,
                family responsibilities, work-life balance, and deeper theological insights. Include practical applications
                for family life and community involvement.""",
                "max_length": 700
            }
        }

    async def generate_devotional(self, age_group: str, topic: Optional[str] = None) -> Dict[str, Any]:
        try:
            # Create search query
            search_query = topic if topic else "faith spiritual growth Bible devotional"
            
            # Get relevant content from Pinecone
            relevant_content = await self._retrieve_relevant_content(search_query)
            
            # Generate age-appropriate devotional
            devotional = await self._generate_age_appropriate_content(
                age_group, relevant_content, topic
            )
            
            return devotional
            
        except Exception as e:
            logger.error(f"Error in generate_devotional: {str(e)}")
            raise e

    async def _retrieve_relevant_content(self, query: str, top_k: int = 3) -> str:
        try:
            # Create embedding for the query
            query_response = self.openai_client.embeddings.create(
                input=query,
                model=self.embedding_model
            )
            query_embedding = query_response.data[0].embedding
            
            # Search Pinecone for similar content
            search_response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                include_values=False
            )
            
            # Combine relevant content
            relevant_texts = []
            for match in search_response.matches:
                if match.metadata and 'text' in match.metadata:
                    relevant_texts.append(match.metadata['text'])
            
            return "\n\n".join(relevant_texts)
            
        except Exception as e:
            logger.error(f"Error retrieving content: {str(e)}")
            return "Faith is the foundation of our relationship with God."

    async def _generate_age_appropriate_content(
        self, age_group: str, context: str, topic: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            age_config = self.age_group_prompts[age_group]
            
            topic_instruction = f" Focus on the topic: {topic}." if topic else ""
            
            prompt = f"""
            {age_config['system_prompt']}
            
            Based on the following Assemblies of God devotional content, create an original devotional 
            appropriate for the {age_group} age group.{topic_instruction}
            
            Context from existing devotionals:
            {context}
            
            Create a devotional with the following structure:
            1. A compelling title
            2. A relevant Bible verse (include reference)
            3. Main devotional content (appropriate length for age group)
            4. A closing prayer
            
            Keep the total content under {age_config['max_length']} words for the main content section.
            Make it engaging, biblically sound, and age-appropriate.
            
            Return the response in this exact JSON format:
            {{
                "title": "Title Here",
                "scripture": "Bible verse with reference",
                "content": "Main devotional content here",
                "prayer": "Closing prayer here"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a Christian devotional writer specializing in age-appropriate spiritual content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            try:
                # Find JSON in the response
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
                devotional_data = json.loads(json_str)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.warning("Failed to parse JSON response, using fallback")
                devotional_data = {
                    "title": "Daily Devotional",
                    "scripture": "Proverbs 3:5-6 - Trust in the LORD with all your heart and lean not on your own understanding; in all your ways submit to him, and he will make your paths straight.",
                    "content": content,
                    "prayer": "Dear God, help us to trust in You and follow Your ways. Amen."
                }
            
            # Add metadata
            devotional_data.update({
                "age_group": age_group,
                "topic": topic
            })
            
            return devotional_data
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            # Return a fallback devotional
            return {
                "title": "God's Love for You",
                "scripture": "John 3:16 - For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life.",
                "content": "God loves you so much! This is the most important truth you can know today.",
                "prayer": "Dear God, thank You for Your amazing love. Help us to share that love with others. Amen.",
                "age_group": age_group,
                "topic": topic
            }
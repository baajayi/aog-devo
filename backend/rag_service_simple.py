import os
import json
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.openai_client = OpenAI()
        self.embedding_model = "text-embedding-3-large"
        
        # Sample devotional content for demonstration
        self.sample_content = """
        The Bible teaches us that faith is the foundation of our relationship with God. 
        In Hebrews 11:1, we read: "Now faith is confidence in what we hope for and assurance 
        about what we do not see." This verse reminds us that faith involves trusting in God's 
        promises even when we cannot see the outcome.

        When we face challenges in life, our faith becomes our anchor. It keeps us grounded 
        in God's love and helps us remember that He has a plan for our lives. Through prayer 
        and reading His Word, we can strengthen our faith daily.

        Living by faith means taking steps of obedience even when the path ahead seems unclear. 
        God honors those who trust in Him with all their heart. As we grow in our faith, we 
        become more like Jesus and can be a light to others around us.
        """
        
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
            # Use sample content for now (in production, this would query Pinecone)
            relevant_content = self._get_sample_content(topic)
            
            # Generate age-appropriate devotional
            devotional = await self._generate_age_appropriate_content(
                age_group, relevant_content, topic
            )
            
            return devotional
            
        except Exception as e:
            logger.error(f"Error in generate_devotional: {str(e)}")
            raise e

    def _get_sample_content(self, topic: Optional[str] = None) -> str:
        # For demo purposes, return sample content
        # In production, this would query your Pinecone index
        return self.sample_content

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
            
            Create a devotional following the official AOG Family Devotions format:
            
            STRUCTURE:
            - Question of the Day (central theme question)
            - LISTEN to God through His Word (Scripture reading with context)
            - LEARN from God's Word (deeper understanding with Q&A)
            - LIVE God's Word (practical application with Q&A)
            - PRAY about It (closing prayer)
            
            Keep the content age-appropriate and under {age_config['max_length']} words total.
            Make it engaging, biblically sound, and interactive with questions.
            
            Return the response in this exact JSON format:
            {{
                "title": "Day X—FAMILY DEVOTIONS",
                "question_of_day": "Question of the Day: [your question here]",
                "listen_scripture": "[Scripture reference]",
                "listen_content": "Pray and ask God to speak to you before you read today's Scripture.\n\nRead [reference].\n\n[Context paragraph]\n\nQuestion\n[Question about passage]\nAnswer: [Answer]",
                "learn_content": "Question\n[Deeper question]\nAnswer: [Answer]\n\n[Additional explanation if needed]",
                "live_content": "[Application paragraph]\n\nQuestion\n[Personal application question]\nAnswer: Answers will vary.\n\nQuestion\n[Follow-up practical question]\nAnswer: Answers will vary.",
                "prayer": "Dear God, [prayer addressing the day's theme]. I love You, God. Amen."
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """You are a Christian devotional writer specializing in age-appropriate spiritual content. "
                    Use content from the context only and nothing from outside sources.
                    Use the same format specified in the context."""},
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
                    "title": "Day 1—FAMILY DEVOTIONS",
                    "question_of_day": "Question of the Day: How can we trust God today?",
                    "listen_scripture": "Proverbs 3:5-6",
                    "listen_content": "Pray and ask God to speak to you before you read today's Scripture.\n\nRead Proverbs 3:5-6.\n\nGod wants us to trust Him completely. When we don't understand what's happening, we can still trust that God knows what's best for us.\n\nQuestion\nWhat does this verse tell us to do?\nAnswer: Trust in the LORD with all our heart.",
                    "learn_content": "Question\nWhat should we not lean on according to verse 5?\nAnswer: Our own understanding.\n\nGod's wisdom is greater than ours. He sees the whole picture when we only see a small part.",
                    "live_content": "When we trust God and follow His ways, He promises to make our paths straight. This means He will guide us in the right direction.\n\nQuestion\nWhat is one area where you need to trust God more?\nAnswer: Answers will vary.\n\nQuestion\nHow can you show that you trust God this week?\nAnswer: Answers will vary.",
                    "prayer": "Dear God, thank You for wanting to guide my life. Help me to trust You completely, even when I don't understand. I love You, God. Amen."
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
                "title": "Day 1—FAMILY DEVOTIONS",
                "question_of_day": "Question of the Day: How much does God love us?",
                "listen_scripture": "John 3:16",
                "listen_content": "Pray and ask God to speak to you before you read today's Scripture.\n\nRead John 3:16.\n\nThis is one of the most famous verses in the Bible because it tells us about God's amazing love for us.\n\nQuestion\nWhat did God give because He loved the world?\nAnswer: His one and only Son.",
                "learn_content": "Question\nWhat happens to those who believe in Jesus?\nAnswer: They will not perish but have eternal life.\n\nGod's love is so great that He gave His most precious gift - Jesus - to save us.",
                "live_content": "God loves you so much! This is the most important truth you can know today. When we understand God's love, we want to share it with others.\n\nQuestion\nHow does it feel to know God loves you this much?\nAnswer: Answers will vary.\n\nQuestion\nHow can you show God's love to someone today?\nAnswer: Answers will vary.",
                "prayer": "Dear God, thank You for Your amazing love. Help us to share that love with others. I love You, God. Amen.",
                "age_group": age_group,
                "topic": topic
            }
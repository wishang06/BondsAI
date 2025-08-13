"""Core architecture for BondsAI - Dating App Personality Profiler."""

import asyncio
import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from .config import config


class Message:
    """Represents a chat message."""
    
    def __init__(self, role: str, content: str):
        """Initialize a message."""
        self.role = role
        self.content = content
    
    def to_dict(self) -> Dict[str, str]:
        """Convert message to dictionary format for OpenAI API."""
        return {"role": self.role, "content": self.content}


class PersonalityProfile:
    """Tracks user personality traits and preferences."""
    
    def __init__(self):
        """Initialize personality profile."""
        self.traits = {
            "communication_style": [],
            "social_preferences": [],
            "values": [],
            "interests": [],
            "lifestyle": [],
            "relationship_goals": [],
            "deal_breakers": [],
            "personality_type": "",
            "conversation_insights": []
        }
        self.conversation_count = 0
        self.topics_covered = set()
    
    def add_insight(self, category: str, insight: str) -> None:
        """Add a personality insight."""
        if category in self.traits:
            if isinstance(self.traits[category], list):
                self.traits[category].append(insight)
            else:
                self.traits[category] = insight
    
    def get_summary(self) -> str:
        """Generate a concise personality summary."""
        if self.conversation_count < 5:
            return "Still getting to know this person..."
        
        summary_parts = []
        
        # Personality overview
        personality_traits = []
        if self.traits["communication_style"]:
            personality_traits.extend(self.traits["communication_style"][:2])
        if self.traits["social_preferences"]:
            personality_traits.extend(self.traits["social_preferences"][:2])
        
        if personality_traits:
            summary_parts.append(f"**Personality**: {', '.join(personality_traits)}")
        
        # Values and interests
        if self.traits["values"]:
            summary_parts.append(f"**Core Values**: {', '.join(self.traits['values'][:3])}")
        
        if self.traits["interests"]:
            summary_parts.append(f"**Key Interests**: {', '.join(self.traits['interests'][:3])}")
        
        # Lifestyle and goals
        if self.traits["lifestyle"]:
            summary_parts.append(f"**Lifestyle**: {', '.join(self.traits['lifestyle'][:2])}")
        
        if self.traits["relationship_goals"]:
            summary_parts.append(f"**Relationship Goals**: {', '.join(self.traits['relationship_goals'][:2])}")
        
        if self.traits["deal_breakers"]:
            summary_parts.append(f"**Deal-breakers**: {', '.join(self.traits['deal_breakers'][:2])}")
        
        return "\n".join(summary_parts) if summary_parts else "Still getting to know this person..."


class DatingAssistant:
    """Main conversation manager with personality profiling for dating app."""
    
    def __init__(self):
        """Initialize the dating assistant."""
        self.client = AsyncOpenAI(api_key=config.openai_api_key)
        self.messages: List[Message] = []
        self.model = config.openai_model
        self.temperature = config.openai_temperature
        self.max_tokens = config.openai_max_tokens
        self.profile = PersonalityProfile()
        self.conversation_phase = "introduction"
        self.is_first_message = True
        
        # Dating-specific conversation prompts
        self.system_prompt = """You are a charming, friendly, and genuinely curious AI designed to help people find meaningful connections through a dating app. Your role is to:

1. **Be warm and engaging**: Use emojis, show genuine interest, and create a comfortable atmosphere
2. **Ask thoughtful follow-up questions**: Build on their responses naturally, don't just move to the next topic
3. **Gather personality insights**: Learn about their values, communication style, interests, and relationship goals
4. **Be conversational**: Vary your language, use casual conversation, feel like talking to a real person
5. **Show active listening**: Reference what they've shared and demonstrate you're paying attention
6. **Progressive disclosure**: Start light and fun, gradually explore deeper topics
7. **Be encouraging**: Create a safe space for sharing personal information
8. **Ask 1-2 follow-up questions MAX**: Don't dwell too long on one topic - move to new areas after 1-2 exchanges (Unless there is a smooth transition to a new topic that is connected to the previous topic)
9. **Cover diverse topics quickly**: Explore different personality dimensions in each conversation
10. **Gather broad personality insights**: Learn about values, communication style, social preferences, interests, lifestyle, and relationship goals
11. **Show active listening**: Reference what they've shared briefly, then move to new topics

Key traits to identify quickly:
- Communication style (direct, playful, thoughtful, analytical, etc.)
- Social preferences (introvert/extrovert, group vs individual, collaborative vs independent)
- Core values and beliefs (what drives them, principles they live by)
- Interests and hobbies (creative, analytical, physical, social, etc.)
- Lifestyle preferences (routine vs spontaneity, work-life balance, etc.)
- Relationship goals and deal-breakers
- Personality type indicators (MBTI-style insights)

IMPORTANT: After 1-2 exchanges on a topic, naturally transition to a completely different area. Don't stay on one topic too long. Cover as many personality dimensions as possible in 10-15 exchanges.

Keep responses conversational, engaging, and focused on getting to know them better. Use emojis naturally and show genuine curiosity about their responses."""
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        message = Message(role, content)
        self.messages.append(message)
        if role == "user":
            self.profile.conversation_count += 1
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.messages.clear()
        self.profile = PersonalityProfile()
        self.conversation_phase = "introduction"
        self.is_first_message = True
    
    def get_conversation_context(self) -> str:
        """Get context about the conversation for personality analysis."""
        if self.profile.conversation_count <= 3:
            return "early_conversation"
        elif self.profile.conversation_count <= 8:
            return "building_connection"
        else:
            return "deep_dive"
    
    async def analyze_personality(self, user_input: str) -> None:
        """Analyze user input for personality insights."""
        analysis_prompt = f"""Analyze this user response for personality insights. Extract key traits and add them to the appropriate categories:

User response: "{user_input}"

Current conversation context: {self.get_conversation_context()}
Conversation count: {self.profile.conversation_count}

Categories to analyze:
- communication_style: How they express themselves (direct, playful, thoughtful, etc.)
- social_preferences: Group vs individual, introvert/extrovert indicators
- values: What they care about, principles, beliefs
- interests: Hobbies, activities, things they enjoy
- lifestyle: Daily routines, living preferences, habits
- relationship_goals: What they want in relationships
- deal_breakers: Things they avoid or dislike

Return ONLY a JSON object like this:
{{
    "communication_style": ["trait1", "trait2"],
    "social_preferences": ["trait1", "trait2"],
    "values": ["value1", "value2"],
    "interests": ["interest1", "interest2"],
    "lifestyle": ["habit1", "habit2"],
    "relationship_goals": ["goal1", "goal2"],
    "deal_breakers": ["dealbreaker1", "dealbreaker2"]
}}

Be specific and insightful. Only return the JSON, no other text."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3,
                max_tokens=400,
            )
            
            analysis = response.choices[0].message.content.strip()
            
            # Try to parse JSON and add insights
            try:
                import json
                insights = json.loads(analysis)
                
                # Add insights to profile
                for category, traits in insights.items():
                    if isinstance(traits, list):
                        for trait in traits:
                            self.profile.add_insight(category, trait)
                    else:
                        self.profile.add_insight(category, str(traits))
                        
            except json.JSONDecodeError:
                # If JSON parsing fails, add raw analysis to insights
                self.profile.add_insight("conversation_insights", analysis)
            
        except Exception:
            # If analysis fails, continue without it
            pass
    
    async def chat(self, user_input: str = None) -> str:
        """Send a message to the AI and get a response."""
        
        # If this is the first message, initiate the conversation
        if self.is_first_message:
            self.is_first_message = False
            initial_message = "Hey there! 👋 I'm so excited to get to know you! What's the most interesting thing that happened to you today?"
            self.add_message("assistant", initial_message)
            return initial_message
        
        # Add user message to history
        if user_input:
            self.add_message("user", user_input)
            # Analyze personality from user input
            await self.analyze_personality(user_input)
        
        # Prepare messages for OpenAI API with system prompt
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend([msg.to_dict() for msg in self.messages])
        
        try:
            # Make API call to OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            # Extract AI response
            ai_response = response.choices[0].message.content
            
            # Add AI response to history
            self.add_message("assistant", ai_response)
            
            return ai_response
            
        except Exception as e:
            error_msg = f"Error communicating with OpenAI: {str(e)}"
            self.add_message("assistant", error_msg)
            return error_msg
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation and personality profile."""
        return {
            "message_count": self.profile.conversation_count,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "conversation_phase": self.conversation_phase,
            "personality_summary": self.profile.get_summary(),
        }
    
    def get_personality_profile(self) -> str:
        """Get the complete personality profile summary."""
        return self.profile.get_summary()


# Alias for backward compatibility
Assistant = DatingAssistant

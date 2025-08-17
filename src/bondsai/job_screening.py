"""Job Screening Assistant for Quant Trading Candidates."""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from .config import config
from server.DeltaTimeRecorder import DeltaTimeRecorder

class JobCandidate:
    """Represents a job candidate with assessment data."""
    
    def __init__(self):
        """Initialize candidate profile."""
        self.name = ""
        self.experience = []
        self.education = []
        self.skills = []
        self.projects = []
        self.conversation_count = 0
        self.conversation_duration = "0h 0m 0s"
        self.conversation_timer = DeltaTimeRecorder()
        
        # Assessment scores
        self.scores = {
            "technical_skills": {
                "quantitative_reasoning": 0,
                "programming": 0,
                "market_knowledge": 0,
                "data_analysis": 0
            },
            "behavioral_traits": {
                "problem_solving": 0,
                "teamwork": 0,
                "initiative": 0,
                "resilience": 0,
                "adaptability": 0
            },
            "cultural_fit": {
                "collaborative_thinking": 0,
                "continuous_learning": 0,
                "challenge_seeking": 0,
                "entrepreneurial_spirit": 0
            },
            "soft_skills": {
                "communication": 0,
                "decision_making": 0,
                "time_management": 0,
                "leadership": 0
            }
        }
        
        # Assessment insights
        self.insights = {
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "cultural_alignment": [],
            "technical_gaps": []
        }
    
    def get_filename(self) -> str:
        """Generate filename for candidate assessment."""
        if self.name:
            name_part = self.name.replace(" ", "_")
        else:
            name_part = "candidate"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{name_part}_assessment_{timestamp}.txt"
    
    def calculate_final_score(self) -> int:
        """Calculate final assessment score out of 100."""
        total_score = 0
        category_weights = {
            "technical_skills": 0.25,
            "behavioral_traits": 0.25,
            "cultural_fit": 0.25,
            "soft_skills": 0.25
        }
        
        for category, weight in category_weights.items():
            category_scores = self.scores[category].values()
            category_avg = sum(category_scores) / len(category_scores)
            total_score += category_avg * weight
        
        return round(total_score)


class JobScreeningAssistant:
    """AI assistant for screening quant trading candidates."""
    
    def __init__(self):
        """Initialize the job screening assistant."""
        self.client = AsyncOpenAI(api_key=config.openai_api_key)
        self.messages: List[Dict[str, str]] = []
        self.model = config.openai_model
        self.temperature = config.openai_temperature
        self.max_tokens = config.openai_max_tokens
        self.candidate = JobCandidate()
        self.is_first_message = True
        self.ready_for_assessment = False
        
        # Job description for quant trading
        self.job_description = """Quantitative Trading Trainee/Intern Position

We are seeking highly motivated candidates for our Quantitative Trading program. This role involves developing and implementing trading strategies, analyzing market data, and working with cutting-edge technology.

Key Requirements:
- Strong quantitative and analytical skills
- Programming experience (Python, C++, etc.)
- Understanding of financial markets and instruments
- Problem-solving and decision-making abilities
- Team collaboration and communication skills
- Continuous learning mindset
- Entrepreneurial spirit and initiative

Our Values:
- Collaborative Thinkers: Best ideas come from teamwork
- Continuous Learners: Always improving and upskilling
- Challenge Seekers: Thrive on complexity and innovation
- Entrepreneurial Spirits: Own your ideas and take initiative"""

        # System prompt for job screening
        self.system_prompt = f"""You are an experienced HR recruiter conducting a comprehensive interview for a Quantitative Trading position. Your role is to:

1. **Be professional but conversational**: Create a comfortable atmosphere while maintaining focus on assessment
2. **Gather comprehensive information**: Learn about their education, experience, projects, and skills
3. **Assess behavioral traits**: Evaluate problem-solving, teamwork, initiative, resilience, and adaptability
4. **Evaluate cultural fit**: Assess alignment with collaborative thinking, continuous learning, challenge-seeking, and entrepreneurial spirit
5. **Technical assessment**: Understand their quantitative skills, programming abilities, and market knowledge
6. **Soft skills evaluation**: Assess communication, decision-making, and leadership potential

**Assessment Areas to Cover:**
- Education background and academic performance
- Relevant work experience and internships
- Technical projects and achievements
- Programming and quantitative skills
- Market knowledge and trading experience
- Problem-solving approaches and examples
- Teamwork and collaboration experiences
- Initiative and leadership examples
- Handling challenges and setbacks
- Career goals and motivation

**Conversation Flow:**
- Start with introduction and background
- Explore education and technical skills
- Discuss relevant experiences and projects
- Assess behavioral traits through examples
- Evaluate cultural alignment and values
- Understand career motivations and goals

**Job Context:**
{self.job_description}

Keep the conversation engaging and professional. Ask follow-up questions to get specific examples and details. After 10-15 exchanges, naturally conclude and generate the assessment report.

Start with: "Hello! I'm conducting interviews for our Quantitative Trading program. Could you tell me a bit about yourself and your background?" """

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.messages.append({"role": role, "content": content})
        if role == "user":
            self.candidate.conversation_count += 1
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.messages.clear()
        self.candidate = JobCandidate()
        self.is_first_message = True
        self.ready_for_assessment = False
    
    async def generate_assessment_report(self) -> str:
        """Generate comprehensive assessment report using AI."""
        try:
            assessment_prompt = f"""Based on this interview conversation, create a detailed candidate assessment for a Quantitative Trading position.

Conversation:
{chr(10).join([f"{msg['role'].upper()}: {msg['content']}" for msg in self.messages])}

Please provide a comprehensive assessment including:

1. **Technical Skills Assessment** (0-100 for each):
   - Quantitative Reasoning
   - Programming Skills
   - Market Knowledge
   - Data Analysis

2. **Behavioral Traits Assessment** (0-100 for each):
   - Problem-solving
   - Teamwork
   - Initiative
   - Resilience
   - Adaptability

3. **Cultural Fit Assessment** (0-100 for each):
   - Collaborative Thinking
   - Continuous Learning
   - Challenge-seeking
   - Entrepreneurial Spirit

4. **Soft Skills Assessment** (0-100 for each):
   - Communication
   - Decision-making
   - Time Management
   - Leadership

5. **Overall Assessment**:
   - Final Score (0-100)
   - Key Strengths
   - Areas for Improvement
   - Cultural Alignment
   - Recommendation (Strong/Moderate/Weak candidate)

Format the response clearly with sections and scores, in the following example format:

### Candidate Assessment for Quantitative Trading Position

#### 1. Technical Skills Assessment
- **Quantitative Reasoning**: (score)
  - (insight)
- **Programming Skills**: (score)
  - Proficient in Python, with experience in libraries like Pandas, NumPy, and scikit-learn, and real-time simulation APIs.
- **Market Knowledge**: (score)
  - (insight)
- **Data Analysis**: (score)
  - (insight)

#### 2. Behavioral Traits Assessment
- **Problem-solving**: (score)
  - (insight)
- **Teamwork**: (score)
  - (insight)
- **Initiative**: (score)
  - (insight)
- **Resilience**: (score)
  - (insight)
- **Adaptability**: (score)
  - (insight)

#### 3. Cultural Fit Assessment
- **Collaborative Thinking**: (score)
  - (insight)
- **Continuous Learning**: (score)
  - (insight)
- **Challenge-seeking**: (score)
  - (insight)
- **Entrepreneurial Spirit**: (score)
  - (insight)

#### 4. Soft Skills Assessment
- **Communication**: (score)
  - (insight)
- **Decision-making**: (score)
  - (insight)
- **Time Management**: (score)
  - (insight)
- **Leadership**: (score)
  - (insight)

#### 5. Overall Assessment
- **Final Score**: (score)
- **Key Strengths**:
  - (insight)
  - (insight)
- **Areas for Improvement**:
  - (insight)
  - (insight)
- **Cultural Alignment**:
  - (insight)
- **Recommendation**: (weak/moderate/strong candidate)
  - (insight)

(Final comment)

"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": assessment_prompt}],
                temperature=0.3,
                max_tokens=1000,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating assessment: {str(e)}"
    
    async def save_assessment_to_file(self) -> str:
        """Save the assessment report to a text file."""
        try:
            # Ensure assessments directory exists
            assessments_dir = "assessments"
            if not os.path.exists(assessments_dir):
                os.makedirs(assessments_dir)
            
            # Generate filename
            filename = self.candidate.get_filename()
            filepath = os.path.join(assessments_dir, filename)
            
            # Generate AI assessment
            ai_assessment = await self.generate_assessment_report()
            
            # Create assessment content
            assessment_content = f"""QUANTITATIVE TRADING CANDIDATE ASSESSMENT
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Interview Length: {self.candidate.conversation_count} exchanges
Conversation Duration: {self.candidate.conversation_duration}

{ai_assessment}

---
Full Interview Transcript:
"""
            
            # Add conversation history
            for i, message in enumerate(self.messages, 1):
                assessment_content += f"\n{i}. {message['role'].upper()}: {message['content']}\n"
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(assessment_content)
            
            return filepath
            
        except Exception as e:
            return f"Error saving assessment: {str(e)}"
    
    async def extract_candidate_name(self) -> None:
        """Extract candidate name from conversation using AI."""
        if self.candidate.name or len(self.messages) < 2:
            return
        
        try:
            # Create a prompt to extract the candidate's name
            name_extraction_prompt = f"""Based on this conversation, what is the candidate's name? 
            
Conversation:
{chr(10).join([f"{msg['role'].upper()}: {msg['content']}" for msg in self.messages[-4:]])}

Please respond with just the candidate's first and last name, or "Unknown" if no name was mentioned.
Examples: "John Smith", "Sarah Johnson", "Unknown" """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": name_extraction_prompt}],
                temperature=0.1,
                max_tokens=50,
            )
            
            extracted_name = response.choices[0].message.content.strip()
            if extracted_name and extracted_name.lower() != "unknown" and len(extracted_name.split()) <= 3:
                self.candidate.name = extracted_name
                
        except Exception as e:
            print(f"Error extracting candidate name: {str(e)}")

    async def chat(self, user_input: str = None) -> str:
        """Send a message to the AI and get a response."""
        
        # Add user message to history
        if user_input:
            self.add_message("user", user_input)
            
            # Try to extract candidate name from early messages
            if self.candidate.conversation_count <= 3:
                await self.extract_candidate_name()
        
        # Check if conversation is ready to end (10-15 exchanges)
        if self.candidate.conversation_count >= 10 and not self.ready_for_assessment:
            self.candidate.conversation_timer.update()
            self.candidate.conversation_duration = self.candidate.conversation_timer.get_delta_str()
            self.ready_for_assessment = True
            # Save assessment to file
            filepath = await self.save_assessment_to_file()
            ending_message = f"Thank you for your time! I've completed your assessment and saved it to: {filepath}\n\nI'll review your responses and get back to you with next steps. Good luck with your application!"
            self.add_message("assistant", ending_message)
            return ending_message
        
        # Check if conversation has gone too long (15+ exchanges) and force end
        if self.candidate.conversation_count >= 15 and not self.ready_for_assessment:
            self.ready_for_assessment = True
            # Save assessment to file
            filepath = await self.save_assessment_to_file()
            ending_message = f"Thank you for your time! I've completed your assessment and saved it to: {filepath}\n\nI'll review your responses and get back to you with next steps. Good luck with your application!"
            self.add_message("assistant", ending_message)
            return ending_message
        
        # Prepare messages for OpenAI API with system prompt
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.messages)
        
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

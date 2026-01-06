"""Student Interview Coach for Early-Career Roles."""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from .config import config
from server.DeltaTimeRecorder import DeltaTimeRecorder
import re

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
        # Sanitize and fallback logic for candidate name
        name = self.name.strip() if self.name else ""
        if name and name.lower() != "unknown":
            # Remove special characters and extra spaces
            name_part = "_".join(
                [
                    "".join(c for c in part if c.isalnum())
                    for part in name.split()
                ]
            )
            if not name_part:
                name_part = "candidate"
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
        
        # Generic early-career context for students
        self.job_description = """Student & Graduate Interview Practice Context

You are helping university students and recent graduates prepare for internships, graduate roles and part-time jobs across fields (e.g. software engineering, data science, consulting, finance, marketing, retail, etc.).

Most students have limited experience. Their main material comes from:
- Coursework and capstone projects
- Group assignments and club/committee roles
- Personal projects and hackathons
- Part-time or casual jobs

Your goal is to help them practise answering behavioural, motivational and basic role-related questions in a way that would make sense to a real recruiter, without pretending to be one.
"""

        # System prompt for student interview coaching
        self.system_prompt = f"""You are a friendly but rigorous early-career interview coach.
You are **not** the real employer and must not promise jobs, but you aim to prepare the student for real interviews.

Your role in each conversation:
1. **Be supportive and clear** – explain what you're asking and why it matters for internships / grad roles.
2. **Gather relevant background** – degree, year level, target field/role, any projects, clubs, or part-time work.
3. **Ask balanced questions** – behavioural (STAR), motivational ("why this role/company"), and light technical/role questions suited to their field.
4. **Teach structure** – gently nudge students toward using STAR (Situation, Task, Action, Result) and concise answers.
5. **Notice common student pitfalls** – rambling, generic answers, no concrete results, underselling impact, not answering the question.
6. **Encourage reflection** – ask what they learned, what they'd change, and how they can improve next time.

**Conversation Flow:**
- Start by asking their name, what they study, which year they are in, and what kind of role they are aiming for.
- Then run a short, realistic practice interview (behavioural + motivational + light role-related) adapted to their background.
- Use follow-up questions to get concrete examples and numbers when possible.
- After 10–15 student responses, start to wrap up and move towards closing the session.

**Assessment & Report:**
At the end of the interview (after 10–15 student messages), you will create a **student-friendly assessment report** that includes:
1. Clear 0–100 scores for several skill areas (technical/role, behavioural, communication, etc.).
2. A short, honest summary of what they did well and where they struggled.
3. 3–7 specific, actionable recommendations for how to improve before the next practice (e.g. \"prepare 3 STAR stories\", \"quantify outcomes\" etc.).
4. A brief, encouraging closing note reminding them this is practice and improvement is expected.

Use warm, encouraging language but stay realistic about their current interview readiness.

**Context:**
{self.job_description}

Start with: "Hi! I'm your interview coach. Could you tell me your name, what you're studying, and what kind of internship or role you're aiming for?" """

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
        """Generate comprehensive assessment report using AI for a student practice session."""
        try:
            assessment_prompt = f"""Based on the following practice interview conversation with a student, create a detailed assessment to help them improve for future real interviews.

Conversation:
{chr(10).join([f"{msg['role'].upper()}: {msg['content']}" for msg in self.messages])}

Assume this is a practice session only. Do **not** pretend to be the real employer and do **not** guarantee any job outcomes.

Please provide a comprehensive assessment including **all** of the following sections and headings so that it can be parsed reliably:

1. **Technical Skills Assessment** (0-100 for each):
   - Quantitative Reasoning (or Analytical Thinking if non-quant role)
   - Programming Skills (or relevant hard skills for their field)
   - Market / Industry Knowledge (adapt to their field)
   - Data Analysis (or Working With Information if non-technical)

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

5. **Student Skill Map & Feedback Loop**:
   - Brief commentary on where they are strongest right now.
   - Brief commentary on their weakest 2–3 areas.
   - 3–7 concrete, student-friendly action items (e.g. practise 3 STAR stories, quantify outcomes, prepare a 60-second intro).

6. **Overall Assessment**:
   - Final Score (0-100) for current interview readiness for their target level.
   - Key Strengths (bullet points).
   - Areas for Improvement (bullet points).
   - Cultural Alignment (bullet points, optional).
   - Recommendation (weak / moderate / strong candidate **for early-career roles**, framed as guidance only).

Format the response clearly with markdown-style headings, following this structure exactly:

### Student Interview Practice Assessment

#### 1. Technical Skills Assessment
- **Quantitative Reasoning**: (score)
  - (insight)
- **Programming Skills**: (score)
  - (insight)
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

#### 5. Student Skill Map & Feedback Loop
- (Write 2–4 short paragraphs or bullets explaining their current skill profile and practice focus areas.)
- (List 3–7 specific action items the student can take before their next practice.)

#### 6. Overall Assessment
- **Final Score**: (score)
- **Key Strengths**:
  - (insight)
- **Areas for Improvement**:
  - (insight)
- **Cultural Alignment**:
  - (insight)
- **Recommendation**: (weak/moderate/strong early-career candidate)
  - (insight)

End with a short, encouraging paragraph emphasising that practice leads to improvement.
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
            assessment_content = f"""STUDENT INTERVIEW PRACTICE ASSESSMENT
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
        """Robustly extract candidate name from the first user message, fallback to OpenAI if needed."""
        name = (self.candidate.name or "").strip()
        user_msgs = [m["content"] for m in self.messages if m["role"] == "user"]
        if (name and name.lower() != "unknown") or not user_msgs:
            return
        first_msg = user_msgs[0].strip()
        extracted_name = None
        # 1. Try common intro patterns (case-insensitive)
        patterns = [
            r"my name is ([A-Za-z][a-zA-Z\-']*(?: [A-Za-z][a-zA-Z\-']*){0,2})",
            r"i am ([A-Za-z][a-zA-Z\-']*(?: [A-Za-z][a-zA-Z\-']*){0,2})",
            r"i'm ([A-Za-z][a-zA-Z\-']*(?: [A-Za-z][a-zA-Z\-']*){0,2})",
            r"this is ([A-Za-z][a-zA-Z\-']*(?: [A-Za-z][a-zA-Z\-']*){0,2})",
            r"it's ([A-Za-z][a-zA-Z\-']*(?: [A-Za-z][a-zA-Z\-']*){0,2})",
            r"([A-Za-z][a-zA-Z\-']* [A-Za-z][a-zA-Z\-']*) here",
        ]
        for pat in patterns:
            match = re.search(pat, first_msg, re.IGNORECASE)
            if match:
                extracted_name = match.group(1).strip()
                print(f"[DEBUG] Name extracted by pattern '{pat}': {extracted_name}")
                break
        # 2. If not found, extract first two alphabetic words (allow single name)
        if not extracted_name:
            words = [w for w in first_msg.split() if w.isalpha() and len(w) > 1]
            if words:
                extracted_name = words[0]
                if len(words) > 1:
                    extracted_name += f" {words[1]}"
                print(f"[DEBUG] Name extracted by first words: {extracted_name}")
        # 3. Fallback to OpenAI
        if not extracted_name:
            try:
                name_extraction_prompt = f"""Based on the following candidate response, what is the candidate's name?\n\nResponse:\n{first_msg}\n\nPlease respond with just the candidate's first and last name, or \"Unknown\" if no name was mentioned.\nExamples: \"John Smith\", \"Sarah Johnson\", \"Unknown\" """
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": name_extraction_prompt}],
                    temperature=0.1,
                    max_tokens=50,
                )
                extracted_name = response.choices[0].message.content.strip()
                print(f"[DEBUG] Name extracted by OpenAI: {extracted_name}")
            except Exception as e:
                print(f"Error extracting candidate name: {str(e)}")
                extracted_name = None
        # Only accept if not unknown, not empty, and 3 words or fewer
        if (
            extracted_name
            and extracted_name.lower() != "unknown"
            and len(extracted_name.split()) <= 3
            and any(c.isalpha() for c in extracted_name)
        ):
            self.candidate.name = extracted_name
            print(f"[DEBUG] Candidate name set: {self.candidate.name}")
        else:
            print(f"[DEBUG] Name extraction failed or result invalid: '{extracted_name}'")

    async def chat(self, user_input: str = None) -> str:
        """Send a message to the AI and get a response."""
        
        # Add user message to history
        if user_input:
            self.add_message("user", user_input)
            
            # Immediately extract candidate name after first user message
            user_msg_count = len([m for m in self.messages if m["role"] == "user"])
            if user_msg_count == 1:
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

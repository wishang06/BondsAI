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

        # System prompt for formal mock interview (not coaching during interview)
        self.system_prompt = f"""You are a professional interviewer conducting a formal mock interview for a student candidate.

**Your Role:**
- Act as a real interviewer would: professional, focused, and evaluative
- Do NOT coach, teach, or give feedback during the interview itself
- Do NOT explain what you're asking or why it matters
- Do NOT give hints or suggestions during the conversation
- Simply ask questions and follow up naturally, just like a real interviewer would

**Interview Style:**
- Be professional and courteous, but maintain interviewer distance
- Ask clear, direct questions without explaining their purpose
- Use follow-up questions to probe deeper when answers are vague
- Keep the conversation focused and efficient
- Do not praise or critique answers during the interview

**Question Types to Ask:**
1. **Opening**: Name, background, what they're studying, what role they're aiming for
2. **Behavioral questions**: Ask for specific examples using STAR framework (but don't mention STAR to them)
3. **Motivational questions**: Why this role/company, career goals, what interests them
4. **Role-related questions**: Light technical or field-specific questions based on their target role
5. **Closing**: Any questions for the interviewer, wrap up professionally

**Conversation Flow:**
- Start with: "Hello, thank you for coming in today. Could you start by telling me a bit about yourself?"
- Conduct a realistic 10-15 question interview
- After 10-15 student responses, naturally conclude: "Thank you for your time today. We'll be in touch with next steps."

**Important:**
- This is a PRACTICE interview, but conduct it exactly like a real one
- Do not mention it's practice during the conversation
- Do not provide coaching or feedback during the interview
- All teaching and feedback will come in the assessment report after the interview

**Context:**
{self.job_description}

Start with: "Hello, thank you for coming in today. Could you start by telling me a bit about yourself?" """

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
            assessment_prompt = f"""You are a supportive interview coach providing detailed feedback to a university student after their practice interview. This was a MOCK INTERVIEW - the student just completed a formal practice session, and now you need to provide comprehensive, student-friendly coaching feedback.

**Important Context:**
- During the interview, you acted as a formal interviewer (no coaching was given)
- Now, provide ALL the teaching, coaching, and guidance in this feedback report
- Be encouraging, specific, and actionable
- Help them understand what worked, what didn't, and how to improve

Conversation from the mock interview:
{chr(10).join([f"{msg['role'].upper()}: {msg['content']}" for msg in self.messages])}

Provide a comprehensive, student-friendly assessment with **all** of the following sections (use exact headings for parsing):

1. **Technical Skills Assessment** (Score 0-100 for each, with detailed 2-3 sentence feedback):
   - Quantitative Reasoning (or Analytical Thinking if non-quant role)
   - Programming Skills (or relevant hard skills for their field)
   - Market / Industry Knowledge (adapt to their field)
   - Data Analysis (or Working With Information if non-technical)
   
   For each skill: Give the score, what they did well, specific gaps you noticed, and concrete steps to improve. Include examples from their answers.

2. **Behavioral Traits Assessment** (Score 0-100 for each, with detailed 2-3 sentence feedback):
   - Problem-solving
   - Teamwork
   - Initiative
   - Resilience
   - Adaptability
   
   For each trait: Give the score, evidence from their answers (quote specific examples), what worked well, what was missing, and concrete ways to strengthen. Teach them how to structure better answers using STAR framework.

3. **Cultural Fit Assessment** (Score 0-100 for each, with detailed 2-3 sentence feedback):
   - Collaborative Thinking
   - Continuous Learning
   - Challenge-seeking
   - Entrepreneurial Spirit
   
   For each: Give the score, how they demonstrated it (or didn't) with examples, and specific ways to better showcase these qualities in future interviews.

4. **Soft Skills Assessment** (Score 0-100 for each, with detailed 2-3 sentence feedback):
   - Communication (clarity, structure, conciseness)
   - Decision-making (how they approach choices)
   - Time Management (organization, prioritization)
   - Leadership (influence, taking charge)
   
   For each: Give the score, specific examples from their answers (what was clear/unclear), and actionable tips for improvement. Include coaching on common student pitfalls like rambling, being too generic, or not quantifying impact.

5. **Overall Assessment**:
   - Final Score (0-100) representing current interview readiness
   - Key Strengths: 3-5 bullet points highlighting what they're doing well, with specific examples from their answers
   - Areas for Improvement: 3-5 bullet points with SPECIFIC weaknesses observed, WHY each matters for real interviews, and HOW to fix it with concrete steps (frame as learning opportunities)
   - Recommended Future Steps: 5-7 specific, actionable practice actions (e.g., "Prepare 3 STAR stories about teamwork - practice saying them out loud", "Practice quantifying outcomes for 2 projects - add numbers and metrics", "Write a 60-second elevator pitch and time yourself", "Practice answering 'Tell me about yourself' in under 2 minutes")
   
   Include a brief coaching section on common student interview mistakes you noticed and how to avoid them.

Format EXACTLY as follows (use these exact markdown headings):

### Student Interview Practice Assessment

#### 1. Technical Skills Assessment
- **Quantitative Reasoning**: (score)
  - (2-3 sentences: what they did well, specific gaps, how to improve)
- **Programming Skills**: (score)
  - (2-3 sentences: what they did well, specific gaps, how to improve)
- **Market Knowledge**: (score)
  - (2-3 sentences: what they did well, specific gaps, how to improve)
- **Data Analysis**: (score)
  - (2-3 sentences: what they did well, specific gaps, how to improve)

#### 2. Behavioral Traits Assessment
- **Problem-solving**: (score)
  - (2-3 sentences: evidence from answers, what worked, what to improve)
- **Teamwork**: (score)
  - (2-3 sentences: evidence from answers, what worked, what to improve)
- **Initiative**: (score)
  - (2-3 sentences: evidence from answers, what worked, what to improve)
- **Resilience**: (score)
  - (2-3 sentences: evidence from answers, what worked, what to improve)
- **Adaptability**: (score)
  - (2-3 sentences: evidence from answers, what worked, what to improve)

#### 3. Cultural Fit Assessment
- **Collaborative Thinking**: (score)
  - (2-3 sentences: how they showed this, how to improve)
- **Continuous Learning**: (score)
  - (2-3 sentences: how they showed this, how to improve)
- **Challenge-seeking**: (score)
  - (2-3 sentences: how they showed this, how to improve)
- **Entrepreneurial Spirit**: (score)
  - (2-3 sentences: how they showed this, how to improve)

#### 4. Soft Skills Assessment
- **Communication**: (score)
  - (2-3 sentences: clarity/structure examples, specific tips to improve)
- **Decision-making**: (score)
  - (2-3 sentences: examples from answers, how to strengthen)
- **Time Management**: (score)
  - (2-3 sentences: examples from answers, how to strengthen)
- **Leadership**: (score)
  - (2-3 sentences: examples from answers, how to strengthen)

#### 5. Overall Assessment
- **Final Score**: (score)
- **Key Strengths**:
  - (bullet point 1)
  - (bullet point 2)
  - (bullet point 3)
- **Areas for Improvement**:
  - (bullet point 1 - specific weakness with why it matters and how to fix)
  - (bullet point 2 - specific weakness with why it matters and how to fix)
  - (bullet point 3 - specific weakness with why it matters and how to fix)
- **Recommended Future Steps**:
  - (actionable step 1)
  - (actionable step 2)
  - (actionable step 3)
  - (actionable step 4)
  - (actionable step 5)

End with 2-3 encouraging sentences emphasizing that:
- This was practice and improvement comes with repetition
- They're building valuable interview skills
- Each practice session makes them more confident and prepared
- They should review this feedback and focus on the recommended steps before their next practice
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

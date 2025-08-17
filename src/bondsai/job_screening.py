"""Job Screening Assistant for Quant Trading Candidates."""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from .config import config


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

QUANTITATIVE TRADING CANDIDATE ASSESSMENT
Generated on: 2025-08-16 15:37:03
Interview Length: 10 exchanges

### Candidate Assessment for Quantitative Trading Position

#### 1. Technical Skills Assessment
- **Quantitative Reasoning**: 85
  - Andy demonstrates a strong foundation in mathematics and statistics, essential for quantitative reasoning.
- **Programming Skills**: 90
  - Proficient in Python, with experience in libraries like Pandas, NumPy, and scikit-learn, and real-time simulation APIs.
- **Market Knowledge**: 70
  - While Andy shows interest in finance and market microstructure, further exposure to market dynamics is needed.
- **Data Analysis**: 88
  - Strong skills in processing and analyzing large datasets, with practical experience in machine learning techniques.

#### 2. Behavioral Traits Assessment
- **Problem-solving**: 90
  - Demonstrates excellent problem-solving skills, employing data-driven decision-making and quick backtesting.
- **Teamwork**: 85
  - Effective communicator and collaborator, with experience in resolving team conflicts through data analysis.
- **Initiative**: 88
  - Proactively engages in competitions, side projects, and continuous learning to enhance skills.
- **Resilience**: 80
  - Shows resilience in adapting strategies and learning from real-time feedback in trading simulations.
- **Adaptability**: 85
  - Comfortable with dynamic environments and quick strategy adjustments, essential for trading.

#### 3. Cultural Fit Assessment
- **Collaborative Thinking**: 90
  - Values teamwork and open communication, fostering a culture of knowledge sharing and collaboration.
- **Continuous Learning**: 95
  - Highly motivated to learn and stay updated with the latest tools and techniques in quantitative trading.
- **Challenge-seeking**: 88
  - Thrives in fast-paced, problem-solving environments, seeking intellectual challenges and immediate feedback.
- **Entrepreneurial Spirit**: 85
  - Demonstrates a proactive mindset and a desire to innovate and contribute to team success.

#### 4. Soft Skills Assessment
- **Communication**: 85
  - Clear and effective communicator, ensuring role clarity and resource accessibility in team settings.
- **Decision-making**: 88
  - Strong decision-making skills, relying on data-driven approaches to resolve conflicts and optimize strategies.
- **Time Management**: 80
  - Manages time effectively through structured daily problem-solving and project involvement.
- **Leadership**: 82
  - Exhibits leadership potential by mentoring peers and fostering a collaborative team environment.

#### 5. Overall Assessment
- **Final Score**: 87
- **Key Strengths**:
  - Strong programming and data analysis skills.
  - Excellent problem-solving and decision-making abilities.
  - High motivation for continuous learning and collaboration.
- **Areas for Improvement**:
  - Further development of market knowledge.
  - Continued exposure to real-world trading scenarios.
- **Cultural Alignment**:
  - Strong alignment with a culture of innovation, collaboration, and continuous improvement.
- **Recommendation**: Strong candidate

Andy Shang demonstrates a strong technical foundation, excellent problem-solving skills, and a proactive approach to learning and collaboration. His enthusiasm for quantitative trading and alignment with the company's values make him a strong candidate for the position. Further exposure to market dynamics will enhance his readiness for real-world trading challenges.

---
Full Interview Transcript:

1. USER: Hi I'm Andy Shang, a first year bachelor's of science student, majoring in Data Science at the University of Melbourne

2. ASSISTANT: Hello Andy, it's great to meet you! Thank you for joining us today. As you're in your first year, you must be gaining a lot of foundational knowledge. Could you share more about your experience so far in your studies? Specifically, what subjects or areas have you found most engaging or challenging?

3. USER: Great to meet you too! I was drawn to data science because it combines my interests in mathematics, statistics, and problem-solving with practical applications that can have real-world impact. From the start of my degree, I’ve enjoyed courses in probability, statistics, and computational modelling, as they give me the tools to analyse complex datasets and extract meaningful insights.  One project I particularly enjoyed involved developing a pipeline to process and summarise large sets of textual data, where I applied Python and machine learning techniques to extract actionable insights. I found it exciting to see theoretical concepts come to life in a practical, results-driven project, and it reinforced my interest in applying data science skills to dynamic, high-stakes environments like quantitative trading.

4. ASSISTANT: That's wonderful to hear, Andy. It sounds like you have a solid foundation and a passion for applying your skills in practical settings. Your project on processing and summarizing textual data with Python and machine learning is quite relevant to quantitative trading, where data-driven insights are crucial.

Could you elaborate on how you approached this project? Specifically, what problem-solving strategies did you employ, and what challenges did you face during the development process?

5. USER: In those competitions, I mainly used **Python** for both strategy development and data analysis, relying on **Pandas**, **NumPy**, and **scikit-learn** for preprocessing, statistical modelling, and backtesting. In the IMC Trading Simulation, I also worked with **real-time simulation APIs** to process live order book data and generate trades with minimal latency.  For continuous learning, I take a structured approach:  * **Daily problem-solving** to sharpen quantitative and coding skills. * **Competitions and side projects** to apply concepts under realistic, time-pressured conditions. * **Ongoing reading and research** on finance, market microstructure, and new ML techniques. * **Peer collaboration** to exchange ideas, debug challenges, and gain new perspectives.  This keeps my skills sharp, adaptable, and aligned with the latest tools and market developments.

6. ASSISTANT: It sounds like you've developed a comprehensive approach to learning and skill enhancement, which is incredibly valuable in the fast-paced world of quantitative trading. Your hands-on experience with Python, real-time simulation APIs, and continuous learning strategies aligns well with what we look for in a candidate.

I'm curious about your teamwork and collaboration experiences. Could you share a situation where you worked with peers on a project or competition? How did you contribute to the team, and what did you learn from that experience?

7. USER: In team settings, I focus on **clear communication, role clarity, and proactive support**. For example, during the IMC Trading Simulation, my team divided responsibilities between data analysis, model development, and strategy implementation. I made sure everyone had access to shared resources and that our code was well-documented, so integration was smooth.  There was one instance where we disagreed on a parameter adjustment that could significantly affect risk exposure. I suggested we run a **quick backtest with both approaches**, review the results together, and then decide based on data rather than intuition. This not only resolved the disagreement but also strengthened our model and reinforced trust within the team. Ultimately, our coordinated efforts and open communication allowed us to deliver a robust strategy that performed consistently throughout the simulation.

8. ASSISTANT: That's a great example of effective teamwork and leadership, Andy. Your approach to conflict resolution through data-driven decision-making is particularly impressive, as it not only enhanced your strategy but also built trust and cohesion within your team. This kind of collaborative spirit is essential in quantitative trading.

Looking towards the future, how do you see your career developing in the field of quantitative trading? What motivates you to pursue this path, and what are your long-term goals?

9. USER: What excites me most about quantitative trading is the combination of **real-time problem-solving, data-driven decision-making, and continuous learning**. Every market scenario is different, and I enjoy designing strategies that can adapt quickly while having a measurable impact.  My long-term goal is to become a trader who can not only develop high-performing strategies but also mentor and collaborate with others to build a strong, innovative team. I see myself contributing by **bringing analytical rigor, coding expertise, and a proactive mindset** to the table, while fostering a culture of knowledge sharing and experimentation. By combining technical skills with teamwork and creativity, I hope to help the firm continuously innovate and stay ahead in dynamic markets.

10. ASSISTANT: Your vision for the future in quantitative trading is quite inspiring, especially your focus on innovation, mentorship, and collaboration. It aligns well with our values of continuous learning and entrepreneurial spirit. Your enthusiasm for data-driven decision-making and strategy development, coupled with your technical skills, positions you well for a successful career in this field.

As we wrap up, is there anything specific you would like to add or any questions you have about the program or the company?

11. USER: My career goal is to become a quantitative trader who can design and refine data-driven strategies that perform in real, fast-moving markets. I’m motivated by the mix of intellectual challenge and immediate feedback — every trade is a live test of your ideas. What excites me most is the combination of deep quantitative analysis, coding, and decision-making under uncertainty, where small improvements can have a big impact. The pace, problem-solving, and constant learning environment are exactly what I thrive in.

12. ASSISTANT: Your motivation and enthusiasm for the field truly shine through, Andy. The dynamic and challenging nature of quantitative trading indeed offers a unique blend of intellectual rigor and real-time impact, which seems to align perfectly with your interests and skills. 

If you have any questions about our Quantitative Trading program or how we operate, feel free to ask. I'm here to provide any information you may need to ensure this is the right fit for your career aspirations.

13. USER: Thank you so much

14. ASSISTANT: You're welcome, Andy! It was a pleasure speaking with you and learning about your background and aspirations. If you have any more questions in the future or need further assistance, don't hesitate to reach out. Best of luck with your studies and your journey into quantitative trading. Have a great day!

15. USER: thanks!

16. ASSISTANT: You're welcome! Take care and best of luck with everything, Andy!

17. USER: you too

18. ASSISTANT: Thank you! Goodbye, Andy!

19. USER: bye!
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

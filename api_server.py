"""Flask API server for BondsAI frontend integration."""

import asyncio
import json
import re
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import glob
from datetime import datetime
import random

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from bondsai.job_screening import JobScreeningAssistant
from server.DeltaTimeRecorder import DeltaTimeRecorder

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Global instances to maintain conversation state
job_assistant = JobScreeningAssistant()
candidate_conversation_timer = DeltaTimeRecorder()

#routing setup for static files
@app.route('/')
def index():
    return app.send_static_file("index.html")

@app.route('/styles.css')
def styles():
    return app.send_static_file("styles.css")

@app.route('/scripts/<path:filename>')
def send_script(filename):
    return app.send_static_file("scripts/" + filename)

@app.route('/styles/<path:filename>')
def send_styles(filename):
    return app.send_static_file("styles/" + filename)

@app.route('/recruiter')
def recruiter():
    return app.send_static_file("recruiter.html")

@app.route('/image/<path:filename>')
def send_icon(filename):
    return app.send_static_file("image/" + filename)

#routing for API endpoints

#Health check endpoint to verify SERVER is running
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "BondsAI API is running"})

#for job screening chat:
# Takes in a candidate message from client and send AI response and candidate profile data to client
@app.route('/api/job/chat', methods=['POST'])
def job_chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Use asyncio to run the async chat method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Get AI response
            ai_response = loop.run_until_complete(job_assistant.chat(user_message))
            
            # Check if conversation is complete (ready for assessment)
            is_complete = job_assistant.ready_for_assessment
            
            # If complete, generate assessment summary
            profile_data = None
            if is_complete:
                profile_data = {
                    "name": job_assistant.candidate.name or "Candidate",
                    "conversation_count": job_assistant.candidate.conversation_count,
                    "assessment_summary": "Assessment completed based on interview"
                }
            
            response = {
                "message": ai_response,
                "isComplete": is_complete,
                "profile": profile_data,
                "conversation_count": job_assistant.candidate.conversation_count
            }
            
            return jsonify(response)
            
        finally:
            loop.close()
            
    except Exception as e:
        print(f"Error in job chat: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# Endpoint to reset job screening conversation
@app.route('/api/job/reset', methods=['POST'])
def reset_job():
    global job_assistant
    job_assistant.clear_history()
    return jsonify({"message": "Job screening conversation reset"})

#Get the initial job screening message
@app.route('/api/job/start', methods=['GET'])
def start_job():
    candidate_conversation_timer.update()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Get the initial message
            initial_message = loop.run_until_complete(job_assistant.chat())
            
            response = {
                "message": initial_message,
                "isComplete": False,
                "profile": None,
                "conversation_count": 0
            }
            
            return jsonify(response)
            
        finally:
            loop.close()
            
    except Exception as e:
        print(f"Error starting job chat: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# Parse an assessment file and extract candidate data
def parse_assessment_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract basic info from filename and content
        filename = os.path.basename(filepath)
        name_match = re.search(r'^(.+?)_assessment_', filename)
        candidate_name = name_match.group(1).replace('_', ' ').title() if name_match else "Anonymous"
        
        # Extract interview date from filename
        date_match = re.search(r'_(\d{8})_\d{6}\.txt$', filename)
        if date_match:
            date_str = date_match.group(1)
            interview_date = datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
        else:
            interview_date = "Unknown"
        
        # Extract conversation count
        conversation_count = 0
        count_match = re.search(r'Interview Length: (\d+) exchanges', content)
        if count_match:
            conversation_count = int(count_match.group(1))

        final_score = 0
        final_score_match = re.search(r'Final Score: (\d+)/100', content.replace('**', ''))
        if final_score_match:
            final_score = int(final_score_match.group(1))

        print(f'final score: {final_score}')
        
        # Initialize default scores
        candidate_data = {
            "name": candidate_name,
            "interview_date": interview_date,
            "conversation_count": conversation_count,
            "final_score": final_score,
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
            },
            "insights": {
                "strengths": [],
                "weaknesses": [],
                "recommendations": []
            },
            "ai_assessment": ""
        }
        
        # Try to extract AI assessment content (everything between the header and transcript)
        assessment_start = content.find("Generated on:")
        transcript_start = content.find("Full Interview Transcript:")
        
        if assessment_start != -1 and transcript_start != -1:
            ai_assessment = content[assessment_start:transcript_start].strip()
            candidate_data["ai_assessment"] = ai_assessment
            
            # Try to extract scores using regex patterns
            # Look for patterns like "Technical Skills Assessment (0-100 for each):"
            # followed by skill names and scores
            
            # Extract final score
            final_score_match = re.search(r'Final Score[:\s]+(\d+)', ai_assessment, re.IGNORECASE)
            if final_score_match:
                candidate_data["final_score"] = int(final_score_match.group(1))
            
            # Extract technical skills scores
            tech_section = re.search(r'Technical Skills.*?(?=Behavioral|Cultural|Soft|Overall|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
            if tech_section:
                tech_text = tech_section.group(0)
                candidate_data["technical_skills"]["quantitative_reasoning"] = extract_score(tech_text, "quantitative")
                candidate_data["technical_skills"]["programming"] = extract_score(tech_text, "programming")
                candidate_data["technical_skills"]["market_knowledge"] = extract_score(tech_text, "market")
                candidate_data["technical_skills"]["data_analysis"] = extract_score(tech_text, "data")
            
            # Extract behavioral traits scores
            behavioral_section = re.search(r'Behavioral.*?(?=Technical|Cultural|Soft|Overall|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
            if behavioral_section:
                behavioral_text = behavioral_section.group(0)
                candidate_data["behavioral_traits"]["problem_solving"] = extract_score(behavioral_text, "problem")
                candidate_data["behavioral_traits"]["teamwork"] = extract_score(behavioral_text, "teamwork")
                candidate_data["behavioral_traits"]["initiative"] = extract_score(behavioral_text, "initiative")
                candidate_data["behavioral_traits"]["resilience"] = extract_score(behavioral_text, "resilience")
                candidate_data["behavioral_traits"]["adaptability"] = extract_score(behavioral_text, "adaptability")
            
            # Extract cultural fit scores
            cultural_section = re.search(r'Cultural.*?(?=Technical|Behavioral|Soft|Overall|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
            if cultural_section:
                cultural_text = cultural_section.group(0)
                candidate_data["cultural_fit"]["collaborative_thinking"] = extract_score(cultural_text, "collaborative")
                candidate_data["cultural_fit"]["continuous_learning"] = extract_score(cultural_text, "learning")
                candidate_data["cultural_fit"]["challenge_seeking"] = extract_score(cultural_text, "challenge")
                candidate_data["cultural_fit"]["entrepreneurial_spirit"] = extract_score(cultural_text, "entrepreneurial")
            
            # Extract soft skills scores
            soft_section = re.search(r'Soft Skills.*?(?=Technical|Behavioral|Cultural|Overall|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
            if soft_section:
                soft_text = soft_section.group(0)
                candidate_data["soft_skills"]["communication"] = extract_score(soft_text, "communication")
                candidate_data["soft_skills"]["decision_making"] = extract_score(soft_text, "decision")
                candidate_data["soft_skills"]["time_management"] = extract_score(soft_text, "time")
                candidate_data["soft_skills"]["leadership"] = extract_score(soft_text, "leadership")
            
            # Extract insights
            strengths_match = re.search(r'(?:Key )?Strengths?[:\s]+(.*?)(?=Areas|Weaknesses|Recommendations|Cultural|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
            if strengths_match:
                strengths_text = strengths_match.group(1)
                candidate_data["insights"]["strengths"] = extract_list_items(strengths_text)
            
            weaknesses_match = re.search(r'(?:Areas for Improvement|Weaknesses?)[:\s]+(.*?)(?=Strengths|Recommendations|Cultural|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
            if weaknesses_match:
                weaknesses_text = weaknesses_match.group(1)
                candidate_data["insights"]["weaknesses"] = extract_list_items(weaknesses_text)
            
            recommendations_match = re.search(r'Recommendations?[:\s]+(.*?)(?=Strengths|Weaknesses|Cultural|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
            if recommendations_match:
                recommendations_text = recommendations_match.group(1)
                candidate_data["insights"]["recommendations"] = extract_list_items(recommendations_text)
        
        return candidate_data
        
    except Exception as e:
        print(f"Error parsing assessment file {filepath}: {str(e)}")
        return None

# Extract a score for a specific skill from text.
def extract_score(text, skill_keyword):
    # Look for patterns like "Programming: 85" or "Programming Skills: 85/100"
    pattern = rf'{skill_keyword}[^:]*:\s*(\d+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    # Look for patterns like "- Programming: 85"
    pattern = rf'-\s*{skill_keyword}[^:]*:\s*(\d+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    return 0

# Extract list items from text (bullet points, numbered lists, etc.).
def extract_list_items(text):
    items = []
    
    # Split by lines and look for list patterns
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Remove common list markers
        line = re.sub(r'^[-*•]\s*', '', line)
        line = re.sub(r'^\d+\.\s*', '', line)
        
        if line and len(line) > 5:  # Only include meaningful items
            items.append(line)
    
    return items[:5]  # Limit to 5 items

# Get all job applicants and their assessment data
@app.route('/api/recruiter/applicants', methods=['GET'])
def get_applicants():
    try:
        assessments_dir = "assessments"
        applicants = []
        
        if not os.path.exists(assessments_dir):
            return jsonify({"applicants": []})
        
        # Get all assessment files
        assessment_files = glob.glob(os.path.join(assessments_dir, "*_assessment_*.txt"))
        
        for filepath in assessment_files:
            candidate_data = parse_assessment_file(filepath)
            if candidate_data:
                applicants.append(candidate_data)
        
        # Sort by interview date (most recent first)
        applicants.sort(key=lambda x: x.get('interview_date', ''), reverse=True)
        
        return jsonify({"applicants": applicants})
        
    except Exception as e:
        print(f"Error getting applicants: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting BondsAI API Server...")
    print("Make sure you have set up your OpenAI API key in the .env file")
    print("Server will be available at http://localhost:8000")
    app.run(debug=True, host='0.0.0.0', port=8000)

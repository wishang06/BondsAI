"""Flask API server for BondsAI frontend integration."""

import asyncio
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sys
import os
import glob
from server.AssessmentFileLoader import parse_assessment_file
from server.ApplicantManager import ApplicantManager

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Global instances to maintain conversation state
applicant_manager = ApplicantManager()

@app.route('/applicant')
def applicant():
    """
    Student-facing practice interview entrypoint.

    For the student odyssey use case we allow repeated practice sessions,
    so we always (re)start a conversation for this IP and send them to the
    applicant (student) chat UI.
    """
    applicant_manager.start_conversation(request.remote_addr)
    return app.send_static_file('applicant.html')

@app.route('/applicant/chat', methods=['POST'])
def applicant_chat():
    try:
        applicant_job_assistant = applicant_manager.get_job_assistant(request.remote_addr)
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Get AI response
            ai_response = loop.run_until_complete(applicant_job_assistant.chat(user_message))
            
            # Check if conversation is complete (ready for assessment)
            is_complete = applicant_job_assistant.ready_for_assessment
            
            # If complete, generate assessment summary
            profile_data = None
            if is_complete:
                applicant_manager.stop_conversation_timer(request.remote_addr)
                conversation_duration = applicant_manager.get_conversation_duration(request.remote_addr)
                profile_data = {
                    "name": applicant_job_assistant.candidate.name or "Candidate",
                    "conversation_count": applicant_job_assistant.candidate.conversation_count,
                    "conversation_duration": conversation_duration,
                    "assessment_summary": "Assessment completed based on interview"
                }
            
            response = {
                "message": ai_response,
                "isComplete": is_complete,
                "profile": profile_data,
                "conversation_count": applicant_job_assistant.candidate.conversation_count
            }
            
            return jsonify(response)
            
        finally:
            loop.close()

    except Exception as e:
        print(f"Error in job chat: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/applicant/end', methods=['POST'])
def end_applicant_conversation():
    try:
        applicant_manager.end_conversation(request.remote_addr)
        return jsonify({"message": "Conversation ended successfully"})
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 403

@app.route('/scripts/<path:filename>')
def send_script(filename):
    return app.send_static_file("scripts/" + filename)

@app.route('/styles/<path:filename>')
def send_styles(filename):
    return app.send_static_file("styles/" + filename)

@app.route('/recruiter')
def recruiter():
    return app.send_static_file("recruiter.html")

@app.route('/journey')
def journey():
    """Student long-term growth / journey view."""
    return app.send_static_file("journey.html")

@app.route('/image/<path:filename>')
def send_icon(filename):
    return app.send_static_file("image/" + filename)

#Health check endpoint to verify SERVER is running
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "BondsAI API is running"})

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
                # Add filepath for later retrieval
                candidate_data['filepath'] = filepath
                applicants.append(candidate_data)
        
        # Sort by interview date (ascending for journey progression)
        applicants.sort(key=lambda x: x.get('interview_date', ''))
        
        # Limit to 5 most recent sessions
        applicants = applicants[-5:]
        
        return jsonify({"applicants": applicants})
        
    except Exception as e:
        print(f"Error getting applicants: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/assessment/raw/<path:filename>', methods=['GET'])
def get_raw_assessment(filename):
    """Get raw assessment text for parsing detailed feedback."""
    try:
        from server.AssessmentFileLoader import get_raw_assessment_text
        import urllib.parse
        
        # Decode filename
        decoded_filename = urllib.parse.unquote(filename)
        filepath = os.path.join("assessments", decoded_filename)
        
        if not os.path.exists(filepath):
            return jsonify({"error": "Assessment file not found"}), 404
        
        raw_text = get_raw_assessment_text(filepath)
        return jsonify({"assessment_text": raw_text})
        
    except Exception as e:
        print(f"Error getting raw assessment: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.errorhandler(404)
def page_not_found(e):
    return app.send_static_file('404.html'), 404

if __name__ == '__main__':
    print("Starting BondsAI API Server...")
    print("Make sure you have set up your OpenAI API key in the .env file")
    print("Server will be available at http://localhost:8000")
    app.run(debug=True, host='0.0.0.0', port=8000)

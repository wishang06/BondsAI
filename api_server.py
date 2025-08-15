"""Flask API server for BondsAI frontend integration."""

import asyncio
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from bondsai.core import DatingAssistant
from bondsai.job_screening import JobScreeningAssistant

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Global instances to maintain conversation state
dating_assistant = DatingAssistant()
job_assistant = JobScreeningAssistant()

@app.route('/')
def index():
    return app.send_static_file("index.html")

@app.route('/styles.css')
def styles():
    return app.send_static_file("styles.css")

@app.route('/script.js')
def script():
    return app.send_static_file("script.js")

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file("favicon.ico")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "BondsAI API is running"})

@app.route('/api/dating/chat', methods=['POST'])
def dating_chat():
    """Handle dating chat messages."""
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
            ai_response = loop.run_until_complete(dating_assistant.chat(user_message))
            # Check if conversation is complete (ready for summary)
            is_complete = dating_assistant.ready_for_summary
            
            # If complete, generate profile summary
            profile_data = None
            if is_complete:

                # Extract profile information from the conversation
                profile_data = {
                    "name": dating_assistant.profile.name or "User",
                    "age": dating_assistant.profile.age or "Not specified",
                    "gender": dating_assistant.profile.gender or "Not specified",
                    "sexual_orientation": dating_assistant.profile.sexual_orientation or "Not specified",
                    "conversation_count": dating_assistant.profile.conversation_count,
                    "personality_summary": dating_assistant.profile_content
                }
            
            response = {
                "message": ai_response,
                "isComplete": is_complete,
                "profile": profile_data,
                "conversation_count": dating_assistant.profile.conversation_count
            }
            
            return jsonify(response)
            
        finally:
            loop.close()
            
    except Exception as e:
        print(f"Error in dating chat: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/job/chat', methods=['POST'])
def job_chat():
    """Handle job screening chat messages."""
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

@app.route('/api/dating/reset', methods=['POST'])
def reset_dating():
    """Reset dating conversation."""
    global dating_assistant
    dating_assistant.clear_history()
    return jsonify({"message": "Dating conversation reset"})

@app.route('/api/job/reset', methods=['POST'])
def reset_job():
    """Reset job screening conversation."""
    global job_assistant
    job_assistant.clear_history()
    return jsonify({"message": "Job screening conversation reset"})

@app.route('/api/dating/start', methods=['GET'])
def start_dating():
    """Get the initial dating message."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Get the initial message
            initial_message = loop.run_until_complete(dating_assistant.chat())
            
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
        print(f"Error starting dating chat: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/job/start', methods=['GET'])
def start_job():
    """Get the initial job screening message."""
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

if __name__ == '__main__':
    print("Starting BondsAI API Server...")
    print("Make sure you have set up your OpenAI API key in the .env file")
    print("Server will be available at http://localhost:8000")
    app.run(debug=True, host='0.0.0.0', port=8000)

class BondsAI {
    constructor() {
        this.currentSection = 'logo';
        this.datingMessages = [];
        this.jobMessages = [];
        this.isTyping = false;
        
        // API endpoints
        this.API_BASE = window.location.origin;
        
        this.init();
    }

    init() {
        this.setupScrollBehavior();
        this.setupChatHandlers();
        this.setupKeyboardHandlers();
        this.loadInitialMessages();
        
        // Set initial scroll position to logo section
        document.getElementById('logo-section').scrollIntoView();
    }

    loadInitialMessages() {
        // Use static initial messages - don't make API calls on page load
        // The initial messages are already in the HTML, so we don't need to add them here
        // This prevents automatic responses before user interaction
    }

    clearMessages(type) {
        const messagesContainer = document.getElementById(`${type}-messages`);
        messagesContainer.innerHTML = '';
        if (type === 'dating') {
            this.datingMessages = [];
        } else {
            this.jobMessages = [];
        }
    }

    setupScrollBehavior() {
        // Handle scroll events to determine current section
        window.addEventListener('scroll', () => {
            const sections = ['logo-section', 'job-section'];
            const scrollPosition = window.scrollY;
            const windowHeight = window.innerHeight;
            
            // Determine which section is currently visible
            sections.forEach((sectionId, index) => {
                const section = document.getElementById(sectionId);
                const sectionTop = section.offsetTop;
                const sectionBottom = sectionTop + section.offsetHeight;
                
                if (scrollPosition >= sectionTop - windowHeight/2 && 
                    scrollPosition < sectionBottom - windowHeight/2) {
                    this.currentSection = sectionId.replace('-section', '');
                }
            });
        });

        // Smooth scroll to sections
        this.setupSmoothScrolling();
    }

    setupSmoothScrolling() {
        // Add scroll snap behavior
        const sections = document.querySelectorAll('.chat-section, .logo-section');
        
        // Optional: Add wheel event listener for more controlled scrolling
        let isScrolling = false;
        let isRescrolling = false;
        
        window.addEventListener('wheel', (e) => {
            if (isScrolling) return;
            
            const delta = e.deltaY;
            const currentSection = document.querySelector(`#${this.currentSection}-section`);
            
            if (Math.abs(delta) > 10) { // Threshold for intentional scroll
                isScrolling = true;
                
                //scroll down to job-section, scroll up to logo-section
                if (delta > 0)
                    document.getElementById('job-section').scrollIntoView({ behavior: 'smooth' });
                else
                    document.getElementById('logo-section').scrollIntoView({ behavior: 'smooth' });
    
                
                setTimeout(() => {
                    isScrolling = false;
                }, 1000);
            }
            else {
                const initialSection = this.currentSection;
                if (!isRescrolling)
                {
                    isRescrolling = true;
                    setTimeout(() => {
                        if (isScrolling)
                        {
                            isRescrolling = false;
                            return;
                        }
                        if (initialSection !== this.currentSection)
                        {
                            isRescrolling = false;
                            return;
                        }

                        currentSection.scrollIntoView({ behavior: 'smooth' });
                        isRescrolling = false;
                    }, 100);
                }
                
            }
        }, { passive: true });
    }

    setupChatHandlers() {
        // Job chat handlers
        const jobInput = document.getElementById('job-input');
        const jobSend = document.getElementById('job-send');
        
        jobSend.addEventListener('click', () => {
            this.sendMessage('job', jobInput.value);
        });
    }

    setupKeyboardHandlers() {

        document.getElementById('job-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage('job', e.target.value);
            }
        });
    }

    async sendMessage(type, message) {
        if (!message.trim() || this.isTyping) return;

        const input = document.getElementById(`${type}-input`);
        const messagesContainer = document.getElementById(`${type}-messages`);
        
        // Clear input
        input.value = '';
        
        // Add user message to UI
        this.addMessageToUI(type, message, 'user');
        
        // Show typing indicator
        this.showTypingIndicator(type);
        
        try {
            // Send message to backend
            const response = await this.callAPI(type, message);
            
            // Hide typing indicator
            this.hideTypingIndicator(type);
            
            // Add AI response to UI
            this.addMessageToUI(type, response.message, 'ai');
            
            // Check if conversation is complete and show profile with a one second delay
            if (response.isComplete && response.profile) {
                setTimeout(() => {
                    this.showProfile(type, response.profile);
                }, 1000);
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator(type);
            this.addMessageToUI(type, 'Sorry, I encountered an error connecting to the server. Please make sure the backend is running and try again.', 'ai');
        }
    }

    async callAPI(type, message) {
        const endpoint = type === 'dating' ? '/api/dating/chat' : '/api/job/chat';
        const response = await fetch(`${this.API_BASE}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || 'Network response was not ok');
        }
        
        return await response.json();
    }

    addMessageToUI(type, message, sender) {
        const messagesContainer = document.getElementById(`${type}-messages`);
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = `message-bubble ${type === 'dating' ? 'pink' : 'blue'}`;
        
        if (sender === 'user') {
            bubbleDiv.className = 'message-bubble';
        }
        
        bubbleDiv.textContent = message;
        messageDiv.appendChild(bubbleDiv);
        messagesContainer.appendChild(messageDiv);
        
        // Store message
        if (type === 'dating') {
            this.datingMessages.push({ sender, message });
        } else {
            this.jobMessages.push({ sender, message });
        }
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showTypingIndicator(type) {
        this.isTyping = true;
        const typingIndicator = document.getElementById(`${type}-typing`);
        typingIndicator.style.display = 'flex';
        
        // Scroll to show typing indicator
        const messagesContainer = document.getElementById(`${type}-messages`);
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    }

    hideTypingIndicator(type) {
        this.isTyping = false;
        const typingIndicator = document.getElementById(`${type}-typing`);
        typingIndicator.style.display = 'none';
    }

    showProfile(type, profileData) {
        const profileDisplay = document.getElementById(`${type}-profile`);
        const profileContent = document.getElementById(`${type}-profile-content`);
        
        let profileHTML = '';
        
        profileHTML = `
            <div class="profile-section">
                <strong>Candidate:</strong> ${profileData.name}
            </div>
            <div class="profile-section">
                <strong>Assessment Summary:</strong><br>
                ${profileData.assessment_summary}
            </div>
            <div class="profile-section">
                <strong>Interview Length:</strong> ${profileData.conversation_count} exchanges
            </div>
        `;
    
        
        profileContent.innerHTML = profileHTML;
        profileDisplay.style.display = 'block';
        
        // Add click handler to close profile
        const closeHandler = (e) => {
            if (e.target === profileDisplay) {
                profileDisplay.style.display = 'none';
                profileDisplay.removeEventListener('click', closeHandler);
            }
        };
        profileDisplay.addEventListener('click', closeHandler);
    }

    // Utility method to reset conversations
    async resetConversation(type) {
        try {
            const response = await fetch(`${this.API_BASE}/api/${type}/reset`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                this.clearMessages(type);
                // Reload initial message
                if (type === 'dating') {
                    const startResponse = await fetch(`${this.API_BASE}/api/dating/start`);
                    if (startResponse.ok) {
                        const data = await startResponse.json();
                        this.addMessageToUI('dating', data.message, 'ai');
                    }
                } else {
                    const startResponse = await fetch(`${this.API_BASE}/api/job/start`);
                    if (startResponse.ok) {
                        const data = await startResponse.json();
                        this.addMessageToUI('job', data.message, 'ai');
                    }
                }
            }
        } catch (error) {
            console.error('Error resetting conversation:', error);
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new BondsAI();
    
    // Make app globally available for debugging
    window.bondsAI = app;
    
    // Add reset buttons for development (optional)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('Development mode: Use bondsAI.resetConversation("dating") or bondsAI.resetConversation("job") to reset conversations');
    }
});

// Add some additional CSS for profile sections
const additionalStyles = `
    .profile-section {
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(0,0,0,0.1);
    }
    
    .profile-section:last-child {
        border-bottom: none;
        margin-bottom: 0;
    }
    
    .profile-section ul {
        margin: 8px 0 0 20px;
        padding: 0;
    }
    
    .profile-section li {
        margin: 4px 0;
        font-size: 0.9rem;
    }
    
    .profile-section strong {
        color: #e91e63;
    }
    
    .blue-card .profile-section strong {
        color: #3b82f6;
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

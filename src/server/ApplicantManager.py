from bondsai.job_screening import JobScreeningAssistant

# This class manages applicant by their ip address to ensure they can only apply once
# Each applicant is represented by their ip, which they can have three states: 'applied' 'not applied' or 'applying'
# Once an applicant requests the application page, they are set to 'applying' which allows them to request to communicate with the AI
# Once they submit their application, they are set to 'applied' which prevents them from applying again
class ApplicantManager:
    def __init__(self):
        self.applicant_state = {}
        self.applicant_job_assistant = {}
    
    # Return the status of the applicant based on their IP address
    def get_applicant_status(self, ip_address):
        return self.applicant_state.get(ip_address, 'not applied')
    
    # Set the status of the applicant based on their IP address
    def set_applicant_status(self, ip_address, status):
        if status not in ['applied', 'not applied', 'applying']:
            raise ValueError("Status must be either 'applied', 'not applied' or 'applying'")
        
        self.applicant_state[ip_address] = status

    # Start a conversation with the applicant by creating a JobScreeningAssistant instance
    def start_conversation(self, ip_address):
        if self.get_applicant_status(ip_address) != 'not applied':
            raise ValueError(f"Applicant {ip_address} has already applied or is currently applying.")
        
        self.set_applicant_status(ip_address, 'applying')
        self.applicant_job_assistant[ip_address] = JobScreeningAssistant()

    # End the conversation for the applicant by removing their JobScreeningAssistant instance
    def end_conversation(self, ip_address):
        if self.get_applicant_status(ip_address) != 'applying':
            print(f"Applicant {ip_address} is not in conversation.")
            return
        
        self.set_applicant_status(ip_address, 'applied')
        del self.applicant_job_assistant[ip_address]

    # Get the JobScreeningAssistant instance for the applicant
    def get_job_assistant(self, ip_address):
        if self.get_applicant_status(ip_address) != 'applying':
            raise ValueError(f"Applicant {ip_address} is not currently applying.") 
        
        return self.applicant_job_assistant[ip_address]
        


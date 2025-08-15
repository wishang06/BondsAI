from datetime import datetime

class DeltaTimeRecorder:
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = self.start_time

    def update(self):
        # Update the end time to the current time
        self.start_time = self.end_time
        self.end_time = datetime.now()

    def get_delta(self):
        # Return the time difference between start and end
        delta = self.end_time - self.start_time
        return delta
    
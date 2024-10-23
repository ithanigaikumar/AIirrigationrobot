# AI Irrigation Robot Using WatsonX

This application utilizes the WatsonX platform to control an AI-powered irrigation robot.

## Prerequisites

Before you start, ensure you have the `ibm_cloud_sdk_core` downloaded.

## Installation

To set up the project, follow these steps:

1. **Set up a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

2. **Install the required libraries:**
    ```bash
    pip install -r requirements.txt

3. **Install docker and make sure it is running**

4. **Run the application:**
    ```bash
    docker build -t ai-irrigation-chatbot . 
    docker run -p 8080:80 ai-irrigation-chatbot


5. **Navigate to http://localhost:8080/**
   Hover near the right-hand bottom corner for the chatbot, and type in update to get update. 

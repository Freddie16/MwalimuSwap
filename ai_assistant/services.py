# ai_assistant/services.py

import google.generativeai as genai
from decouple import config
import json
import logging

logger = logging.getLogger(__name__)

# Configure the Gemini API key from environment variables
# Ensure GOOGLE_API_KEY is set in your .env file
GEMINI_API_KEY = config('GOOGLE_API_KEY', default='')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GOOGLE_API_KEY not found in .env. Gemini API interactions will not work.")

def get_gemini_chat_response(prompt, chat_history=None):
    """
    Interacts with the Gemini Pro model to get a chat response.
    Args:
        prompt (str): The user's current message.
        chat_history (list, optional): A list of previous messages in the format
                                      [{'role': 'user'/'model', 'parts': [{'text': 'message'}]}]
                                      Defaults to None.
    Returns:
        str: The AI's response message.
    """
    if not GEMINI_API_KEY:
        return "AI assistant is not configured. Please set GOOGLE_API_KEY in your .env file."

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Initialize chat session
        chat = model.start_chat(history=chat_history if chat_history is not None else [])
        
        response = chat.send_message(prompt)
        
        # Extract text from the response
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            return response.candidates[0].content.parts[0].text
        else:
            logger.warning(f"Gemini API returned an unexpected response structure: {response}")
            return "I'm sorry, I couldn't generate a response. Please try again."
    except Exception as e:
        logger.error(f"Error calling Gemini API for chat: {e}")
        return "I'm currently unable to process your request. Please try again later."

def get_smart_match_suggestions(user_profile_data, existing_swap_requests):
    """
    Uses Gemini to generate smart matching suggestions based on user profile and
    existing swap requests.
    Args:
        user_profile_data (dict): Dictionary containing user's profile information
                                  (e.g., current location, subjects, school type, desired swap location).
        existing_swap_requests (list): List of dictionaries, each representing an existing
                                       swap request from other users.
    Returns:
        list: A list of dictionaries, where each dictionary represents a suggested match.
              Returns an empty list if no suggestions or an error occurs.
    """
    if not GEMINI_API_KEY:
        return []

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')

        # Craft a detailed prompt for the AI
        prompt = f"""
        You are an AI assistant for MwalimuSwap, a platform for teachers to swap schools.
        Your task is to identify potential swap opportunities for a given teacher based on their profile
        and a list of existing swap requests from other teachers.

        Here is the requesting teacher's profile:
        {json.dumps(user_profile_data, indent=2)}

        Here are existing swap requests from other teachers:
        {json.dumps(existing_swap_requests, indent=2)}

        Analyze the data and suggest potential swap matches. A good match means:
        1. The other teacher's CURRENT location is close to the requesting teacher's DESIRED swap location.
        2. The other teacher's DESIRED swap location is close to the requesting teacher's CURRENT location.
        3. Consider subject expertise and school type compatibility (if available in profiles/requests).

        Provide your suggestions as a JSON array of objects. Each object should have:
        - "match_id": A unique identifier for the suggested match (e.g., the ID of the other swap request).
        - "other_teacher_username": The username of the other teacher.
        - "other_teacher_current_location": The current county, subcounty, and ward of the other teacher.
        - "other_teacher_desired_location": The desired county, subcounty, and ward of the other teacher.
        - "compatibility_score": A score (0-100) indicating how good the match is.
        - "reason": A brief explanation of why this is a good match.
        - "suggested_action": What the requesting teacher can do next (e.g., "View Profile", "Initiate Contact").

        If no good matches are found, return an empty JSON array [].
        Example of a single match object:
        {{
            "match_id": 123,
            "other_teacher_username": "teacher_B",
            "other_teacher_current_location": "Nairobi, Westlands, Kileleshwa",
            "other_teacher_desired_location": "Mombasa, Changamwe, Port Reitz",
            "compatibility_score": 90,
            "reason": "Teacher B's current location matches your desired location, and their desired location is close to your current school.",
            "suggested_action": "View Teacher B's Profile"
        }}
        """

        # Use gemini-2.0-flash for structured output
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            json_text = response.candidates[0].content.parts[0].text
            try:
                suggestions = json.loads(json_text)
                return suggestions
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response from Gemini: {e}\nResponse: {json_text}")
                return []
        else:
            logger.warning(f"Gemini API returned an unexpected response structure for smart match: {response}")
            return []
    except Exception as e:
        logger.error(f"Error calling Gemini API for smart match: {e}")
        return []
def get_smart_match_summary(user_profile_data, existing_swap_requests):
    """
    Uses Gemini to generate a summary of potential swap matches based on user profile and
    existing swap requests.
    Args:
        user_profile_data (dict): Dictionary containing user's profile information
                                  (e.g., current location, subjects, school type, desired swap location).
        existing_swap_requests (list): List of dictionaries, each representing an existing
                                       swap request from other users.
    Returns:
        str: A summary of potential matches or an error message if something goes wrong.
    """
    if not GEMINI_API_KEY:
        return "AI assistant is not configured. Please set GOOGLE_API_KEY in your .env file."
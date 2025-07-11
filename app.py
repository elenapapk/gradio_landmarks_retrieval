import gradio as gr
import openai
import requests
import json
import os
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from IPython.display import display
import requests.exceptions



# Print all environment variables
print("=== DEBUG: Checking Available Environment Variables ===")
print(list(os.environ.keys()))  # This will print all available environment variable names

# Check if API keys are loaded
print("GOOGLE_PLACES_API_KEY:", os.getenv("GOOGLE_PLACES_API_KEY"))
print("GOOGLE_CSE_API_KEY:", os.getenv("GOOGLE_CSE_API_KEY"))
print("GOOGLE_CSE_ID:", os.getenv("GOOGLE_CSE_ID"))
print("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))


# Retrieve API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
google_places_api_key = os.getenv("GOOGLE_PLACES_API_KEY")
google_cse_api_key = os.getenv("GOOGLE_CSE_API_KEY")
google_cse_id = os.getenv("GOOGLE_CSE_ID")





# 1️⃣ Function to Determine Strategy Using ChatGPT API
def determine_strategy_and_fetch_images(user_prompt):
    print(f"DEBUG: User input received -> {user_prompt}")  # ✅ Debugging print

    """
    Uses OpenAI's ChatGPT API to classify the user prompt into one of two strategies:
    - STRATEGY A: If the user prompt is a city name, it extracts the city and calls
      get_landmarks_by_city(city) to fetch images of 10 famous landmarks from that city.
    - STRATEGY B: If the user prompt is a descriptive landmark query, it extracts the description and calls
      get_landmarks_by_description(description) to fetch images that resemble the provided description.
    The function sends a prompt to ChatGPT with instructions to return a JSON response formatted as follows:
    For a city:
      {
        "strategy": "A",
        "city": "<extracted_city_name>"
      }
    For a description:
      {
        "strategy": "B",
        "description": "<extracted_description>"
      }
    No extra text should be included in the response.
    """
    # Construct the prompt for ChatGPT with clear instructions.
    chat_prompt = f"""
    You are an assistant that helps determine the strategy for fetching landmark images.
    Given the following user prompt: "{user_prompt}",
    please analyze the prompt and decide if the user is referring to a city name (STRATEGY A) or a descriptive query (STRATEGY B).
    If it is a city name, respond with JSON formatted as:
    {{
        "strategy": "A",
        "city": "<extracted_city_name>"
    }}
    If it is a descriptive query, respond with JSON formatted as:
    {{
        "strategy": "B",
        "description": "<extracted_description>"
    }}
    Do not include any additional text in your response.
    """

    try:
        # Call the ChatGPT API with our system and user messages.
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # Use your preferred model
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that classifies user prompts into strategies for fetching landmark images."
                },
                {"role": "user", "content": chat_prompt}
            ]
        )

        # Parse the response from ChatGPT to extract the JSON data.
        strategy_data = json.loads(response["choices"][0]["message"]["content"])
        print(f"DEBUG: ChatGPT response -> {strategy_data}")  # ✅ Debugging print

        # Based on the classified strategy, call the corresponding function.
        if strategy_data["strategy"] == "A":
            print(f"DEBUG: Fetching landmarks for city -> {strategy_data['city']}")  # ✅ Debugging print
            return get_landmarks_by_city(strategy_data["city"])  # Strategy A

        elif strategy_data["strategy"] == "B":
            print(f"DEBUG: Fetching images for description -> {strategy_data['description']}")  # ✅ Debugging print
            return get_landmarks_by_description(strategy_data["description"])  # Strategy B

        else:
            print("DEBUG: ChatGPT returned an invalid strategy.")  # ✅ Debugging print
            return ["Unable to determine strategy. Please try a different prompt."]

    except Exception as e:
        print(f"ERROR: {e}")  # ✅ Debugging print for errors
        return ["An error occurred while processing your request."]


    



   # 2️⃣ Strategy A: Get Landmark Images by City (Google Places API)
def get_landmarks_by_city(city):
    """Fetches top 10 famous landmarks for a given city using Google Places API."""
    GOOGLE_PLACES_SEARCH_ENDPOINT = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"famous landmarks in {city}",
        "key": google_places_api_key  
    }

    print(f"DEBUG: Requesting Google Places API for city -> {city}")  # ✅ Debugging print

    try:
        response = requests.get(GOOGLE_PLACES_SEARCH_ENDPOINT, params=params)
        response.raise_for_status()  # ✅ Raise error for bad responses
        data = response.json()
        print(f"DEBUG: Google API Response -> {data}")  # ✅ Debugging print

        if "error_message" in data:
            print(f"ERROR: Google Places API Error -> {data['error_message']}")  # ✅ Debugging print
            return [f"Google API Error: {data['error_message']}"]

        if "results" in data:
            results = data["results"][:10]
            image_links = []

            for landmark in results:
                if "photos" in landmark:
                    photo_reference = landmark["photos"][0]["photo_reference"]
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_reference}&key={google_places_api_key}"
                    image_links.append(photo_url)

            return image_links if image_links else ["No results found for this city."]
        
        return ["No results found."]
    
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to get landmarks - {e}")  # ✅ Debugging print
        return [f"Failed to retrieve landmarks. Error: {e}"]


# Test function call
result_1 = get_landmarks_by_city("Tokyo")




for img in result_1:
    display(img)



   # 2️⃣ Strategy B:
def get_landmarks_by_description(description):
    """Fetches images that match a given description using Google Custom Search API."""
    GOOGLE_CSE_SEARCH_ENDPOINT = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": description,
        "cx": google_cse_id,
        "searchType": "image",
        "num": 10,
        "key": google_cse_api_key
    }

    print(f"DEBUG: Requesting Google Custom Search API for -> {description}")  # ✅ Debugging print

    try:
        response = requests.get(GOOGLE_CSE_SEARCH_ENDPOINT, params=params)
        response.raise_for_status()  # ✅ Raise error for bad responses
        results = response.json()
        print(f"DEBUG: Google CSE API Response -> {results}")  # ✅ Debugging print

        if "error_message" in results:
            print(f"ERROR: Google CSE API Error -> {results['error_message']}")  # ✅ Debugging print
            return [f"Google CSE API Error: {results['error_message']}"]

        if "items" in results:
            image_links = [item["link"] for item in results["items"]]
            return image_links if image_links else ["No images found."]
        
        return ["No matching images found."]
    
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to get images - {e}")  # ✅ Debugging print
        return [f"Failed to retrieve images. Error: {e}"]


result_2 = get_landmarks_by_description("castle")




for img in result_2:
    display(img)




# 5️⃣ Gradio UI

# Ensure the function returns a list of image URLs
def gradio_interface(user_prompt):
    results = determine_strategy_and_fetch_images(user_prompt)

    if isinstance(results, list) and len(results) > 0:
        return results  # Return plain list of URLs 

    return ["No images found."]

# Use `Blocks` for a more interactive layout
with gr.Blocks() as demo:
    gr.Markdown("## 🏛️ Landmark Image Finder")
    gr.Markdown("Enter a city name or describe a landmark to get relevant images.")

    user_input = gr.Textbox(label="Enter a city or landmark description")
    submit_button = gr.Button("Find Images")
    output_gallery = gr.Gallery(label="Images")

    submit_button.click(gradio_interface, inputs=user_input, outputs=output_gallery)

#Remove `ssr=False`
demo.launch(debug=True, share=True) 

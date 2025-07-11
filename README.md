Gradio Landmark Retrieval App

This repository contains a Gradio-based web application for retrieving landmark images either by city name or descriptive prompt. The app uses the OpenAI GPT model to classify input and Google APIs to fetch relevant landmark images.

Team

Elena Papakosta
Ramy Anka
Nouhaila Elmalouli

Files

- **`app.py`**  
  The main Python script that runs the Gradio app. It:
  - Determines user intent using OpenAI's GPT (city name vs. description)
  - Fetches images from:
    - Google Places API (for cities)
    - Google Custom Search API (for descriptions)
  - Displays results in an interactive Gradio gallery.

- **`requirements.txt`**  
  Contains the list of Python dependencies to run the app:
  - `gradio`
  - `openai`
  - `requests`
  - `python-dotenv`
  - `Pillow`

How to Run

1. Clone the Repository

```bash
git clone https://github.com/elenapapk/gradio_landmarks_retrieval.git
cd gradio_landmarks_retrieval

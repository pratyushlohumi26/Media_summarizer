# Media_summarizer
Takes input as a mp3/mp4 file and summarize it using whisper and gpt.

# Audio and Video Processing Flask App

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Flask-2.1.1-green)
![OpenAI](https://img.shields.io/badge/OpenAI-API-orange)
![Whisper](https://img.shields.io/badge/Whisper-API-yellow)

A Flask web application that allows users to upload audio (MP3) and video (MP4) files for processing. It supports the following features:

- Chunking of audio/video files into 15-minute segments.
- Transcription of audio segments using the Whisper API.
- Summarization of transcribed text using the GPT-3.5-turbo API.
- Display of both individual chunk summaries and a final summary.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed on your machine.
- Flask 2.1.1 and other required Python packages installed. You can install them using `pip`:

``` pip install Flask flask-ngrok pydub openai moviepy ```

or 

``` pip install -r requirements.txt ```


- OpenAI API key. You can obtain one from the OpenAI website.

- Whisper API key. You can obtain one from the Whisper API provider.

## Installation
Clone this repository to your local machine:

``` git clone https://github.com/pratyushlohumi26/Media_summarizer.git ``` 

### Navigate to the project directory:

```cd Media_summarizer/```

1. Set your OpenAI API key as environment variables. You can do this by creating a .env file in the project root directory and adding your keys:

``` OPENAI_API_KEY=your_openai_api_key_here ```

2. Run the Flask application:

``` python app.py ``` 

The application should now be running locally at http://localhost:5000.

## Usage
- Access the web application by opening your web browser and navigating to http://localhost:5000.

- Upload an audio (MP3) or video (MP4) file.

- The application will process the file, transcribe it, summarize it, and display the results.

- You can view individual chunk summaries as well as a final summary of the processed content.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Flask - Web framework for Python.
- OpenAI - API for natural language processing.
- Whisper - API for automatic transcription of audio.

## Contributing

Contributions are welcome! Please feel free to open an issue or create a pull request with any improvements or additional features.



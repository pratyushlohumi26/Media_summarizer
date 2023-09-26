import os
import time
from flask import Flask, request, render_template, redirect, url_for
import openai
from moviepy.editor import AudioFileClip, VideoFileClip
from waitress import serve
import pandas as pd
from flask_cors import CORS, cross_origin
# Set up your OpenAI API key
# openai.api_key = 'YOUR_API_KEY'

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Define the directory to store uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define the directory to store audio segments
SEGMENT_FOLDER = 'segments'
app.config['SEGMENT_FOLDER'] = SEGMENT_FOLDER

@app.route('/')
@cross_origin()
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
@cross_origin()

def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        

        # Check the file extension to determine if it's an MP3 or MP4 file
        file_extension = os.path.splitext(filename)[1].lower()
        start_time = time.time()  # Start timing the request processing
        if file_extension == '.mp3':
            # Handle MP3 files
            # Chunk the audio into 15-minute segments
            segment_paths = chunk_audio(filename)
            
            system_prompt = """
                        You are a helpful assistant that summarizes videos/audios.
                        You are provided chunks of raw audio that were transcribed from the video's audio.
                        Summarize the current chunk to succint and clear bullet points of its contents.
                        """
            
            # Transcribe each segment using Whisper
            transcriptions = []
            for segment_path in segment_paths:
                transcription = transcribe_audio(segment_path)
                transcriptions.append(transcription)

            # Summarize each segment using GPT-3.5-turbo
            summaries = []
            for transcription in transcriptions:
                summary = summarize_text(transcription, system_prompt)
                summaries.append(summary)
            
            system_prompt_tldr = """
                                You are a helpful assistant that summarizes videos/audios.
                                Someone has already summarized the video to key points.
                                Summarize the key points to a short summary that captures the essence of all the points.
                                """
            
            # Create a short summary of all the chunk summaries using GPT-3.5-turbo
            master_summary = summarize_text("\n".join(summaries), system_prompt)
            end_time = time.time()  # End timing the request processing
            processing_time = end_time - start_time
            print(f"Processing time: {processing_time:.2f} seconds")
            save_in_csv(filename, summaries, master_summary)
            return render_template('result.html', master_summary=master_summary, chunk_summaries=summaries, processing_time=processing_time)

        elif file_extension == '.mp4':
            # Handle MP4 files
            # Extract audio from the MP4 file
            audio_filename = convert_mp4_to_audio(filename)

            # Chunk the audio into 15-minute segments
            segment_paths = chunk_audio(audio_filename)
            system_prompt = """
                        You are a helpful assistant that summarizes videos/audios.
                        You are provided chunks of raw audio that were transcribed from the video's audio.
                        Summarize the current chunk to succint and clear bullet points of its contents.
                        """
            # Transcribe each segment using Whisper
            transcriptions = []
            for segment_path in segment_paths:
                transcription = transcribe_audio(segment_path)
                transcriptions.append(transcription)

            # Summarize each segment using GPT-3.5-turbo
            summaries = []
            for transcription in transcriptions:
                summary = summarize_text(transcription, system_prompt)
                summaries.append(summary)
            
            system_prompt_tldr = """
                                You are a helpful assistant that summarizes videos/audios.
                                Someone has already summarized the video to key points.
                                Summarize the key points to a short summary that captures the essence of all the points.
                                """
            # Create a short summary of all the chunk summaries using GPT-3.5-turbo
            master_summary = summarize_text("\n".join(summaries), system_prompt_tldr)
            save_in_csv(filename, summaries, master_summary)
            end_time = time.time()  # End timing the request processing
            processing_time = end_time - start_time
            
            return render_template('result.html', master_summary=master_summary, chunk_summaries=summaries, processing_time=processing_time)

        else:
            # Handle unsupported file types
            return "Unsupported file format."

def save_in_csv(filename, summaries, master_summary):
    # Check if "summary.csv" file exists in the current directory
    if os.path.isfile("master_summary.csv"):
        # If the file exists, read it into a DataFrame
        summary_csv = pd.read_csv('./master_summary.csv')
        print("Existing 'summary.csv' file loaded.")
    else:
        # If the file doesn't exist, create a new DataFrame
        summary_csv = pd.DataFrame(columns=['title','chunk_summary','short_summary'])
        summary_csv.to_csv("master_summary.csv", index=False)

        print("New 'master_summary.csv' file created.")



    data = {'title':filename, 'chunk_summary':summaries, 'short_summary':master_summary}
    new_row = pd.DataFrame([data])
    summary_csv = pd.concat([summary_csv, new_row], axis=0, ignore_index=True)

    summary_csv[["title", "chunk_summary", "short_summary"]].to_csv("./master_summary.csv", mode='w', index=False)
    print("FINAL Summary created :: ", summary_csv)
    

def convert_mp4_to_audio(mp4_path):
    # Create the audio directory if it doesn't exist
    os.makedirs(app.config['SEGMENT_FOLDER'], exist_ok=True)

    # Define the output audio filename
    audio_filename = os.path.join(app.config['SEGMENT_FOLDER'], 'audio_from_mp4.mp3')

    # Use moviepy to extract audio from the MP4 file and save it as MP3
    video = VideoFileClip(mp4_path)
    audio = video.audio
    audio.write_audiofile(audio_filename)

    return audio_filename

def chunk_audio(audio_path):
    # Create the segments directory if it doesn't exist
    os.makedirs(app.config['SEGMENT_FOLDER'], exist_ok=True)

    # Define the chunk duration in seconds (15 minutes)
    chunk_duration = 15 * 60

    # Use moviepy to split the audio into 15-minute segments
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    num_segments = int(total_duration // chunk_duration) + 1

    segment_paths = []

    for i in range(num_segments):
        start_time = i * chunk_duration
        end_time = min((i + 1) * chunk_duration, total_duration)
        output_path = os.path.join(app.config['SEGMENT_FOLDER'], f'segment_{i}.mp3')
        audio_subclip = audio.subclip(start_time, end_time)
        audio_subclip.write_audiofile(output_path)
        segment_paths.append(output_path)

    return segment_paths

def transcribe_audio(audio_path):
    # Use OpenAI Whisper API to transcribe the audio
    with open(audio_path, 'rb') as audio_file:
        response = openai.Audio.transcribe("whisper-1", audio_file)
    return response['text']

def summarize_text(text, prompt, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                ],
            )
    summary = response["choices"][0]["message"]["content"]
    return summary

if __name__ == "__main__":
    app.debug = True  # Set the debug mode directly on the app object
    app.port=5000
    app.host='0.0.0.0'
    app.threaded=True
    app.run()
    # serve(app, host='0.0.0.0', port=5000)

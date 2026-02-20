import streamlit as st
from dotenv import load_dotenv
import re

load_dotenv()  # load all the environment variables
import os
import google.generativeai as genai

from youtube_transcript_api import YouTubeTranscriptApi

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt="""You are Youtube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """


## getting the transcript data from yt videos

def extract_video_id(youtube_url):
    """Extract video ID from various YouTube URL formats."""
    # Pattern matches: watch?v=ID, youtu.be/ID, embed/ID, etc.
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # Standard watch?v= format
        r'youtu\.be\/([0-9A-Za-z_-]{11})',   # Short youtu.be format
        r'embed\/([0-9A-Za-z_-]{11})',        # Embed format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    return None

def extract_transcript_details(video_id):
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched = ytt_api.fetch(video_id)  # returns FetchedTranscript with .snippets
        text = " ".join(s.text for s in fetched)
        return text
    except Exception as e:
        error_msg = str(e)
        if "TranscriptsDisabled" in error_msg:
            st.error("This video has transcripts disabled. Please try a different video.")
        elif "NoTranscriptFound" in error_msg:
            st.error("No transcript found for this video. The video may not have captions available.")
        elif "VideoUnavailable" in error_msg or "VideoUnplayable" in error_msg:
            st.error("This video is unavailable or cannot be played. It may be private, deleted, or restricted.")
        else:
            st.error(f"Error fetching transcript: {error_msg}")
        return None
    
## getting the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text,prompt):

    model=genai.GenerativeModel("gemini-2.0-flash")
    response=model.generate_content(prompt+transcript_text)
    return response.text

st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

video_id = None
if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", width=True)
    else:
        st.warning("Invalid YouTube URL. Please enter a valid YouTube video link.")

if st.button("Get Detailed Notes"):
    if not youtube_link:
        st.warning("Please enter a YouTube link.")
    elif not video_id:
        st.warning("Could not extract video ID from the URL. Please check the link format.")
    else:
        with st.spinner("Fetching transcript..."):
            transcript_text = extract_transcript_details(video_id)

        if transcript_text:
            with st.spinner("Generating summary..."):
                summary = generate_gemini_content(transcript_text, prompt)
            
            if summary:
                st.markdown("## Detailed Notes:")
                st.write(summary)





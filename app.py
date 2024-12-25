import streamlit as st
import os
from youtube_transcript_api import YouTubeTranscriptApi
import re
from fpdf import FPDF
import io

# Set base prompt for summarization
base_prompt = """
You are a YouTube video summarizer. Take the transcript text and summarize 
the video as per the selected format. Format: {summary_format} with the summary size{summary_length}.
Please provide the summary of the text given here:
"""

# Function to extract video ID from URL
def extract_video_id(youtube_url):
    pattern = r"(?:v=|youtu\\.be/|embed/|v/|watch\\?v=|shorts/|e/|^)([A-Za-z0-9_-]{11})"
    match = re.search(pattern, youtube_url)
    if match:
        return match.group(1)
    else:
        st.error("Invalid YouTube URL. Please enter a valid link.")
        return None

# Function to extract transcript details
def extract_transcript_details(video_id):
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([entry["text"] for entry in transcript_data])
        return transcript
    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None

# Dummy AI function (to replace external API for deployment)
def generate_summary(transcript_text, prompt):
    return f"Generated summary based on the prompt and transcript text: {transcript_text[:200]}..."

# Function to generate PDF
def generate_pdf(summary_text):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, summary_text)
    return pdf.output(dest="S").encode("latin1")

# Streamlit app
st.markdown(
    """
    <div style="text-align: center;">
        <h1 style="color: #4a90e2;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/4/42/YouTube_icon_%282013-2017%29.png" alt="YouTube Logo" width="60" style="vertical-align: middle; margin-right: 10px;"> 
            YouGPT
        </h1>
        <p style="color: #4a90e2;">Your Intelligent YouTube Video Summarizer</p>
    </div>
    """,
    unsafe_allow_html=True
)

# User input for YouTube link
youtube_link = st.text_input("Enter YouTube Video Link")

# User input for summary type
summary_format = st.radio(
    "Select the summary format:",
    options=["Bullet Points", "Sentences", "Paragraphs", "Report", "Essay", "Review"],
    index=2
)
summary_length = st.radio(
    "Select the summary length in words:",
    options=["100 ", "500", "800", "1000", "1500", "custom"],
    index=3
)
# Extract video ID and display thumbnail
video_id = None
if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.markdown(
            f"<div style='text-align: center;'><img src='http://img.youtube.com/vi/{video_id}/0.jpg' width='300'></div>",
            unsafe_allow_html=True
        )

# Button to generate summary
if st.button("Generate Summary"):
    if not youtube_link:
        st.error("Please enter a YouTube link.")
        st.stop()

    if not video_id:
        st.error("Invalid YouTube URL. Please enter a valid link.")
        st.stop()

    transcript_text = extract_transcript_details(video_id)
    if not transcript_text:
        st.error("Failed to extract transcript. Ensure the video supports captions.")
        st.stop()

    # Generate summary
    summary_prompt = base_prompt.format(summary_format=summary_format)
    summary = generate_summary(transcript_text, summary_prompt)

    # Display summary
    st.subheader(f"Video Summary ({summary_format})")
    st.write(summary)

    # Provide download options
    col1, col2 = st.columns(2)
    with col1:
        # Download as TXT
        txt_data = BytesIO()
        txt_data.write(summary.encode("utf-8"))
        txt_data.seek(0)
        st.download_button(
            label="Download as TXT",
            data=txt_data,
            file_name=f"summary_{summary_format.lower()}.txt",
            mime="text/plain"
        )
    with col2:
        # Download as PDF
        pdf_data = BytesIO(generate_pdf(summary))
        st.download_button(
            label="Download as PDF",
            data=pdf_data,
            file_name=f"summary_{summary_format.lower()}.pdf",
            mime="application/pdf"
        )

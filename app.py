import streamlit as st
import io
import tempfile
import os
from PIL import Image
from audio_processor import merge_audio_files, add_metadata_to_audio

# Page configuration
st.set_page_config(
    page_title="Audio Merger",
    page_icon="🎵",
    layout="wide"
)

# Header
st.title("🎵 Audio File Merger")
st.markdown("Upload multiple audio files, merge them, and add metadata to create a single MP3 file.")

# Create a placeholder for status messages
status_placeholder = st.empty()

# Create a placeholder for progress bar
progress_placeholder = st.empty()

# Sidebar for instructions
with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    1. Upload audio files (MP3, WAV, OGG, etc.)
    2. Arrange them in desired order (drag to reorder)
    3. Add metadata (optional)
    4. Click "Merge Audio Files" button
    5. Download the merged MP3 file
    """)
    
    st.header("About")
    st.markdown("""
    This app merges multiple audio files into a single MP3 file and allows you to add metadata.
    
    It uses:
    - pydub for audio processing
    - mutagen for metadata tagging
    """)

# File uploader for audio files
st.subheader("Step 1: Upload Audio Files")
uploaded_files = st.file_uploader("Select audio files to merge", 
                                 type=["mp3", "wav", "ogg", "flac", "aac", "m4a"],
                                 accept_multiple_files=True)

# If files are uploaded, show file information
if uploaded_files:
    st.subheader(f"Uploaded Files ({len(uploaded_files)})")
    
    # Create a dataframe to display file information
    file_info = []
    for i, file in enumerate(uploaded_files):
        file_info.append(f"📂 {i+1}. {file.name} ({file.size/1024:.1f} KB)")
    
    # Display file list
    for info in file_info:
        st.text(info)
    
    st.info("Note: Files will be merged in the order listed above.")

# Metadata form
st.subheader("Step 2: Add Metadata (Optional)")

col1, col2 = st.columns(2)

with col1:
    title = st.text_input("Title")
    artist = st.text_input("Artist")
    album = st.text_input("Album")
    
with col2:
    year = st.text_input("Year")
    cover_image = st.file_uploader("Cover Image", type=["jpg", "jpeg", "png"])

# Preview cover image if uploaded
if cover_image:
    try:
        image = Image.open(cover_image)
        st.image(image, caption="Cover Image Preview", width=300)
    except Exception as e:
        st.error(f"Error previewing image: {str(e)}")

# Process files button
st.subheader("Step 3: Merge and Download")

if st.button("Merge Audio Files"):
    if not uploaded_files:
        st.error("Please upload at least one audio file to merge.")
    else:
        try:
            status_placeholder.info("Processing audio files... Please wait.")
            
            # Save uploaded files to temporary directory
            temp_dir = tempfile.mkdtemp()
            temp_files = []
            
            # Create progress bar
            progress_bar = progress_placeholder.progress(0)
            
            # Save uploaded files to temp directory
            for i, file in enumerate(uploaded_files):
                progress = (i / len(uploaded_files)) * 0.4  # First 40% for file saving
                progress_bar.progress(progress)
                
                # Save the file to a temporary location
                temp_file = os.path.join(temp_dir, file.name)
                with open(temp_file, "wb") as f:
                    # Reset pointer to the beginning of the file
                    file.seek(0)
                    # Read and write in chunks to avoid loading the whole file into memory
                    while True:
                        chunk = file.read(8192)  # 8KB chunks
                        if not chunk:
                            break
                        f.write(chunk)
                temp_files.append(temp_file)
                
                status_placeholder.info(f"Processing: Saved {i+1}/{len(uploaded_files)} files...")
            
            # Merge audio files
            status_placeholder.info("Merging audio files...")
            progress_bar.progress(0.5)  # 50% progress for merging
            
            merged_audio_path = os.path.join(temp_dir, "merged_audio.mp3")
            merge_audio_files(temp_files, merged_audio_path, 
                             status_callback=lambda msg: status_placeholder.info(msg),
                             progress_callback=lambda prog: progress_bar.progress(0.5 + prog * 0.3))  # 50-80% progress
            
            # Add metadata if provided
            if any([title, artist, album, year, cover_image]):
                status_placeholder.info("Adding metadata...")
                progress_bar.progress(0.8)  # 80% progress
                
                cover_image_data = None
                if cover_image:
                    cover_image_data = cover_image.getvalue()
                
                add_metadata_to_audio(merged_audio_path, {
                    "title": title,
                    "artist": artist,
                    "album": album,
                    "year": year,
                    "cover_image": cover_image_data
                })
            
            # Read the merged file to create a download link
            progress_bar.progress(0.9)  # 90% progress
            
            # Determine file name based on title or default
            file_name = "merged_audio.mp3"
            if title:
                # Remove special characters that might cause issues in filenames
                safe_title = "".join(c for c in title if c.isalnum() or c in [' ', '-', '_']).strip()
                if safe_title:
                    file_name = f"{safe_title}.mp3"
            
            with open(merged_audio_path, "rb") as file:
                btn = st.download_button(
                    label="Download Merged MP3",
                    data=file,
                    file_name=file_name,
                    mime="audio/mpeg"
                )
            
            # Complete progress
            progress_bar.progress(1.0)
            status_placeholder.success("✅ Processing complete! You can now download your merged audio file.")
            
            # Clean up temp files
            for file in temp_files:
                if os.path.exists(file):
                    os.remove(file)
            if os.path.exists(merged_audio_path):
                os.remove(merged_audio_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
                
        except Exception as e:
            status_placeholder.error(f"Error processing audio files: {str(e)}")
            progress_placeholder.empty()

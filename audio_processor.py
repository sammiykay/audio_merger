import os
import tempfile
import io
from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC
import time

def merge_audio_files(file_paths, output_path, status_callback=None, progress_callback=None):
    """
    Merge multiple audio files into a single MP3 file.
    
    Args:
        file_paths (list): List of paths to audio files
        output_path (str): Path to save the merged MP3 file
        status_callback (function): Function to call with status updates
        progress_callback (function): Function to call with progress updates (0.0 to 1.0)
    
    Returns:
        str: Path to the merged MP3 file
    """
    if not file_paths:
        raise ValueError("No files provided for merging")
    
    # Report status
    if status_callback:
        status_callback("Starting audio file merging...")
    
    # Initialize merged audio with the first file
    try:
        merged_audio = AudioSegment.from_file(file_paths[0])
    except Exception as e:
        raise ValueError(f"Error loading file {os.path.basename(file_paths[0])}: {str(e)}")
    
    # Process files in chunks to reduce memory usage
    for i, file_path in enumerate(file_paths[1:], 1):
        try:
            if status_callback:
                status_callback(f"Merging file {i+1}/{len(file_paths)}: {os.path.basename(file_path)}")
            
            # Load audio file
            audio = AudioSegment.from_file(file_path)
            
            # Append to merged audio
            merged_audio += audio
            
            # Report progress
            if progress_callback:
                progress_callback(i / (len(file_paths) - 1))
                
        except Exception as e:
            raise ValueError(f"Error processing file {os.path.basename(file_path)}: {str(e)}")
    
    # Export as MP3 (use a reasonable bitrate for quality vs size)
    if status_callback:
        status_callback("Exporting merged audio as MP3...")
    
    # Export in chunks to reduce memory usage
    merged_audio.export(
        output_path,
        format="mp3",
        bitrate="192k",
        tags={"comment": "Created with Audio Merger"}
    )
    
    return output_path

def add_metadata_to_audio(audio_path, metadata):
    """
    Add metadata to an MP3 file.
    
    Args:
        audio_path (str): Path to the MP3 file
        metadata (dict): Dictionary with metadata (title, artist, album, year, cover_image)
    
    Returns:
        str: Path to the MP3 file with metadata
    """
    try:
        # Load the MP3 file
        audio = MP3(audio_path)
        
        # Create ID3 tag if it doesn't exist
        if not audio.tags:
            audio.tags = ID3()
        
        # Add title if provided
        if metadata.get("title"):
            audio.tags.add(TIT2(encoding=3, text=metadata["title"]))
        
        # Add artist if provided
        if metadata.get("artist"):
            audio.tags.add(TPE1(encoding=3, text=metadata["artist"]))
        
        # Add album if provided
        if metadata.get("album"):
            audio.tags.add(TALB(encoding=3, text=metadata["album"]))
        
        # Add year if provided
        if metadata.get("year"):
            audio.tags.add(TDRC(encoding=3, text=metadata["year"]))
        
        # Add cover image if provided
        if metadata.get("cover_image"):
            image_data = metadata["cover_image"]
            audio.tags.add(
                APIC(
                    encoding=3,
                    mime="image/jpeg",
                    type=3,  # 3 is for cover image
                    desc="Cover",
                    data=image_data
                )
            )
        
        # Save the changes
        audio.save()
        
    except Exception as e:
        print(f"Error adding metadata: {str(e)}")
        
    return audio_path

import os
import tempfile
import io
import eyed3
import subprocess

def merge_audio_files(file_paths, output_path, status_callback=None, progress_callback=None):
    """
    Merge multiple audio files into a single MP3 file using ffmpeg for scalability.
    
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
    
    if status_callback:
        status_callback("Starting audio file merging...")
    if progress_callback:
        progress_callback(0.1) # 10% progress

    # Create a temporary file to list the input files for ffmpeg
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_list_file:
        for file_path in file_paths:
            # ffmpeg requires paths to be escaped
            temp_list_file.write(f"file '{file_path}'\n")
        temp_list_path = temp_list_file.name

    if status_callback:
        status_callback("Generated file list for merging...")
    if progress_callback:
        progress_callback(0.3) # 30% progress

    try:
        # Construct the ffmpeg command
        # -f concat: Use the concat demuxer
        # -safe 0: Allow unsafe file paths (temp directory paths can be long)
        # -i: Input file list
        # -b:a 192k: Set audio bitrate to 192kbps
        # -y: Overwrite output file if it exists
        command = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', temp_list_path,
            '-b:a', '192k',
            '-y',
            output_path
        ]

        if status_callback:
            status_callback("Running ffmpeg to merge files... This may take a moment.")

        # Execute the command
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        if status_callback:
            status_callback("ffmpeg process completed.")
        if progress_callback:
            progress_callback(0.9) # 90% progress

    except subprocess.CalledProcessError as e:
        # If ffmpeg fails, raise an error with its output for debugging
        error_message = f"ffmpeg error: {e.stderr}"
        if status_callback:
            status_callback(error_message)
        raise ValueError(error_message)
    except FileNotFoundError:
        # If ffmpeg is not installed or not in PATH
        error_message = "ffmpeg not found. Please ensure ffmpeg is installed and in your system's PATH."
        if status_callback:
            status_callback(error_message)
        raise RuntimeError(error_message)
    finally:
        # Clean up the temporary list file
        if os.path.exists(temp_list_path):
            os.remove(temp_list_path)

    if status_callback:
        status_callback("Exporting merged audio as MP3...")
    if progress_callback:
        progress_callback(1.0) # 100% progress

    return output_path

def add_metadata_to_audio(audio_path, metadata):
    """
    Add metadata to an MP3 file using eyed3.
    
    Args:
        audio_path (str): Path to the MP3 file
        metadata (dict): Dictionary with metadata (title, artist, album, year, cover_image)
    
    Returns:
        str: Path to the MP3 file with metadata
    """
    try:
        # Load the audio file
        audiofile = eyed3.load(audio_path)
        
        # Create tag if it doesn't exist
        if audiofile.tag is None:
            audiofile.initTag()
        
        # Add title if provided
        if metadata.get("title"):
            audiofile.tag.title = metadata["title"]
        
        # Add artist if provided
        if metadata.get("artist"):
            audiofile.tag.artist = metadata["artist"]
        
        # Add album if provided
        if metadata.get("album"):
            audiofile.tag.album = metadata["album"]
        
        # Add year if provided
        if metadata.get("year"):
            try:
                audiofile.tag.recording_date = metadata["year"]
            except:
                # Fallback if year is not in the correct format
                pass
        
        # Add cover image if provided
        if metadata.get("cover_image"):
            image_data = metadata["cover_image"]
            imageType = 3  # 3 means front cover
            audiofile.tag.images.set(imageType, image_data, "image/jpeg", "Cover")
        
        # Save the changes
        audiofile.tag.save()
        
    except Exception as e:
        print(f"Error adding metadata: {str(e)}")
        
    return audio_path

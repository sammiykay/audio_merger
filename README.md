# Audio File Merger

A lightweight Streamlit application for merging multiple audio files into a single MP3 with metadata tagging capabilities.

## Features

- Upload multiple audio files
- Merge audio files into a single MP3 file
- Add metadata (Artist, Album, Year, Cover Image)
- Preview cover image before processing
- Download the merged MP3 file
- Progress tracking during processing

## System Requirements

- Python 3.7 or higher
- 512MB RAM or higher
- Internet connection for downloading dependencies

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd audio-file-merger
   ```

2. Install required packages:
   ```
   pip install streamlit pydub mutagen pillow
   ```

3. Install FFmpeg (required for audio processing):
   
   **On Ubuntu/Debian:**
   ```
   sudo apt-get update
   sudo apt-get install ffmpeg
   ```
   
   **On macOS (using Homebrew):**
   ```
   brew install ffmpeg
   ```
   
   **On Windows:**
   Download from https://ffmpeg.org/download.html and add to PATH

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and go to http://localhost:5000

3. Upload your audio files using the file uploader

4. (Optional) Add metadata information:
   - Artist name
   - Album name
   - Year
   - Cover image

5. Click "Merge Audio Files" button to process the files

6. Download the merged MP3 file using the download button

## Technical Details

- **Audio Processing**: Uses pydub (which relies on FFmpeg) for efficient audio file merging
- **Metadata Tagging**: Uses mutagen for adding ID3 tags to MP3 files
- **Memory Usage**: Implements chunk-based processing to minimize memory usage
- **Supported Formats**: Can process MP3, WAV, OGG, FLAC, AAC, and M4A files
- **Output Format**: Exports merged files as MP3 with 192kbps bitrate

## Limitations

- Very large audio files may still require additional memory
- Processing time depends on the size and number of audio files
- Some audio formats may require additional codecs to be installed with FFmpeg

## License

[MIT License](LICENSE)

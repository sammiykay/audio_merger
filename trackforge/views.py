from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.core.files.storage import FileSystemStorage
from pydub import AudioSegment
from mutagen.easyid3 import EasyID3
import os
import tempfile
import threading
import time

from django.shortcuts import render

def home(request):
    return render(request, 'index.html')


# In-memory progress store (in production: use DB or Redis)
status_store = {}

def set_status(session_id, status):
    status_store[session_id] = status

def get_status(session_id):
    return status_store.get(session_id, "Waiting...")

@require_GET
def get_progress(request):
    session_id = request.GET.get("session_id")
    if not session_id:
        return JsonResponse({"status": "error", "message": "No session_id provided"}, status=400)
    return JsonResponse({"status": get_status(session_id)})

def delete_file_delayed(path, delay_seconds=600):
    def _delete():
        time.sleep(delay_seconds)
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"🗑️ Auto-deleted: {path}")
            except Exception as e:
                print(f"⚠️ Delete failed: {e}")
    threading.Thread(target=_delete).start()

@csrf_exempt
@require_POST
def ajax_merge_audio(request):
    try:
        form_data = request.POST
        files = request.FILES.getlist("audio_files")
        session_id = form_data.get("session_id", "anonymous")

        if not files:
            return JsonResponse({"status": "error", "message": "No audio files provided."}, status=400)

        fs = FileSystemStorage()
        output_dir = fs.location
        os.makedirs(output_dir, exist_ok=True)

        metadata = {
            "title": form_data.get("title", "Untitled"),
            "artist": form_data.get("artist", "Unknown Artist"),
            "album": form_data.get("album", "Unknown Album"),
            "genre": form_data.get("genre", "Misc"),
            "year": form_data.get("year", "2025")
        }

        merged = AudioSegment.empty()
        temp_files = []

        set_status(session_id, "Uploading completed.")
        set_status(session_id, "Merging started...")

        for file in files:
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1])
            for chunk in file.chunks():
                temp_audio.write(chunk)
            temp_audio.close()
            temp_files.append(temp_audio.name)
            audio = AudioSegment.from_file(temp_audio.name)
            merged += audio

        temp_wav_path = os.path.join(output_dir, f"{session_id}_merged.wav")
        merged.export(temp_wav_path, format="wav")

        set_status(session_id, "Tagging audio and exporting MP3...")

        final_mp3_path = os.path.join(output_dir, f"{metadata['title']}.mp3")
        AudioSegment.from_wav(temp_wav_path).export(final_mp3_path, format="mp3")

        tags = EasyID3(final_mp3_path)
        tags["title"] = metadata["title"]
        tags["artist"] = metadata["artist"]
        tags["album"] = metadata["album"]
        tags["genre"] = metadata["genre"]
        tags["date"] = metadata["year"]
        tags.save()

        os.remove(temp_wav_path)
        delete_file_delayed(final_mp3_path, delay_seconds=600)

        output_url = f"/download/{os.path.basename(final_mp3_path)}/"
        set_status(session_id, "✅ Merging complete. Ready to download.")

        return JsonResponse({"status": "success", "download_url": output_url})

    except Exception as e:
        set_status(session_id, f"❌ Error: {str(e)}")
        return JsonResponse({"status": "error", "message": str(e)})

    finally:
        for path in temp_files:
            try:
                os.remove(path)
            except Exception:
                pass

def download_and_delete(request, filename):
    from django.conf import settings
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if not os.path.exists(file_path):
        raise Http404("File not found")
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)

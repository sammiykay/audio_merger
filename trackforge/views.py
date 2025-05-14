from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.files.storage import FileSystemStorage
from pydub import AudioSegment
from mutagen.easyid3 import EasyID3
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import os
import tempfile
import threading
import time
from django.shortcuts import render

def home(request):
    return render(request, 'index.html')



def send_progress(session_id, status_text):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"status_{session_id}",
        {
            "type": "send_status",
            "message": {"status": status_text}
        }
    )


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

        send_progress(session_id, "Uploading completed.")
        send_progress(session_id, "Merging started...")

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

        send_progress(session_id, "Tagging audio and exporting MP3...")

        final_mp3_path = os.path.join(output_dir, f"{session_id}_output.mp3")
        AudioSegment.from_wav(temp_wav_path).export(final_mp3_path, format="mp3")

        tags = EasyID3(final_mp3_path)
        tags["title"] = metadata["title"]
        tags["artist"] = metadata["artist"]
        tags["album"] = metadata["album"]
        tags["genre"] = metadata["genre"]
        tags["date"] = metadata["year"]
        tags.save()

        os.remove(temp_wav_path)
        delete_file_delayed(final_mp3_path, delay_seconds=600)  # auto-delete after 10 min

        output_url = f"/download/{os.path.basename(final_mp3_path)}/"
        send_progress(session_id, "✅ Merging complete. Ready to download.")

        return JsonResponse({"status": "success", "download_url": output_url})

    except Exception as e:
        send_progress(session_id, f"❌ Error: {str(e)}")
        return JsonResponse({"status": "error", "message": str(e)})

    finally:
        for path in temp_files:
            try:
                os.remove(path)
            except Exception:
                pass


def download_and_delete(request, filename):
    file_path = os.path.join("media", filename)
    if not os.path.exists(file_path):
        raise Http404("File not found")

    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    return response

from flask import Flask, render_template, request, redirect, jsonify
import os
from whisper_transcriber import transcribe_audio_file
from db import init_db, insert_transcript, get_all_transcripts, get_transcript_by_id, get_all_venues, \
    get_venue_by_transcript_id, get_all_days, get_day_by_transcript_id, get_venue_day_by_id
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import send_file
import io
import queue
import threading
from uuid import uuid4
from pathlib import Path

transcription_queue = queue.Queue()
task_status = {}  # task_id: {"status": ..., "transcript_id": ..., "error": ...}
NAS_ROOT = "/data/nas"

def background_worker():
    while True:
        task_id, audio_bytes, filename, venue_id, day_id = transcription_queue.get()
        task_status[task_id]["status"] = "processing"

        try:
            text = transcribe_audio_file(audio_bytes, filename)
            transcript_id = insert_transcript(filename, text, venue_id, day_id)

            transcript = get_transcript_by_id(transcript_id)

            venue, day = get_venue_day_by_id(venue_id, day_id)
            save_dir = os.path.join(NAS_ROOT, day.name, venue.name)
            os.makedirs(save_dir, exist_ok=True)

            text_file = filename.rsplit('.', 1)[0] + ".txt"
            save_path = os.path.join(save_dir, text_file)
            with open(save_path, "wb") as f:
                f.write(transcript.transcription.encode("utf-8"))

            task_status[task_id]["status"] = "done"
            task_status[task_id]["transcript_id"] = transcript_id
        except Exception as e:
            task_status[task_id]["status"] = "error"
            task_status[task_id]["error"] = str(e)

        transcription_queue.task_done()

threading.Thread(target=background_worker, daemon=True).start()





app = Flask(__name__)

init_db()

@app.route('/')
def index():
    venues = get_all_venues()
    days = get_all_days()
    return render_template("index.html", venues=venues, days=days)

@app.route('/transcribe', methods=['POST'])
def handle_transcription():
    file = request.files.get('audio')
    if not file:
        return "No file uploaded", 400

    download_requested = request.form.get("download") == "on"
    filename = datetime.now(ZoneInfo("Europe/Moscow")).strftime("%Y%m%d_%H%M%S") + "_" + file.filename
    audio_bytes = file.read()

    venue_id = request.form.get("venue_id")
    day_id = request.form.get("day_id")
    venue_id = int(venue_id) if venue_id else None
    day_id = int(day_id) if day_id else None

    task_id = str(uuid4())
    task_status[task_id] = {
        "status": "queued",
        "download": download_requested
    }

    venue, day = get_venue_day_by_id(venue_id, day_id)
    save_dir = os.path.join(NAS_ROOT, day.name, venue.name)
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, filename)
    with open(save_path, "wb") as f:
        f.write(audio_bytes)

    transcription_queue.put((task_id, audio_bytes, filename, venue_id, day_id))

    return render_template("waiting.html", task_id=task_id)
    

@app.route('/history')
def history():
    transcripts = get_all_transcripts()
    return render_template("history.html", transcripts=transcripts) 

@app.route('/download/<int:transcript_id>')
def download(transcript_id):
    transcript = get_transcript_by_id(transcript_id)
    if not transcript:
        return "Transcript not found", 404

    transcript_file = io.BytesIO()
    transcript_file.write(transcript.transcription.encode("utf-8"))
    transcript_file.seek(0)

    return send_file(
        transcript_file,
        as_attachment=True,
        download_name=transcript.filename.rsplit('.', 1)[0] + ".txt",
        mimetype="text/plain"
    )

@app.route('/view/<int:transcript_id>')
def view_transcript(transcript_id):
    transcript = get_transcript_by_id(transcript_id)
    if not transcript:
        return "Transcript not found", 404

    venue = get_venue_by_transcript_id(transcript_id)
    day = get_day_by_transcript_id(transcript_id)

    return render_template("view_transcript.html", transcript=transcript, venue=venue, day=day)

@app.route('/queue_status/<task_id>')
def queue_status(task_id):
    status = task_status.get(task_id)
    if not status:
        return jsonify({"status": "not_found"})

    if status["status"] == "queued":
        position = list(transcription_queue.queue).index(
            next((item for item in transcription_queue.queue if item[0] == task_id), None)
        ) + 1
        return jsonify({"status": "queued", "position": position})

    elif status["status"] == "processing":
        return jsonify({"status": "processing"})

    elif status["status"] == "done":
        return jsonify({
            "status": "done",
            "transcript_id": status["transcript_id"],
            "download": status["download"]
        })

    elif status["status"] == "error":
        return jsonify({"status": "error", "message": status["error"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

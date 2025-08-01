from flask import Flask, render_template, request, redirect
import os
from whisper_transcriber import transcribe_audio_file
from db import init_db, insert_transcript, get_all_transcripts, get_transcript_by_id, get_all_venues, get_venue_by_transcript_id
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import send_file
import io


app = Flask(__name__)

init_db()

@app.route('/')
def index():
    venues = get_all_venues()
    return render_template("index.html", venues=venues)

@app.route('/transcribe', methods=['POST'])
def handle_transcription():
    file = request.files['audio']
    if not file:
        return "No file uploaded", 400

    download_requested = request.form.get("download") == "on"

    filename = datetime.now(ZoneInfo("Europe/Moscow")).strftime("%Y%m%d_%H%M%S") + "_" + file.filename

    audio_bytes = file.read()

    text = transcribe_audio_file(audio_bytes, filename)
    # text = "hi"

    venue_id = request.form.get("venue_id")
    if venue_id:
        venue_id = int(venue_id)
    else:
        venue_id = None


    transcript_id = insert_transcript(filename, text, venue_id)

    if download_requested:
        transcript_file = io.BytesIO()
        transcript_file.write(text.encode("utf-8"))
        transcript_file.seek(0)

        return send_file(
            transcript_file,
            as_attachment=True,
            download_name=filename.replace(".mp3", "") + ".txt",
            mimetype="text/plain"
        )
    else:
        return redirect(f"/view/{transcript_id}")
    

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

    return render_template("view_transcript.html", transcript=transcript, venue=venue)

if __name__ == "__main__":
    app.run(debug=True)
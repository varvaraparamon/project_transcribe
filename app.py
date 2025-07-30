from flask import Flask, render_template, request, redirect
import os
from whisper_transcriber import transcribe_audio_file
from db import init_db, insert_transcript, get_all_transcripts, get_transcript_by_id
from datetime import datetime
from flask import send_file
import io


app = Flask(__name__)

init_db()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/transcribe', methods=['POST'])
def handle_transcription():
    file = request.files['audio']
    if not file:
        return "No file uploaded", 400

    download_requested = request.form.get("download") == "on"

    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + file.filename

    audio_bytes = file.read()

    text = transcribe_audio_file(audio_bytes, filename)
    # text = "hi"

    insert_transcript(filename, text)

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
        return redirect("/history")
    

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

    return render_template("view_transcript.html", transcript=transcript)

if __name__ == "__main__":
    app.run(debug=True)
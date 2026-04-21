from flask import Flask, render_template, request, jsonify
from services.speech_to_text import transcribe_audio

import threading
import os
import subprocess

app = Flask(__name__)

progress = 0
transcript_result = ""
is_processing = False


def convert_audio(input_path, output_path):
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        output_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def process_audio(path):
    global progress, transcript_result, is_processing

    try:
        progress = 10

        convert_audio(path, "uploads/clean.wav")
        progress = 30

        transcript = transcribe_audio("uploads/clean.wav", update_progress)

        progress = 90

        transcript_result = transcript

        # 🔥 SIMPAN KE FILE (UNTUK EVALUASI NANTI)
        with open("hasil_transcript.txt", "w", encoding="utf-8") as f:
            f.write(transcript)

        progress = 100

    except Exception as e:
        transcript_result = f"Error: {str(e)}"
        progress = 0

    is_processing = False


@app.route("/", methods=["GET", "POST"])
def index():
    global is_processing, transcript_result

    if request.method == "POST":

        if is_processing:
            return jsonify({"status": "processing"})

        audio = request.files.get("audio")

        if not audio or audio.filename == "":
            return jsonify({"status": "error", "message": "File kosong"})

        os.makedirs("uploads", exist_ok=True)

        raw_path = os.path.join("uploads", audio.filename)
        audio.save(raw_path)

        transcript_result = ""
        is_processing = True

        thread = threading.Thread(target=process_audio, args=(raw_path,))
        thread.start()

        return jsonify({"status": "started"})

    return render_template("index.html")


@app.route("/progress")
def get_progress():
    return jsonify({
        "progress": progress,
        "processing": is_processing,
        "transcript": transcript_result
    })


def update_progress(value):
    global progress
    progress = min(value, 100)


if __name__ == "__main__":
    app.run(debug=True)
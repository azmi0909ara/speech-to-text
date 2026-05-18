from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
    send_from_directory
)

import threading
import os

from faster_whisper import WhisperModel

from utils.audio_utils import convert_audio

from utils.evaluation import (
    normalize_text,
    highlight_diff,
    calculate_metrics
)

from utils.timeline import generate_timeline
from utils.exporter import export_excel

app = Flask(__name__)

# =========================
# MODEL
# =========================
model = WhisperModel(
    "large-v3",
    compute_type="int8"
)

# =========================
# GLOBAL
# =========================
progress = 0

transcript_result = ""
ground_truth_result = ""

wer_result = "-"
cer_result = "-"
accuracy_result = "-"

highlight_result = ""

is_processing = False

time_labels = []
accuracy_timeline = []
wer_timeline = []

history = []

# 🔥 AUDIO FILE
audio_filename = ""

# =========================
# PROCESS AUDIO
# =========================
def process_audio(path, ground_truth):

    global progress
    global transcript_result
    global ground_truth_result

    global wer_result
    global cer_result
    global accuracy_result

    global highlight_result
    global is_processing

    global time_labels
    global accuracy_timeline
    global wer_timeline

    try:

        progress = 10

        # =========================
        # CONVERT AUDIO
        # =========================
        convert_audio(
            path,
            "uploads/clean.wav"
        )

        progress = 30

        # =========================
        # TRANSCRIBE
        # =========================
        segments, _ = model.transcribe(
            "uploads/clean.wav",
            language="id",
            beam_size=3,
            vad_filter=True
        )

        segments = list(segments)

        transcript = ""

        for seg in segments:
            transcript += seg.text.strip() + " "

        transcript = transcript.strip()

        transcript_result = transcript
        ground_truth_result = ground_truth

        progress = 70

        # =========================
        # EVALUATION
        # =========================
        if ground_truth.strip():

            metrics = calculate_metrics(
                ground_truth,
                transcript
            )

            wer_result = metrics["wer"]
            cer_result = metrics["cer"]
            accuracy_result = metrics["accuracy"]

            highlight_result = highlight_diff(
                normalize_text(ground_truth),
                normalize_text(transcript)
            )

            # =========================
            # TIMELINE
            # =========================
            (
                time_labels,
                accuracy_timeline,
                wer_timeline
            ) = generate_timeline(
                segments,
                ground_truth
            )

            # =========================
            # HISTORY
            # =========================
            history.append({
                "Transcript (AI)": transcript,
                "Ground Truth": ground_truth,
                "WER (%)": wer_result,
                "CER (%)": cer_result,
                "Accuracy (%)": accuracy_result
            })

        else:

            wer_result = "-"
            cer_result = "-"
            accuracy_result = "-"

            highlight_result = ""

            time_labels.clear()
            accuracy_timeline.clear()
            wer_timeline.clear()

        progress = 100

    except Exception as e:

        transcript_result = f"Error: {str(e)}"

        progress = 0

    is_processing = False

# =========================
# INDEX
# =========================
@app.route("/", methods=["GET", "POST"])
def index():

    global is_processing
    global audio_filename

    if request.method == "POST":

        if is_processing:
            return jsonify({
                "status": "processing"
            })

        audio = request.files.get("audio")
        gt_file = request.files.get("ground_truth")

        if not audio:
            return jsonify({
                "status": "error",
                "message": "Audio tidak ditemukan"
            })

        os.makedirs("uploads", exist_ok=True)

        raw_path = os.path.join(
            "uploads",
            audio.filename
        )

        audio.save(raw_path)

        # 🔥 SAVE AUDIO NAME
        audio_filename = audio.filename

        ground_truth = ""

        if gt_file:

            ground_truth = gt_file.read().decode(
                "utf-8",
                errors="ignore"
            )

        is_processing = True

        thread = threading.Thread(
            target=process_audio,
            args=(raw_path, ground_truth)
        )

        thread.start()

        return jsonify({
            "status": "started"
        })

    return render_template("index.html")

# =========================
# AUDIO ROUTE
# =========================
@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        "uploads",
        filename
    )

# =========================
# PROGRESS
# =========================
@app.route("/progress")
def get_progress():

    return jsonify({

        "progress": progress,
        "processing": is_processing,

        # 🔥 AUDIO
        "audio_file": audio_filename,

        # RESULT
        "transcript": transcript_result,
        "ground_truth": ground_truth_result,

        # METRICS
        "wer": wer_result,
        "cer": cer_result,
        "accuracy": accuracy_result,

        # HIGHLIGHT
        "highlight": highlight_result,

        # HISTORY
        "history": history,

        # CHART
        "time_labels": time_labels,
        "accuracy_timeline": accuracy_timeline,
        "wer_timeline": wer_timeline
    })

# =========================
# EXPORT
# =========================
@app.route("/export")
def export():

    file_path = export_excel(
        history,
        time_labels,
        accuracy_timeline,
        wer_timeline
    )

    return send_file(
        file_path,
        as_attachment=True
    )

# =========================
# MAIN
# =========================
if __name__ == "__main__":

    app.run(
        debug=True
    )
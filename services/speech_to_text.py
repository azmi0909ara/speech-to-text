from faster_whisper import WhisperModel
import os

# 🔥 pakai medium (karena kamu sudah aman)
model = WhisperModel(
    "medium",
    compute_type="int8"
)

def transcribe_audio(audio_path, progress_callback):

    if not os.path.exists(audio_path):
        return "File tidak ditemukan"

    if os.path.getsize(audio_path) == 0:
        return "Audio kosong"

    try:
        progress_callback(40)

        segments, _ = model.transcribe(
            audio_path,
            language="id",
            beam_size=3,
            vad_filter=True
        )

        segments = list(segments)
        total = len(segments)

        if total == 0:
            return "Audio tidak terbaca"

        text = ""

        for i, seg in enumerate(segments):
            text += seg.text.strip() + " "

            percent = 40 + int((i+1)/total * 50)
            progress_callback(percent)

        progress_callback(95)

        return text.strip()

    except Exception as e:
        return f"Error: {str(e)}"
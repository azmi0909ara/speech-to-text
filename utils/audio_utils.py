import subprocess

def convert_audio(input_path, output_path):

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", input_path,

        "-ar", "16000",
        "-ac", "1",

        output_path

    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL)
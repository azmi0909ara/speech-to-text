def summarize_text(text):

    if not text:
        return ""

    # ambil 2-3 kalimat pertama
    sentences = text.split(".")
    summary = ". ".join(sentences[:3])

    return summary.strip()
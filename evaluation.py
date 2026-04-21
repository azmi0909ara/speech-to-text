import os
import pandas as pd
from jiwer import wer, cer, Compose, ToLowerCase, RemovePunctuation, RemoveMultipleSpaces, Strip
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ==============================
# 🔧 KONFIG
# ==============================

TRANSCRIPT_FILE = "hasil_transcript.txt"
GROUND_TRUTH_FILE = "ground_truth.txt"

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# ==============================
# 🧹 NORMALISASI
# ==============================

transform = Compose([
    ToLowerCase(),
    RemovePunctuation(),
    RemoveMultipleSpaces(),
    Strip()
])

def load_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

hypothesis_raw = load_text(TRANSCRIPT_FILE)
reference_raw = load_text(GROUND_TRUTH_FILE)

hypothesis = transform(hypothesis_raw)
reference = transform(reference_raw)

# ==============================
# 📊 METRIK
# ==============================

print("===== HASIL EVALUASI =====")

if reference:
    wer_score = round(float(wer(reference, hypothesis)), 4)
    cer_score = round(float(cer(reference, hypothesis)), 4)
    accuracy = round((1 - wer_score) * 100, 2)

    print("WER       :", wer_score)
    print("CER       :", cer_score)
    print("Accuracy  :", accuracy, "%")

else:
    wer_score = None
    cer_score = None
    accuracy = None
    print("Tidak ada ground truth")

# ==============================
# 🧠 SUMMARY
# ==============================

print("\n===== GENERATE SUMMARY =====")

try:
    model_name = "google/flan-t5-small"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    text_input = hypothesis[:500]

    prompt = "Buat ringkasan singkat dan jelas dari percakapan berikut:\n" + text_input

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

    outputs = model.generate(
        **inputs,
        max_new_tokens=120,
        do_sample=False
    )

    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print("\nSUMMARY:")
    print(summary)

except Exception as e:
    summary = "-"
    print("Summary error:", e)

# ==============================
# 📁 SIMPAN DATAFRAME
# ==============================

df = pd.DataFrame({
    "Transcript": [hypothesis_raw],
    "Ground Truth": [reference_raw],
    "WER": [wer_score],
    "CER": [cer_score],
    "Accuracy (%)": [accuracy],
    "Summary": [summary]
})

# 🔥 pastikan numeric (biar Excel ga error)
df["WER"] = pd.to_numeric(df["WER"], errors="coerce")
df["CER"] = pd.to_numeric(df["CER"], errors="coerce")
df["Accuracy (%)"] = pd.to_numeric(df["Accuracy (%)"], errors="coerce")

# ==============================
# 💾 EXPORT
# ==============================

# CSV (aman)
df.to_csv("evaluation_result.csv", index=False, encoding="utf-8")

# EXCEL (RECOMMENDED)
with pd.ExcelWriter("evaluation_result.xlsx", engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Hasil")

print("\n✅ Export berhasil:")
print(" - evaluation_result.csv")
print(" - evaluation_result.xlsx")
from jiwer import (
    wer,
    cer,
    Compose,
    ToLowerCase,
    RemovePunctuation,
    RemoveMultipleSpaces,
    Strip
)

import difflib

transform = Compose([
    ToLowerCase(),
    RemovePunctuation(),
    RemoveMultipleSpaces(),
    Strip()
])

def normalize_text(text):
    return " ".join(
        transform(text).lower().split()
    )

def calculate_metrics(ref, hyp):

    ref = normalize_text(ref)
    hyp = normalize_text(hyp)

    w = wer(ref, hyp)
    c = cer(ref, hyp)
    acc = (1 - w) * 100

    return {
        "wer": round(w * 100, 2),
        "cer": round(c * 100, 2),
        "accuracy": round(acc, 2)
    }

def highlight_diff(ref, hyp):

    ref_words = ref.split()
    hyp_words = hyp.split()

    diff = difflib.ndiff(
        ref_words,
        hyp_words
    )

    result = []

    for d in diff:

        if d.startswith("- "):

            result.append(
                f"<span style='color:red'>{d[2:]}</span>"
            )

        elif d.startswith("+ "):

            result.append(
                f"<span style='color:green'>{d[2:]}</span>"
            )

        else:
            result.append(d[2:])

    return " ".join(result)
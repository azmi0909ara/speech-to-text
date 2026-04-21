from jiwer import wer

def calculate_wer(reference, prediction):

    if not reference or not prediction:
        return 1.0

    error = wer(reference, prediction)

    return round(error, 3)
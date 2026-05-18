from jiwer import wer

from utils.evaluation import normalize_text

def generate_timeline(segments, ground_truth):

    time_labels = []
    accuracy_timeline = []
    wer_timeline = []

    gt_clean = normalize_text(ground_truth)

    hyp_running = ""

    for seg in segments:

        seg_text = seg.text.strip()

        if not seg_text:
            continue

        hyp_running += " " + seg_text

        hyp_clean = normalize_text(
            hyp_running
        )

        ratio = len(hyp_clean) / max(len(gt_clean), 1)

        cut_index = int(
            len(gt_clean) * ratio
        )

        gt_slice = gt_clean[:cut_index]

        if len(gt_slice) > 10:

            w = wer(gt_slice, hyp_clean)

            # 🔥 PERCENT
            acc = (1 - w) * 100

            time_labels.append(
                f"{round(seg.end, 1)}s"
            )

            accuracy_timeline.append(
                round(acc, 2)
            )

            wer_timeline.append(
                round(w * 100, 2)
            )

    return (
        time_labels,
        accuracy_timeline,
        wer_timeline
    )
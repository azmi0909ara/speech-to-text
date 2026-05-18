import pandas as pd

def export_excel(
    history,
    time_labels,
    accuracy_timeline,
    wer_timeline
):


    file_path = "exports/evaluation_result.xlsx"

    df = pd.DataFrame(history)

    df_timeline = pd.DataFrame({
        "Time": time_labels,
        "Accuracy (%)": accuracy_timeline,
        "WER": wer_timeline
    })

    with pd.ExcelWriter(
        file_path,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Detail"
        )

        df_timeline.to_excel(
            writer,
            index=False,
            sheet_name="Timeline"
        )

    return file_path
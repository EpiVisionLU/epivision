import pandas as pd

def compress_emotions(df, frame_skip, video_fps, output_txt):
    # Sortera data efter id och time_code för att säkerställa rätt ordning
    df = df.sort_values(by=["id", "time_code"])

    # Skapa en ny lista för att hålla den komprimerade datan
    compressed_data = []

    # Gå igenom varje rad i df och gruppera känslor
    prev_row = None
    for _, row in df.iterrows():
        if prev_row is None:
            # Starta den första intervallet
            prev_row = row
            start_time = row["time_code"]
        elif row["id"] == prev_row["id"] and row["dominant_emotion"] == prev_row["dominant_emotion"]:
            # Om samma id och känsla fortsätter, fortsätt intervallet
            pass
        else:
            # Om id eller känsla ändras, avsluta nuvarande intervall och påbörja ett nytt
            duration = round((prev_row["frame"] - start_time) * (frame_skip / video_fps), 2)
            compressed_data.append(f'{prev_row["id"]}-EMOTION-AutoLabel\t{prev_row["id"]}\t{start_time}\t{prev_row["time_code"]}\t{duration}\t{prev_row["dominant_emotion"]}')
            # Börja ett nytt intervall
            start_time = row["time_code"]
        prev_row = row

    # Lägg till sista intervallet
    if prev_row is not None:
        duration = round((prev_row["frame"] - start_time) * (frame_skip / video_fps), 2)
        compressed_data.append(f'{prev_row["id"]}-EMOTION-AutoLabel\t{prev_row["id"]}\t{start_time}\t{prev_row["time_code"]}\t{duration}\t{prev_row["dominant_emotion"]}')

    # Skriv ut komprimerad data till txt-fil
    with open(output_txt, "w") as f:
        for line in compressed_data:
            f.write(line + "\n")

# Exempelanvändning
# frame_skip och video_fps hämtas från analyskoden
frame_skip = 5  # exempelvärde
video_fps = 30.0  # exempelvärde
df = pd.read_csv("two-faces.csv")
compress_emotions(df, frame_skip, video_fps, "elan_two-faces_emotions.txt")

import cv2
import pandas as pd

video = "output/detection_output.mp4"
csv = "shuttle_tracking/output_ball_filled.csv"
out = "analysis/output.mp4"


df = pd.read_csv(csv)
cap = cv2.VideoCapture(video)

w = int(cap.get(3))
h = int(cap.get(4))
fps = int(round(cap.get(cv2.CAP_PROP_FPS)))

writer = cv2.VideoWriter(
    out,
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (w, h)
)

frame_map = dict(zip(df["Frame"], zip(df["X"], df["Y"], df["Visibility"])))

fid = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    if fid in frame_map:
        x, y, v = frame_map[fid]
        if v == 1:
            cv2.circle(frame, (int(x), int(y)), 5, (0, 0, 255), -1)

    writer.write(frame)
    fid += 1

cap.release()
writer.release()
print("🎥 Final clean tracking video saved")









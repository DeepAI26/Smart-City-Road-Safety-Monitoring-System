import cv2
import os
import pandas as pd
import math
import gpxpy
import gpxpy.gpx
from datetime import datetime

# This is used to estimate the direction of movement
# between consecutive GPS points (e.g., N, NE, E, etc.)
def calculate_bearing(lat1, lon1, lat2, lon2):
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = (
        math.cos(lat1) * math.sin(lat2)
        - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    )

    bearing = math.degrees(math.atan2(x, y))
    bearing = (bearing + 360) % 360  # normalize to [0, 360)
    return bearing


# Groups the bearing angle into one of 8 directions
def bearing_to_direction(bearing):
    directions = [
        "N", "NE", "E", "SE",
        "S", "SW", "W", "NW"
    ]
    idx = round(bearing / 45) % 8
    return directions[idx]

# Extracts timestamped latitude and longitude values
# from the recorded GPS track
def load_gpx(gpx_file):
    gpx_data = []

    with open(gpx_file, 'r') as file:
        gpx = gpxpy.parse(file)

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    gpx_data.append({
                        "time": point.time,
                        "lat": point.latitude,
                        "lon": point.longitude
                    })

    return gpx_data

# Finds the GPS coordinate whose timestamp is closest
# to the given video timestamp
def find_closest_gps(timestamp, gpx_data):
    closest = min(
        gpx_data,
        key=lambda x: abs((x["time"] - timestamp).total_seconds())
    )
    return closest


# 5. Extract video frames and attach GPS metadata
def extract_frames_with_gps(video_path, gpx_path, output_folder, frame_interval):

    # Create output folder for extracted images
    images_folder = os.path.join(output_folder, "images")
    os.makedirs(images_folder, exist_ok=True)

    csv_path = os.path.join(output_folder, "data.csv")

    # Load GPS track data
    gpx_data = load_gpx(gpx_path)

    # Open video file
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    frame_count = 0
    saved_count = 30  # start image numbering from a fixed offset

    data_records = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Current video time (in seconds)
        current_time = frame_count / fps

        # Extract a frame every 'frame_interval' seconds
        if current_time % frame_interval < 1 / fps:

            # Convert video time into an absolute timestamp
            video_timestamp = (
                gpx_data[0]["time"]
                + pd.to_timedelta(current_time, unit="s")
            )

            # Find the closest GPS point to this frame
            gps_point = find_closest_gps(video_timestamp, gpx_data)

            # Estimate movement direction using the next GPS point
            gps_index = gpx_data.index(gps_point)

            if gps_index < len(gpx_data) - 1:
                next_gps = gpx_data[gps_index + 1]
                bearing = calculate_bearing(
                    gps_point["lat"], gps_point["lon"],
                    next_gps["lat"], next_gps["lon"]
                )
                direction = bearing_to_direction(bearing)
            else:
                direction = "Unknown"

            # Save extracted frame as an image
            image_name = f"frame_{saved_count:04d}.jpg"
            image_path = os.path.join(images_folder, image_name)
            cv2.imwrite(image_path, frame)

            # Store metadata for CSV
            data_records.append({
                "image_name": image_name,
                "latitude": gps_point["lat"],
                "longitude": gps_point["lon"],
                "timestamp": gps_point["time"],
                "direction": direction,
                "street_name": "",
                "road_condition": "",
                "problem_type": ""
            })

            saved_count += 1

        frame_count += 1

    cap.release()

    # Save metadata to CSV for later processing
    df = pd.DataFrame(data_records)
    df.to_csv(csv_path, index=False)

    print(f"Saved {saved_count} images.")
    print(f"CSV saved to: {csv_path}")


video_file = "data file/run 2.MOV"
gpx_file = "data file/Run2d.gpx"
output_dataset = "datasetPro1-"

extract_frames_with_gps(
    video_file,
    gpx_file,
    output_dataset,
    frame_interval=3
)

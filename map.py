import pandas as pd
import folium
from haversine import haversine
from pathlib import Path
from utils import get_csv_path

# Load the metadata CSV that contains GPS points and road condition info
csv_path = get_csv_path()
if not csv_path.exists():
    raise FileNotFoundError(f"CSV file not found: {csv_path}")

df = pd.read_csv(csv_path)

# If timestamps exist, sort the data so road points are connected in order
# This helps avoid random zig-zag lines on the map
if "timestamp" in df.columns:
    df = df.sort_values("timestamp")

# Use the average latitude and longitude to center the map
center_lat = df["latitude"].mean()
center_lon = df["longitude"].mean()

# Create the base Folium map
m = folium.Map(location=[center_lat, center_lon], zoom_start=15)

# Define colors based on road condition severity
color_map = {
    "safe": "green",
    "minor_issue": "orange",
    "major_problem": "red"
}

# Convert DataFrame rows to dictionaries for easier access
points = df.to_dict("records")

# Maximum distance allowed between two points to be treated as the same road segment
# This prevents drawing long diagonal lines between unrelated points
MAX_SEGMENT_KM = 0.08  # ~80 meters

# Iterate through consecutive GPS points
for i in range(len(points) - 1):
    p1 = points[i]
    p2 = points[i + 1]

    # Calculate distance between consecutive points (Fix #1)
    dist = haversine(
        (p1["latitude"], p1["longitude"]),
        (p2["latitude"], p2["longitude"])
    )

    # Skip points that are too far apart (likely different roads)
    if dist > MAX_SEGMENT_KM:
        continue

    # Extract road condition details for the segment
    condition = p2["road_condition"]
    problem = p2.get("problem_type", "none")
    image = p2.get("image_name", "")

    # Choose segment color based on road condition
    color = color_map.get(condition, "gray")

    # Simple text shown when hovering over the road segment
    tooltip_text = (
        f"Condition: {condition} | "
        f"Problem: {problem}"
    )

    # Detailed popup shown when clicking the segment
    # Includes road info, length, and associated image
    popup_html = f"""
    <div style="width:220px">
        <b>Road Segment Details</b><br>
        <b>Condition:</b> {condition}<br>
        <b>Problem:</b> {problem}<br>
        <b>Length:</b> {dist*1000:.1f} meters<br><br>
        <img src="images/{image}" width="200">
    </div>
    """

    # Draw the road segment as a colored line on the map
    folium.PolyLine(
        locations=[
            (p1["latitude"], p1["longitude"]),
            (p2["latitude"], p2["longitude"])
        ],
        color=color,
        weight=6,
        opacity=0.9,
        tooltip=tooltip_text,
        popup=folium.Popup(popup_html, max_width=250)
    ).add_to(m)

# Save the final interactive map to an HTML file
output_path = Path(__file__).parent / "road_map.html"
m.save(str(output_path))
print(f"Interactive road segment map saved to: {output_path}")

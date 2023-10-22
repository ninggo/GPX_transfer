#TERRY
import tkinter as tk
from tkinter import filedialog
import os
import xml.etree.ElementTree as ET
import random
import math

# 生成自定义格式的XML
def generate_custom_format(coordinates):
    root = ET.Element("gpx")
    root.set("version", "1.1")
    root.set("creator", "Xcode")

    comment = ET.Comment(
        "\n Provide one or more waypoints containing a latitude/longitude pair. "
        "If you provide one waypoint, Xcode will simulate that specific location. "
        "If you provide multiple waypoints, Xcode will simulate a route visiting each waypoint."
    )
    root.append(comment)

    for lat, lon in coordinates:
        wpt = ET.Element("wpt")
        wpt.set("lat", str(lat))
        wpt.set("lon", str(lon))
        root.append(wpt)

    return ET.tostring(root, encoding="utf-8")

# 读取GPX文件并解析坐标点
def read_gpx_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    track_segment = root.find(".//{http://www.topografix.com/GPX/1/1}trkseg")
    track_points = track_segment.findall(".//{http://www.topografix.com/GPX/1/1}trkpt")

    coordinates = []
    for point in track_points:
        lat = float(point.get("lat"))
        lon = float(point.get("lon"))
        coordinates.append((lat, lon))

    return coordinates

# 计算两个坐标点之间的距离
def calculate_distance(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    radius = 6371000  # 地球半径（米）
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = (math.sin(delta_lat / 2) ** 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * (math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c
    return distance

# 在两个坐标点之间插入新的坐标点
def insert_new_coordinates(coord1, coord2):
    distance = calculate_distance(coord1, coord2)
    num_points = int(distance)  # 大约一米一个坐标点
    new_coordinates = []

    for i in range(num_points):
        ratio = (i + 1.5) / (num_points + 1.5)
        new_lat = coord1[0] + ratio * (coord2[0] - coord1[0]) + random.uniform(-0.00001, 0.00001)
        new_lon = coord1[1] + ratio * (coord2[1] - coord1[1]) + random.uniform(-0.00001, 0.00001)
        new_coordinates.append((new_lat, new_lon))

    return new_coordinates

# 選擇檔案函數
def select_gpx_file():
    input_file_path = filedialog.askopenfilename(title="選擇要轉換的GPX檔案")
    if input_file_path:
        selected_file_label.config(text=f"選擇的檔案：{input_file_path}")
        convert_button.config(state=tk.NORMAL)

# 執行轉檔函數
def convert_gpx_file():
    input_file_path = selected_file_label.cget("text").split("：")[1]  # 從選擇的檔案標籤中獲取檔案路徑
    output_file_path = os.path.splitext(input_file_path)[0] + "_modified.gpx"
    gpx_coordinates = read_gpx_file(input_file_path)
    new_gpx_coordinates = []

    for i in range(len(gpx_coordinates) - 1):
        new_gpx_coordinates.append(gpx_coordinates[i])
        new_coords = insert_new_coordinates(gpx_coordinates[i], gpx_coordinates[i + 1])
        new_gpx_coordinates.extend(new_coords)

    wpt_xml = generate_custom_format(new_gpx_coordinates)

    with open(output_file_path, "wb") as gpx_file:
        gpx_file.write(wpt_xml)

    result_label.config(text=f"已生成新的 GPX 文件：{output_file_path}")

# 創建主視窗
root = tk.Tk()
root.title("GPX轉檔程式")

# 選擇檔案按鈕
select_button = tk.Button(root, text="選擇GPX檔案", command=select_gpx_file)
select_button.pack(pady=10)

# 顯示選擇的檔案的標籤
selected_file_label = tk.Label(root, text="", wraplength=300)
selected_file_label.pack()

# 執行轉檔按鈕
convert_button = tk.Button(root, text="執行轉檔", state=tk.DISABLED, command=convert_gpx_file)
convert_button.pack(pady=10)

# 顯示轉檔結果的文本框
result_label = tk.Label(root, text="", wraplength=300)
result_label.pack()

root.mainloop()

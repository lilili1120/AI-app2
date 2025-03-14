from flask import Flask, request, jsonify
import requests
import polyline

app = Flask(__name__)

# ルート（動作確認用）
@app.route("/")
def home():
    return "Root Planner API is running!"

# OSMルート計算関数
def get_osm_route(start, end):
    base_url = "https://routing.openstreetmap.de/routed-car/route/v1/driving"
    url = f"{base_url}/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&steps=true"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "ルート計算に失敗しました。"}

# 住所から緯度経度を取得（OSM Nominatim API）
def geocode_location(location_name):
    url = f"https://nominatim.openstreetmap.org/search?q={location_name}, Japan&format=json"
    headers = {"User-Agent": "MyRouteApp/1.0"}
    response = requests.get(url, headers=headers).json()

    if response and len(response) > 0:
        return float(response[0]["lat"]), float(response[0]["lon"])
    else:
        return None

# API: ルート検索
@app.route("/route", methods=["GET"])
def route():
    start_location = request.args.get("start")  # 例: 35.6895,139.6917
    end_location = request.args.get("end")  # 例: 34.6937,135.5023

    if not start_location or not end_location:
        return jsonify({"error": "start と end を指定してください。"}), 400

    try:
        start_coords = tuple(map(float, start_location.split(",")))
        end_coords = tuple(map(float, end_location.split(",")))
    except ValueError:
        return jsonify({"error": "座標の形式が正しくありません。"}), 400

    route_result = get_osm_route(start_coords, end_coords)
    
    if "routes" in route_result:
        encoded_polyline = route_result["routes"][0]["geometry"]
        decoded_route = polyline.decode(encoded_polyline)
        return jsonify({"route": decoded_route})
    else:
        return jsonify({"error": "ルートを取得できませんでした。"})

# API: 住所 → 緯度経度変換
@app.route("/geocode", methods=["GET"])
def geocode():
    location_name = request.args.get("location")

    if not location_name:
        return jsonify({"error": "location を指定してください。"}), 400

    coords = geocode_location(location_name)
    
    if coords:
        return jsonify({"location": location_name, "lat": coords[0], "lon": coords[1]})
    else:
        return jsonify({"error": "住所の位置情報が見つかりませんでした。"}), 404

# Render用の実行コード
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

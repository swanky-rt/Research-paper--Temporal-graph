from flask import Flask, request, jsonify
import math

app = Flask(__name__)

# Haversine formula to calculate distance (in meters) between two GPS points
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # distance in meters

@app.route('/check-location', methods=['POST'])
def check_location():
    data = request.get_json()
    user_lat = data.get("userLat")
    user_lon = data.get("userLon")
    target_lat = data.get("targetLat")
    target_lon = data.get("targetLon")

    if None in (user_lat, user_lon, target_lat, target_lon):
        return jsonify({"error": "Missing coordinates"}), 400

    distance = haversine_distance(user_lat, user_lon, target_lat, target_lon)
    within_range = distance <= 50  # Acceptable radius in meters

    return jsonify({
        "withinRange": within_range,
        "distanceMeters": round(distance, 2)
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5004)
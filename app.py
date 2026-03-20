from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import os
import requests

app = Flask(__name__)
CORS(app)

MODEL_PATH = 'AI/irrigation_ai_model.pkl'
WEATHER_API_KEY = "b6ce4f6cc8657457d6863b33df17620e" 
CITY = "Pune,IN"

@app.route('/get-smart-data', methods=['POST'])
def predict():
    try:
        if not os.path.exists(MODEL_PATH):
            return jsonify({'error': 'Model not trained'}), 404

        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)

        data = request.get_json()
        t = float(data.get('temp', 25))
        h = float(data.get('humidity', 50))
        m = float(data.get('moisture', 40))

        # 1. AI Prediction
        ai_minutes = float(model.predict([[t, h, m]])[0])
        
        # 2. Weather Logic
        weather_adjustment = 1.0
        rain_chance = 0
        try:
            w_url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
            w_res = requests.get(w_url).json()
            if "Rain" in w_res['weather'][0]['main']:
                weather_adjustment = 0.1 
                rain_chance = 90.0
            else:
                rain_chance = max(0, min(100, (h * 0.8) - (m * 0.2)))
        except:
            rain_chance = max(0, min(100, (h * 0.8) - (m * 0.2)))

        final_minutes = round(float(ai_minutes * weather_adjustment), 1)

        # 3. Water Conservation Logic
        # Compares AI result against a standard 30-minute dumb timer
        STANDARD_TIME = 30.0 
        saved_diff = STANDARD_TIME - final_minutes
        water_saved_pct = round((saved_diff / STANDARD_TIME) * 100, 1) if saved_diff > 0 else 0.0

        print(f"DEBUG: AI={final_minutes}m | Saved={water_saved_pct}%")

        return jsonify({
            'ai_minutes': final_minutes,
            'rain_chance': round(rain_chance, 1),
            'water_saved': water_saved_pct
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=False)
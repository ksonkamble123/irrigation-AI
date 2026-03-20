import pickle
import os
import json

# Move your model loading outside the loop for speed
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'AI/irrigation_ai_model.pkl')

def main(context):
    # Appwrite sends data through context.req.body_json
    if context.req.method == 'POST':
        try:
            # 1. Load the model
            if not os.path.exists(MODEL_PATH):
                return context.res.json({'error': 'Model file not found'}, 404)

            with open(MODEL_PATH, 'rb') as f:
                model = pickle.load(f)

            # 2. Get data from the request
            data = context.req.body_json
            t = float(data.get('temp', 25))
            h = float(data.get('humidity', 50))
            m = float(data.get('moisture', 40))

            # 3. AI Prediction
            ai_minutes = float(model.predict([[t, h, m]])[0])
            
            # 4. Logic Calculation
            water_saved_pct = round(((30.0 - ai_minutes) / 30.0) * 100, 1)
            if water_saved_pct < 0: water_saved_pct = 0

            # 5. Return JSON response
            return context.res.json({
                'ai_minutes': round(ai_minutes, 1),
                'rain_chance': 0, 
                'water_saved': water_saved_pct
            })

        except Exception as e:
            context.error(f"Error: {str(e)}") # This shows in Appwrite logs
            return context.res.json({'error': 'AI processing failed'}, 500)

    return context.res.text('Please send sensor data via POST.')

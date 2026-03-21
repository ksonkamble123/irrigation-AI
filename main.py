import pickle
import os
import json

# 1. Setup paths (Appwrite looks in the same folder as main.py)
# The correct way to point to a subfolder in Appwrite
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'AI', 'irrigation_ai_model.pkl')
def main(context):
    # Appwrite Functions must use the 'context' object to read requests
    if context.req.method == 'POST':
        try:
            # 2. Check if the model file actually exists
            if not os.path.exists(MODEL_PATH):
                return context.res.json({'error': 'Model file not found in function folder'}, 404)

            # 3. Load the AI Model
            with open(MODEL_PATH, 'rb') as f:
                model = pickle.load(f)

            # 4. Get data from the website trigger
            # Appwrite pre-parses JSON into context.req.body_json
            data = context.req.body_json
            t = float(data.get('temp', 25))
            h = float(data.get('humidity', 50))
            m = float(data.get('moisture', 40))

            # 5. Run the AI Prediction
            # Note: The input [[t, h, m]] must match your training features
            prediction = model.predict([[t, h, m]])
            ai_minutes = float(prediction[0])
            
            # 6. Safety & Savings Logic
            # Assuming 30 mins was your old 'dumb' timer standard
            water_saved_pct = round(((30.0 - ai_minutes) / 30.0) * 100, 1)
            if water_saved_pct < 0: water_saved_pct = 0
            if water_saved_pct > 100: water_saved_pct = 100

            # 7. Return the final result to your Website
            return context.res.json({
                'ai_minutes': round(ai_minutes, 1),
                'rain_chance': 0, # Placeholder if you don't have a weather API
                'water_saved': water_saved_pct,
                'status': 'success'
            })

        except Exception as e:
            # This will show up in your Appwrite "Logs" tab
            context.error(f"AI Error: {str(e)}")
            return context.res.json({'error': 'AI Processing Failed', 'details': str(e)}, 500)

    # If someone just visits the URL in a browser
    return context.res.text("AquaGrow AI Engine is Active. Send POST data to calculate.")

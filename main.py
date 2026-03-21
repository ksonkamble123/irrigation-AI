import pickle
import os

# Load model ONCE outside the function to save time
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'AI/irrigation_ai_model.pkl')

def main(context):
    # Appwrite trigger
    if context.req.method == 'POST':
        try:
            with open(MODEL_PATH, 'rb') as f:
                model = pickle.load(f)
            
            data = context.req.body_json
            # Prediction logic here...
            
            return context.res.json({"ai_minutes": 0, "status": "success"})
        except Exception as e:
            return context.res.json({"error": str(e)}, 500)
    
    return context.res.text("Active")

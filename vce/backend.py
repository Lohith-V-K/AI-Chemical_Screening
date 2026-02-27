from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import pickle
import os

# ---- LOAD KEY FROM .env FILE ----
load_dotenv()
API_KEY = os.getenv('API_KEY')
PORT = int(os.getenv('FLASK_PORT', 5000))

app = Flask(__name__)
CORS(app)

print(f"API Key loaded: {API_KEY[:8]}...")  # shows first 8 chars only

# ---- KEY CHECK FUNCTION ----
def check_api_key():
    key = request.headers.get('X-API-Key')
    if not key:
        key = request.args.get('api_key')
    if key != API_KEY:
        return False
    return True

# Load model files
print("Loading model files...")
df = pd.read_csv("preprocessed_chemicals.csv")
fingerprints = np.load("fingerprints.npy")

with open("similarity_model.pkl", "rb") as f:
    similarity_model = pickle.load(f)

with open("final_model.pkl", "rb") as f:
    toxicity_model = pickle.load(f)

print("All files loaded!")

@app.route('/health', methods=['GET'])
def health():
    if not check_api_key():
        return jsonify({'error': 'Invalid or missing API key'}), 401
    return jsonify({
        'status': 'running',
        'total_chemicals': len(df),
        'model_loaded': True
    })

@app.route('/recommend', methods=['POST'])
def recommend():
    if not check_api_key():
        return jsonify({'error': 'Invalid or missing API key'}), 401
    data = request.get_json()
    chemical_name = data.get('chemical_name', '')
    top_n = data.get('top_n', 5)
    if not chemical_name:
        return jsonify({'error': 'chemical_name is required'}), 400

    matches = df[
        df['IUPACName'].str.contains(chemical_name, case=False, na=False)
    ]
    if len(matches) == 0:
        return jsonify({'error': f'{chemical_name} not found'}), 404

    target = matches.iloc[0]
    target_idx = target.name
    target_tox = target['Toxicity_Encoded']

    target_fp = fingerprints[target_idx].reshape(1, -1)
    distances, indices = similarity_model.kneighbors(
        target_fp, n_neighbors=100
    )

    recommendations = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == target_idx:
            continue
        chem = df.iloc[idx]
        similarity = 1 - dist
        if chem['Toxicity_Encoded'] < target_tox:
            tox_improvement = target_tox - chem['Toxicity_Encoded']
            score = (similarity * 0.6) + (tox_improvement * 0.4)
            recommendations.append({
                'rank': 0,
                'cid': int(chem['CID']),
                'chemical_name': str(chem['IUPACName']),
                'similarity_percent': round(similarity * 100, 1),
                'toxicity': str(chem['Toxicity_Label']),
                'overall_score': round(score, 3),
                'data_source': str(chem['Toxicity_Source'])
            })

    recommendations = sorted(
        recommendations,
        key=lambda x: x['overall_score'],
        reverse=True
    )[:top_n]

    for i, r in enumerate(recommendations):
        r['rank'] = i + 1

    return jsonify({
        'input_chemical': str(target['IUPACName']),
        'input_toxicity': str(target['Toxicity_Label']),
        'total_found': len(recommendations),
        'recommendations': recommendations
    })

if __name__ == '__main__':
    app.run(debug=True, port=PORT)
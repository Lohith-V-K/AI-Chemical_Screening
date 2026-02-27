from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import pickle

app = Flask(__name__)
CORS(app)  # allows frontend to talk to backend

# ---- LOAD ALL FILES ONCE AT STARTUP ----
print("Loading model files...")
df = pd.read_csv("preprocessed_chemicals.csv")
fingerprints = np.load("fingerprints.npy")
combined_features = np.load("combined_features.npy")

with open("similarity_model.pkl", "rb") as f:
    similarity_model = pickle.load(f)

with open("final_model.pkl", "rb") as f:
    toxicity_model = pickle.load(f)

descriptor_cols = [
    'MolecularWeight', 'XLogP', 'TPSA',
    'HBondDonorCount', 'HBondAcceptorCount',
    'RotatableBondCount', 'HeavyAtomCount',
    'Complexity', 'Charge'
]
labels_map = {0:'Unknown', 1:'Low Toxic', 2:'Moderate Toxic', 3:'High Toxic'}
print("All files loaded successfully!")

# ---- ENDPOINT 1: HEALTH CHECK ----
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'running',
        'total_chemicals': len(df),
        'model_loaded': True
    })

# ---- ENDPOINT 2: SEARCH CHEMICAL ----
@app.route('/search', methods=['GET'])
def search():
    name = request.args.get('name', '')
    if not name:
        return jsonify({'error': 'name parameter required'}), 400

    matches = df[
        df['IUPACName'].str.contains(name, case=False, na=False)
    ][['CID', 'IUPACName', 'Toxicity_Label', 'MolecularWeight', 'XLogP']].head(10)

    if len(matches) == 0:
        return jsonify({'error': f'{name} not found', 'results': []}), 404

    return jsonify({
        'results': matches.to_dict(orient='records'),
        'count': len(matches)
    })

# ---- ENDPOINT 3: GET RECOMMENDATIONS ----
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    chemical_name = data.get('chemical_name', '')
    top_n = data.get('top_n', 5)

    if not chemical_name:
        return jsonify({'error': 'chemical_name is required'}), 400

    # Find chemical
    matches = df[
        df['IUPACName'].str.contains(chemical_name, case=False, na=False)
    ]

    if len(matches) == 0:
        return jsonify({'error': f'{chemical_name} not found'}), 404

    target = matches.iloc[0]
    target_idx = target.name
    target_tox = target['Toxicity_Encoded']

    # Check if already low toxicity
    if target_tox <= 1:
        return jsonify({
            'message': 'Chemical is already low toxicity',
            'input_chemical': target['IUPACName'],
            'input_toxicity': target['Toxicity_Label'],
            'recommendations': []
        })

    # Find similar chemicals
    target_fp = fingerprints[target_idx].reshape(1, -1)
    distances, indices = similarity_model.kneighbors(
        target_fp, n_neighbors=100
    )

    # Filter safer ones and rank
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
                'molecular_weight': round(float(chem['MolecularWeight']), 2),
                'xlogp': round(float(chem['XLogP']), 2),
                'overall_score': round(score, 3),
                'data_source': str(chem['Toxicity_Source'])
            })

    # Sort by score
    recommendations = sorted(
        recommendations,
        key=lambda x: x['overall_score'],
        reverse=True
    )[:top_n]

    # Add rank numbers
    for i, r in enumerate(recommendations):
        r['rank'] = i + 1

    return jsonify({
        'input_chemical': str(target['IUPACName']),
        'input_toxicity': str(target['Toxicity_Label']),
        'input_cid': int(target['CID']),
        'total_found': len(recommendations),
        'recommendations': recommendations
    })

# ---- ENDPOINT 4: GET CHEMICAL DETAILS ----
@app.route('/chemical/<int:cid>', methods=['GET'])
def chemical_detail(cid):
    match = df[df['CID'] == cid]
    if len(match) == 0:
        return jsonify({'error': 'Chemical not found'}), 404

    chem = match.iloc[0]
    return jsonify({
        'cid': int(chem['CID']),
        'name': str(chem['IUPACName']),
        'formula': str(chem['MolecularFormula']),
        'molecular_weight': round(float(chem['MolecularWeight']), 2),
        'xlogp': round(float(chem['XLogP']), 2),
        'tpsa': round(float(chem['TPSA']), 2),
        'toxicity': str(chem['Toxicity_Label']),
        'toxicity_score': int(chem['Toxicity_Encoded']),
        'data_source': str(chem['Toxicity_Source'])
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
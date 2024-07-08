from flask import Flask, request, render_template, jsonify
import pickle
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
#from models import LogisticRegression, KNN
from sklearn.preprocessing import StandardScaler 

app = Flask(__name__)

models = {}

#pickle_models = ['logistic_regression_model.pkl', 'xgboost_model.pkl', 'adaboost_model.pkl', 'knn_model.pkl', 'random_forest_model.pkl']
pickle_models = ['xgboost_model.pkl', 'adaboost_model.pkl', 'random_forest_model.pkl']
for model_name in pickle_models:
    with open(model_name, 'rb') as f:
        models[model_name.split('_model.pkl')[0]] = pickle.load(f)

models['neural_network'] = load_model('neural_network_model.h5')

with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

primary_weapons = [
    'AK-47', 'M4A1-S', 'M4A4', 'AWP', 'AUG', 'SG 553', 'FAMAS', 'Galil AR',
    'Scar-20', 'G3SG1', 'MP5-SD', 'UMP-45', 'P90', 'MAC-10', 'MP7', 'MP9',
    'PP-Bizon', 'Negev', 'M249', 'Nova', 'XM1014', 'Sawed-Off', 'MAG-7'
]

secondary_weapons = [
    'P2000', 'USP-S', 'Glock-18', 'P250', 'Five-SeveN', 'Tec-9', 
    'CZ75-Auto', 'Desert Eagle', 'R8 Revolver', 'Dual Berettas'
]

grenades = ['Smoke Grenade', 'High Explosive Grenade', 'Flashbang', 'Incendiary Grenade', 'Molotov', 'Decoy Grenade']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    
    players_data = []
    for player in data['players']:
        player_info = [
            int(player['team']), int(player['kills']), int(player['deaths']),
            int(player['defuse_kit']), int(player['helmet']), float(player['armor']),
            float(player['equipment_value']), float(player['money'])
        ]
        
        for weapon in primary_weapons:
            player_info.append(1 if weapon == player['primary_weapon'] else 0)
        
        for weapon in secondary_weapons:
            player_info.append(1 if weapon == player['secondary_weapon'] else 0)
        
        for grenade in grenades:
            player_info.append(player['grenades'].count(grenade))
        
        players_data.append(player_info)
    X = np.array(players_data).flatten().reshape(1, -1)
    np.set_printoptions(suppress=True)
    print(X)
    X = scaler.transform(X)
    print(X)
    
    print(X.shape)

    predictions = {}
    for model_name, model in models.items():
        if model_name == 'neural_network':
            y_probs = model.predict(X)
            y_pred = (y_probs > 0.5).astype(int)
            predictions[model_name] = int(y_pred[0][0])
        else:
            y_pred = model.predict(X)
            predictions[model_name] = int(y_pred[0])
    
    return jsonify(predictions)

if __name__ == '__main__':
    app.run(debug=True)

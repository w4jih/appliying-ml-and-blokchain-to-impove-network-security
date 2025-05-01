# server_app.py
from flask import Flask, request, jsonify
from joblib import load
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload_rules', methods=['POST'])
def upload_rules():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier envoyé'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Fichier vide'}), 400
    
    if file and file.filename.endswith('.joblib'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            rules = load(filepath)
            # Traitement des règles (exemple simplifié)
            rule_count = len(rules)
            first_tree_rules = rules[0]['rules'].count('\n') + 1
            
            return jsonify({
                'status': 'success',
                'rule_count': rule_count,
                'first_tree_rule_count': first_tree_rules,
                'message': 'Règles reçues et traitées'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            os.remove(filepath)
    else:
        return jsonify({'error': 'Format de fichier non supporté'}), 400
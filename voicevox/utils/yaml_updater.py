import os
import yaml
from typing import List, Dict, Any

def update_tts_yaml(speakers_data: List[Dict[str, Any]], yaml_path: str = 'models/tts/tts.yaml') -> None:
    """
    Update the tts.yaml file with the current speaker list from VOICEVOX API
    
    :param speakers_data: List of speaker data from VOICEVOX API
    :param yaml_path: Path to the tts.yaml file
    """
    # Read existing YAML
    if os.path.exists(yaml_path):
        with open(yaml_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
    else:
        config = {
            'model': 'voicevox',
            'model_type': 'tts',
            'model_properties': {
                'default_voice': '2',
                'voices': [],
                'word_limit': 40,
                'audio_type': 'wav',
                'max_workers': 5
            },
            'pricing': {
                'input': '0.0',
                'output': '0',
                'unit': '0.0',
                'currency': 'USD'
            }
        }

    # Create new voices list
    voices = []
    for speaker in speakers_data:
        for style in speaker['styles']:
            voices.append({
                'mode': str(style['id']),
                'name': f"{speaker['name']} - {style['name']}",
                'language': ['ja-JP']
            })

    # Update voices in config
    config['model_properties']['voices'] = voices

    # Ensure directory exists
    os.makedirs(os.path.dirname(yaml_path), exist_ok=True)

    # Write updated YAML
    with open(yaml_path, 'w', encoding='utf-8') as file:
        yaml.dump(config, file, allow_unicode=True, sort_keys=False)
import os
import yaml
from typing import List, Dict, Any

def load_speakers_data(credentials: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Load speakers data from VOICEVOX API
    
    :param credentials: Provider credentials
    :return: List of speaker data
    """
    import httpx
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{credentials['voicevox_api_base']}/speakers",
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as ex:
        raise ex

def update_tts_yaml(speakers_data: List[Dict[str, Any]], yaml_path: str = 'models/tts/tts.yaml') -> List[Dict[str, str]]:
    """
    Update the tts.yaml file with the current speaker list from VOICEVOX API and return formatted voice list
    
    :param speakers_data: List of speaker data from VOICEVOX API
    :param yaml_path: Path to the tts.yaml file
    :return: List of dictionaries containing voice information in {name, value} format
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
    formatted_voices = []
    for speaker in speakers_data:
        for style in speaker['styles']:
            voice_name = f"{speaker['name']} - {style['name']}"
            voices.append({
                'mode': str(style['id']),
                'name': voice_name,
                'language': ['ja-JP']
            })
            formatted_voices.append({
                'name': voice_name,
                'value': str(style['id'])
            })

    # Update voices in config
    config['model_properties']['voices'] = voices

    # Ensure directory exists
    os.makedirs(os.path.dirname(yaml_path), exist_ok=True)

    # Write updated YAML
    with open(yaml_path, 'w', encoding='utf-8') as file:
        yaml.dump(config, file, allow_unicode=True, sort_keys=False)

    return formatted_voices

# Load tts_yaml in formatted_voices format
def load_tts_yaml(yaml_path: str = 'models/tts/tts.yaml') -> List[Dict[str, str]]:
    """
    Load the tts.yaml file and return formatted voice list
    
    :param yaml_path: Path to the tts.yaml file
    :return: List of dictionaries containing voice information in {name, value} format
    """
    if os.path.exists(yaml_path):
        with open(yaml_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            voices = config['model_properties']['voices']
            return [{"name": voice["name"], "value": voice["mode"]} for voice in voices]
    else:
        return []



import json
import os
import requests
from typing import List, Tuple, Optional

import click

from utils import list_directories, find_files_in_directories

def process_clauses(file_path: str) -> List[Tuple[str, List[str]]]:
    with open(file_path, 'r') as file:
        data = json.load(file)

    result = []
    for item in data:
        name = item['name']
        formatted_clauses = []
        for clause in item['clauses']:
            formatted_clause = "\n".join([line + "..." for line in clause])
            formatted_clauses.append(formatted_clause)
        result.append((name, formatted_clauses))

    return result

def get_voice_id(api_key: str, voice_name: str) -> str:
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    voices = response.json()
    for voice in voices['voices']:
        if voice['name'] == voice_name:
            return voice['voice_id']

    raise Exception(f"Voice not found: {voice_name}")

def get_audio(api_key: str, voice_id: str, text: str) -> bytes:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v1",
        "voice_settings": {
            "stability": 0.55,
            "similarity_boost": 0.55
        }
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    return response.content

def save_audio_files(api_key: str, voice_id: str, script_dir: str, processed_clauses: List[Tuple[str, List[str]]]):
    for section_index, (section_name, clauses) in enumerate(processed_clauses):
        for clause_index, clause in enumerate(clauses):
            file_name = f"{section_index}_{section_name}_{clause_index}.wav"
            file_path = os.path.join(script_dir, "raw", file_name)
            if os.path.exists(file_path):
                print(f"Skipped existing audio file: {file_path}")
                continue
            audio = get_audio(api_key, voice_id, clause)
            with open(file_path, "wb") as file:
                file.write(audio)
            print(f"Saved audio file: {file_path}")

@click.command()
@click.option('--voice_name', default='Sleepy Sister', help='Voice name to use for generating audio.')
def fetch(voice_name: str):
    scripts_dir = "scripts"
    all_directories = list_directories(scripts_dir)
    target_file = "script.json"
    found_files = find_files_in_directories(all_directories, target_file)

    for file_path in found_files:
        print(f"Processing {os.path.basename(file_path)} at: {file_path}")
        processed_clauses = process_clauses(file_path)
        print(processed_clauses)

    api_key = os.getenv("ELEVEN_API_KEY")
    voice_name = "Sleepy Sister"
    voice_id = get_voice_id(api_key, voice_name)
    print(f"Voice ID for {voice_name}: {voice_id}")

    for file_path in found_files:
        script_dir = os.path.dirname(file_path)
        save_audio_files(api_key, voice_id, script_dir, processed_clauses)

if __name__ == "__main__":
    fetch()

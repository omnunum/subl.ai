import os
import requests

from typing import List, Tuple

from pathlib import Path

from classes import Script


ProcessedClauses = List[Tuple[str, List[str]]]

def process_clauses(script: Script) -> ProcessedClauses:
    result = []
    for section in script.sections:
        name = section.name
        formatted_clauses = []
        for clause in section.clauses:
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

def generate_audio_files(api_key: str, voice_id: str, write_dir: Path, processed_clauses: ProcessedClauses):
    for section_index, (section_name, clauses) in enumerate(processed_clauses):
        for clause_index, clause in enumerate(clauses):
            file_name = f"{section_index}_{section_name}_{clause_index}.wav"
            file_path = write_dir / file_name
            if os.path.exists(file_path):
                print(f"Skipped existing audio file: {file_path}")
                continue
            audio = get_audio(api_key, voice_id, clause)
            with open(file_path, "wb") as file:
                file.write(audio)
            print(f"Saved audio file: {file_path}")

def fetch(voice_name: str, script: Script, write_dir: Path):
    processed_clauses = process_clauses(script)
    print(processed_clauses)

    api_key = os.getenv("ELEVEN_API_KEY")
    if not api_key:
        raise Exception("ELEVEN_API_KEY environment variable not set")
    voice_id = get_voice_id(api_key, voice_name)
    print(f"Voice ID for {voice_name}: {voice_id}")
    
    generate_audio_files(api_key, voice_id, write_dir, processed_clauses)

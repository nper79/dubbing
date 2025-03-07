from flask import Flask, request, jsonify
import pysrt
from pydub import AudioSegment
import os
import requests

app = Flask(__name__)

# Criar diretório 'output' se não existir
if not os.path.exists('output'):
    os.makedirs('output')

@app.route('/')
def home():
    return 'Bem-vindo ao aplicativo de processamento de áudio!'

@app.route('/process_audio', methods=['POST'])
def process_audio():
    data = request.json
    srt_url = data['srt_url']
    audio_files = data['audio_files']  # Lista de URLs ou caminhos para arquivos de áudio

    # Baixar o arquivo SRT
    srt_path = download_file(srt_url, 'output/subtitles.srt')

    # Carregar legendas
    subs = pysrt.open(srt_path)

    # Combinar áudio
    combined_audio = AudioSegment.silent(duration=0)
    for i, audio_url in enumerate(audio_files):
        audio_path = download_file(audio_url, f'output/audio_{i}.mp3')
        audio_segment = AudioSegment.from_file(audio_path)
        silence_before = AudioSegment.silent(duration=subs[i].start.ordinal)
        combined_audio += silence_before + audio_segment

    # Exportar áudio combinado
    output_audio_path = 'output/final_audio.mp3'
    combined_audio.export(output_audio_path, format='mp3')

    return jsonify({'audio_file': output_audio_path})

def download_file(url, path):
    response = requests.get(url)
    with open(path, 'wb') as file:
        file.write(response.content)
    return path

if __name__ == "__main__":
    # Usar o PORT fornecido pelo Heroku
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

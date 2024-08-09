from flask import Flask, render_template, request, jsonify
import whisper
import base64
import io

app = Flask(__name__)

# Load Whisper model
model = whisper.load_model("base")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        audio_data = request.form.get('audioBlob')
        
        if not audio_data:
            return jsonify({'error': 'No audio data received'})

        # Extract Base64 part
        audio_data = audio_data.split(',')[1]
        audio_bytes = base64.b64decode(audio_data)
        audio_file = io.BytesIO(audio_bytes)

        # Save the audio file temporarily
        file_path = "./static/recorded_audio.wav"
        with open(file_path, 'wb') as f:
            f.write(audio_bytes)

        # Transcribe the audio file
        result = model.transcribe(file_path)
        transcription = result['text']

        return jsonify({'transcription': transcription})

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

from transformers import VitsModel, AutoTokenizer
import torch

# Load the pre-trained TTS model and tokenizer
model = VitsModel.from_pretrained("facebook/mms-tts-eng")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-eng")

# Define the input text
text = "hello this is soothu"

# Tokenize the input text
inputs = tokenizer(text, return_tensors="pt")

# Generate the speech waveform without gradients
with torch.no_grad():
    output = model(**inputs).waveform

# Save the waveform as a WAV file (optional)
import soundfile as sf
sf.write("output.wav", output.squeeze().numpy(), 22050)  # Assuming a sampling rate of 22.05 kHz

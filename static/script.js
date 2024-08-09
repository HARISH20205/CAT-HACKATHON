document.addEventListener('DOMContentLoaded', function() {
    const startButton = document.getElementById('startRecording');
    const stopButton = document.getElementById('stopRecording');
    const uploadForm = document.getElementById('uploadForm');
    const audioBlobInput = document.getElementById('audioBlob');
    const transcriptionResult = document.getElementById('transcriptionResult');
    
    let mediaRecorder;
    let audioChunks = [];

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Your browser does not support audio recording.');
        return;
    }

    startButton.addEventListener('click', async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            audioChunks = [];

            // Convert Blob to Base64 string for sending to server
            const reader = new FileReader();
            reader.onloadend = () => {
                audioBlobInput.value = reader.result;
                uploadForm.style.display = 'block';
            };
            reader.readAsDataURL(audioBlob);
        };

        mediaRecorder.start();
        startButton.disabled = true;
        stopButton.disabled = false;
    });

    stopButton.addEventListener('click', () => {
        mediaRecorder.stop();
        startButton.disabled = false;
        stopButton.disabled = true;
    });

    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(uploadForm);

        fetch('/', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.transcription) {
                transcriptionResult.innerHTML = `<h2>Transcription:</h2><p>${data.transcription}</p>`;
            } else {
                transcriptionResult.innerHTML = '<p>No transcription available.</p>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            transcriptionResult.innerHTML = '<p>An error occurred while processing the file.</p>';
        });
    });
});

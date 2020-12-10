let _STREAM = undefined;


let _IS_RECORDING = false;
let _MEDIA_RECORDER = undefined;
let RECOGNITION = undefined;
let TRANSCRIPT_DATA = [];
let TRANSCRIPT_FINAL = null;
function handleVoiceRecording() {

  if(_IS_RECORDING) {
    RECOGNITION.stop();
    _MEDIA_RECORDER.stop();
    _STREAM.getTracks() // get all tracks from the MediaStream
      .forEach( track => track.stop() ); // stop each of them
    return;
  } else {
    _IS_RECORDING = true;
  }

  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
     navigator.mediaDevices.getUserMedia (
        // constraints - only audio needed for this app
        {
           audio: true
        })

        // Success callback
        .then(function(stream) {
          _STREAM = stream;

          //////////////////////////////////////////////////////////////////////
          _MEDIA_RECORDER = new MediaRecorder(_STREAM, { 'mimeType' : 'audio/webm;codecs=opus' });

          let chunks = [];
          _MEDIA_RECORDER.ondataavailable = e => {
            chunks.push(e.data);
            if(_MEDIA_RECORDER.state === 'inactive') {

              const blob = new Blob(chunks, { 'type' : 'audio/webm;codecs=opus' })
              const file = new File([blob], 'vr.webm', { 'type' : 'audio/webm;codecs=opus' })

              const callback = function() {
                      window.location.reload();
                    };

              Api.voice_recording_create(file, TRANSCRIPT_FINAL, JSON.stringify(TRANSCRIPT_DATA), callback);
            }
          };

          var SpeechRecognition = SpeechRecognition || webkitSpeechRecognition;
          var recognition = new SpeechRecognition();
          RECOGNITION = recognition;
          recognition.continuous = false;
          recognition.lang = 'en-US';
          recognition.interimResults = true;
          recognition.maxAlternatives = 1;
          recognition.start();
          recognition.onresult = function(event) {
            const timeStamp = event.timeStamp,
                  transcript = event.results[0][0].transcript,
                  confidence = event.results[0][0].confidence,
                  isFinal = event.results[0].isFinal;
            TRANSCRIPT_DATA.push({ timeStamp, transcript, confidence, isFinal })
            if(isFinal) {
              TRANSCRIPT_FINAL = transcript;
            }
          }

          _MEDIA_RECORDER.start();
          //////////////////////////////////////////////////////////////////////
        })

        // Error callback
        .catch(function(err) {
           console.log('The following getUserMedia error occured: ' + err);
        }
     );
  } else {
     alert('getUserMedia not supported on your browser!');
  }
}

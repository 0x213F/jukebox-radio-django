// API
////////////////////////////////////////////////////////////////////////////////

let Api = function() {};

Api.text_comment_create = function(text, callback) {
  fetchFromServer('POST', '/comments/text-comment/create/', {'text': text}, callback);
}

Api.voice_recording_create = function(audioFile, transcriptFinal, transcriptData, callback) {
  fetchFromServer(
    'POST',
    '/comments/voice-recording/create/',
    {'transcriptFinal': transcriptFinal, 'transcriptData': transcriptData},
    callback,
    {audioFile: audioFile}
  );
}

Api.music_search = function(providers, formats, query, callback) {

  const data = {
    providers: providers.join(','),
    formats: formats.join(','),
    query: query,
  };

  fetchFromServer('GET', '/music/search/', data, callback);
}

Api.stream_create_queue = function(dataClass, uuid, callback) {

  const data = {
    'class': dataClass,
    musicUuid: uuid,
  };

  fetchFromServer('POST', '/streams/queue/create/', data, callback);
}

Api.stream_delete_queue = function(uuid, callback) {

  const data = {
    queueUuid: uuid,
  };

  fetchFromServer('POST', '/streams/queue/delete/', data, callback);
}

Api.music_create_track = function(audio_file, img_file, track_name, artist_name, album_name, callback) {

  const data = {
    track_name: track_name,
    artist_name: artist_name,
    album_name: album_name,
  };

  const files = {
    audio_file: audio_file,
    img_file: img_file,
  }

  fetchFromServer('POST', '/music/track/create/', data, callback, files);
}

Api.stream_play = function(callback) {
  fetchFromServer('POST', '/streams/stream/play-track/', {}, callback);
}

Api.stream_pause = function(callback) {
  fetchFromServer('POST', '/streams/stream/pause-track/', {}, callback);
}

Api.stream_next = function(callback) {
  fetchFromServer('POST', '/streams/stream/next-track/', {}, callback);
}

Api.stream_previous = function(callback) {
  fetchFromServer('POST', '/streams/stream/previous-track/', {}, callback);
}

Api.stream_forward = function(callback) {
  fetchFromServer('POST', '/streams/stream/scan-forward/', {}, callback);
}

Api.stream_backward = function(callback) {
  fetchFromServer('POST', '/streams/stream/scan-backward/', {}, callback);
}

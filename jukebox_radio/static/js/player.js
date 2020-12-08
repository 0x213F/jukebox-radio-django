const CSRF_TOKEN = document.getElementById("csrf-token").childNodes[0].value;

const failureCallback = data => { console.error(data); }

async function fetchFromServer(method = '', url = '', data = {}, successCallback = null, files = {}) {
  let response;

  if(!successCallback) {
    successCallback = console.log;
  }

  if(method !== 'GET') {
    const formData = new FormData();
    for (const [key, value] of Object.entries(data)) {
      formData.append(key, value);
    }
    for (const [key, value] of Object.entries(files)) {
      formData.append(key, value);
    }
    const request = new Request(url, {headers: {"X-CSRFToken": CSRF_TOKEN}});
    response = await fetch(request, {
      method: method,
      mode: 'same-origin',
      body: formData,
    })
      .then(response => response.json())
      .then(successCallback)
      .catch(failureCallback);
  } else {
    let searchParams = new URLSearchParams();
    for (const [key, value] of Object.entries(data)) {
      searchParams.set(key, value);
    }
    const getUrl = url + '/?' + searchParams.toString();
    const request = new Request(getUrl, {headers: {"X-CSRFToken": CSRF_TOKEN}});

    response = await fetch(request, {
      method: method,
      mode: 'same-origin',
    })
      .then(response => response.json())
      .then(successCallback)
      .catch(failureCallback);
  }
}

// TEXT COMMENT CREATE
////////////////////////////////////////////////////////////////////////////////
document.getElementById('text-comment-create-button').onclick = function() {
  const text = document.getElementById('text').textContent;

  Api.text_comment_create(text);
};

// REMOVE FROM QUEUE
////////////////////////////////////////////////////////////////////////////////
const removeFromQueueSubmit = function() {
  const dataUuid = this.getAttribute('data-uuid'),
        callback = function() {
          window.location.reload();
        };

  Api.stream_delete_queue(dataUuid, callback);

  this.disabled = true;
}

var anchors = document.getElementsByClassName('delete-queue');
for(var i = 0; i < anchors.length; i++) {
    var anchor = anchors[i];
    anchor.onclick = removeFromQueueSubmit;
}

// PLAY TRACK
////////////////////////////////////////////////////////////////////////////////
const playbackPlay = function() {
  const callback = function() {
          window.location.reload();
        };

  Api.stream_play(callback);
}

document.getElementById("playback-play").onclick = playbackPlay;

// PAUSE TRACK
////////////////////////////////////////////////////////////////////////////////
const playbackPause = function() {
  const callback = function() {
          window.location.reload();
        };

  Api.stream_pause(callback);
}

document.getElementById("playback-pause").onclick = playbackPause;

// PREVIOUS TRACK
////////////////////////////////////////////////////////////////////////////////
const playbackPrevious = function() {
  const callback = function() {
          window.location.reload();
        };

  Api.stream_previous(callback);
}

document.getElementById("playback-previous").onclick = playbackPrevious;

// NEXT TRACK
////////////////////////////////////////////////////////////////////////////////
const playbackNext = function() {
  const callback = function() {
          window.location.reload();
        };

  Api.stream_next(callback);
}

document.getElementById("playback-next").onclick = playbackNext;

// ADD TO QUEUE
////////////////////////////////////////////////////////////////////////////////
const addToQueueSubmit = function() {

  // disable all submit buttons
  const addToQueue = document.getElementsByClassName('add-to-queue');
  for(let q of addToQueue) {
    q.disabled = true;
  }

  const dataClass = this.getAttribute('data-class'),
        dataUuid = this.getAttribute('data-uuid'),
        callback = function() {
          window.location.reload();
        };

  Api.stream_create_queue(dataClass, dataUuid, callback);
}

// MUSIC SEARCH
////////////////////////////////////////////////////////////////////////////////
const musicSearchSubmit = function() {

  // providers
  let providers = [];
  let providerNames = [
      "jukebox_radio",
      "spotify",
      "youtube",
  ];
  for(let provider of providerNames) {
    if(document.getElementsByName(provider)[0].checked) {
      providers.push(provider)
    }
  }

  // formats
  let formats = [];
  let formatNames = [
      "track",
      "video",
      "album",
      "playlist",
      "session",
  ];
  for(let format of formatNames) {
    if(document.getElementsByName(format)[0].checked) {
      formats.push(format);
    }
  }

  // query
  const query = document.getElementById('search-query').value;

  // callback
  const callback = function(data) {
    let searchResults = document.getElementById('search-results');
    searchResults.innerHTML = "";
    for(let result of data.data) {
      searchResults.insertAdjacentHTML(
        'beforeend',
        `<tr>
          <td>${result.format}</td>
          <td>${result.provider}</td>
          <td>${result.name}</td>
          <td>${result.artist_name}</td>
          <td><button class="btn btn-primary add-to-queue" data-class="${result.class}" data-uuid="${result.uuid}">+</button>
        </tr>`
      );
    }
    const addToQueueFreshlyMinted = document.getElementsByClassName('add-to-queue');
    for(let q of addToQueueFreshlyMinted) {
      q.onclick = addToQueueSubmit;
    }
  }

  Api.music_search(providers, formats, query, callback);
};

document.getElementById("music-search-button").onclick = musicSearchSubmit;
document.getElementById("search-query").addEventListener("keyup", function(event) {
  if (event.keyCode === 13) {
    event.preventDefault();
    document.getElementById('music-search-button').click();
  }
});

// UPLOAD TRACK
////////////////////////////////////////////////////////////////////////////////
document.getElementById('track-create-button').onclick = function() {
  const text = document.getElementById('text').textContent;

  Api.music_create_track(
    document.getElementById('audio-file').files[0],
    document.getElementById('img-file').files[0],
    document.getElementById('track-name').value,
    document.getElementById('artist-name').value,
    document.getElementById('album-name').value,
    function() { window.location.reload(); }
  );
};

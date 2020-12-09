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
document.getElementById('comment-create-text-submit').onclick = function() {
  const text = document.getElementById('comment-create-text').value,
        callback = function() {
          window.location.reload();
        };

  Api.text_comment_create(text, callback);
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
          <td>
            <button class="btn btn-primary add-to-queue" data-class="${result.class}" data-uuid="${result.uuid}">
              <svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-plus-square-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" d="M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2zm6.5 4.5a.5.5 0 0 0-1 0v3h-3a.5.5 0 0 0 0 1h3v3a.5.5 0 0 0 1 0v-3h3a.5.5 0 0 0 0-1h-3v-3z"/>
              </svg>
            </button>
          </td>
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

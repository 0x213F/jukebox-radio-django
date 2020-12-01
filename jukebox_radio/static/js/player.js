const CSRF_TOKEN = document.getElementById("csrf-token").childNodes[0].value;

const failureCallback = data => { console.error(data); }

async function fetchFromServer(method = '', url = '', data = {}, successCallback = null) {
  let response;

  if(!successCallback) {
    successCallback = console.log;
  }

  if(method !== 'GET') {
    const request = new Request(url, {headers: {"X-CSRFToken": CSRF_TOKEN}});
    response = await fetch(request, {
      method: method,
      mode: 'same-origin',
      body: JSON.stringify(data),
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

////////////////////////////////////////////////////////////////////////////////
document.getElementById('text-comment-create-button').onclick = function() {
  const text = document.getElementById('text').textContent;

  // TEXT COMMENT CREATE
  Api.text_comment_create(text);
};

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

  // MUSIC SEARCH
  Api.stream_create_queue(dataClass, dataUuid, callback);
}

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

  // MUSIC SEARCH
  Api.music_search(providers, formats, query, callback);
};

document.getElementById("music-search-button").onclick = musicSearchSubmit;
document.getElementById("search-query").addEventListener("keyup", function(event) {
  // Number 13 is the "Enter" key on the keyboard
  if (event.keyCode === 13) {
    // Cancel the default action, if needed
    event.preventDefault();
    // Trigger the button element with a click
    document.getElementById('music-search-button').click();
  }
});
////////////////////////////////////////////////////////////////////////////////

let Api = function() {};

Api.text_comment_create = function(text) {
  fetchFromServer('POST', '/comments/text-comment/create/', {'text': text});
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
    uuid: uuid,
  };

  fetchFromServer('POST', '/streams/queue/create/', data, callback);
}

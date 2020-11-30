var CSRF_TOKEN = document.getElementById("csrf-token").childNodes[0].value;

async function fetchFromServer(method = '', url = '', data = {}) {
  let response;

  if(method !== 'GET') {
    response = await fetch(request, {
      method: method,
      mode: 'same-origin',
      body: JSON.stringify(data),
    });
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
    });
  }

  const responseJson = response.json();
  return responseJson;
}

////////////////////////////////////////////////////////////////////////////////

document.getElementById('text-comment-create-button').onclick = function() {
  const text = document.getElementById('text').textContent;
  Api.text_comment_create(text);
};

document.getElementById('music-search-button').onclick = function() {
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

  let formats = [];
  let formatNames = [
      "track",
      "album",
      "playlist",
      "session",
  ];
  for(let format of formatNames) {
    if(document.getElementsByName(format)[0].checked) {
      formats.push(format)
    }
  }

  const query = document.getElementById('search-query').value;
  Api.music_search(providers, formats, query);
};


////////////////////////////////////////////////////////////////////////////////

let Api = function() {};

Api.text_comment_create = function(text) {
  fetchFromServer('POST', '/comments/text-comment/create/', {'text': text});
}

Api.music_search = function(providers, formats, query) {

  const data = {
    providers: providers.join(','),
    formats: formats.join(','),
    query: query,
  }

  fetchFromServer('GET', '/music/search/', data);
}

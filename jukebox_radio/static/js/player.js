var CSRF_TOKEN = document.getElementById("csrf-token").childNodes[0].value;

async function fetchFromServer(method = '', url = '', data = {}) {

  const request = new Request(url, {headers: {"X-CSRFToken": CSRF_TOKEN}});

  const response = await fetch(request, {
    method: method,
    mode: 'same-origin',
    body: JSON.stringify(data),
  });

  const responseJson = response.json();
  console.log(responseJson);
  return responseJson;
}


document.getElementById('new-text-comment').onclick = function() {

  const text = document.getElementById('text').textContent;
  fetchFromServer('PUT', '/comments/text-comment/create/', {'text': text});
};

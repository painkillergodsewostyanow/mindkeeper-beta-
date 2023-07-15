function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');
const referrer = document.referrer

function ajax_send(url, params) {
	fetch(url, {
		method: 'POST',
		headers : {
		    'X-CSRFToken': csrftoken,
		    'X-Referrer': referrer,
			'Content-Type': 'application/x-www-form-urlencoded'
		},
	})
	    .then(response => response.json())
	    .then(json => render(json))

};


let like_trigger = document.getElementById('like_theme_trigger');

like_trigger.onclick = function(){

	let url = like_trigger.getElementsByTagName('a')[0].href
	ajax_send(url)

};

function render(data){
    document.getElementById('test_output').innerHTML = JSON.stringify(data.like)
}

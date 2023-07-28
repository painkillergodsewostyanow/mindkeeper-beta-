
const referrer = document.referrer

function ajax_like(url) {
	fetch(url, {
		method: 'POST',
		headers : {
		    'X-CSRFToken': csrf_token,
		    'X-Referrer': referrer,
			'Content-Type': 'application/x-www-form-urlencoded'
		},
	})
	    .then(response => response.json())
	    .then(json => render(json))
};


let like_trigger = document.getElementById('like_trigger');

like_trigger.onclick = function(){

	let url = like_trigger.getElementsByTagName('a')[0].href
	ajax_like(url)

};

function render(data){
    document.getElementById('likes').innerHTML = JSON.stringify(data.like)
}

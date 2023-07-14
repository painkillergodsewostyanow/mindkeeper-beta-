
function ajax_send(url, params) {
	fetch(`${url}?${params}`, {
		method: 'GET',
		headers : {
			'Content-Type': 'application/x-www-form-urlencoded'
		},
	})
	    .then(response => response.json())
	    .then(json => render(json))

};


let input = document.getElementById('input_query');

input.oninput = function(){

	let url = 'http://127.0.0.1:8000/storage/global_search_json'
	let params = `query=${input.value.toString()}`;
	ajax_send(url, params)

};

function render(data){
    document.getElementById('catalog').innerHTML = JSON.stringify(data)
}

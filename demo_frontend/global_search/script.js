function ajax_send(url, params) {
	fetch(`${url}?${params}`, {
		method: 'GET'
		headers : {

			'Content-Type': 'application/x-www-fform-urlencoded'

		},
	})

	.then(response => response.json())
	.then(json => render(json)).catch(error => console.error(error))

}


let input = document.getElementById('inpute_query');

input.oninput = function(){

	let url = 'http://127.0.0.1:8000/'
	let params = inpute.value.toString();
	ajax_send(url, params)

};	

function render(data){

	let template = Hogan.complite(html)
	let output = template.render(data)
	const ul = document.getElementById('catalog_place');
	ul.innerHTML = output;

}

let html = '\
{{#themes}}\
	<li class="wrapper">\
		<a href="">\
			<div href="" class="card">\
				<object>\
					<a href="" class="cross	">X</a>\
				</object>\
				<div class="photo">\
					<img src="" alt="">\
				</div>\
				<p class="object_title">ПРОГРАММИРОВАНИЕ</p>\
			</div>\
		</a>\
	</li>\
{{/themes}}\
{{#cards}}\
	<li class="wrapper">\
		<a href="">\
			<div href="" class="card">\
				<object>\
					<a href="" class="cross	">X</a>\
				</object>\
				<div class="photo">\
					<img src="" alt="">\
				</div>\
				<p class="object_title">ПРОГРАММИРОВАНИЕ</p>\
			</div>\
		</a>\
	</li>\
{{#cards}}'

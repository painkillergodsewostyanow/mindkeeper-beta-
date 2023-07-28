
// init triggers
let del_triggers = document.querySelectorAll('#del_obj')

for (i=0; i<del_triggers.length; i++){

    del_triggers[i].onclick = del_theme

}

// functions
function del_theme(){

    url = this.getElementsByTagName('a')[0].href
    ajax_del_theme(url)

}

//ajax-request

function ajax_del_theme(url) {
    fetch(url, {
		method: 'DELETE',
		headers : {
		    'X-CSRFToken': csrf_token,
		}
	})
	    .then(response => response.json())
	    .then(json => render_del_theme(json))
};

//render functions

function render_del_theme(data){

       let card = document.getElementById(JSON.parse(JSON.stringify(data.deleted_objs))[0].pk)
       card.remove()

}
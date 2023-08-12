
// init triggers
let del_theme_triggers = document.querySelectorAll('#del_theme')
let del_card_triggers = document.querySelectorAll('#del_card')


for (i=0; i<del_theme_triggers.length; i++){

    del_theme_triggers[i].onclick = del_theme

}

for (i=0; i<del_card_triggers.length; i++){

    del_card_triggers[i].onclick = del_card

}



// functions
function del_theme(){

    url = this.getElementsByTagName('a')[0].href
    ajax_del_theme(url)

}

function del_card(){

    url = this.getElementsByTagName('a')[0].href
    ajax_del_card(url)

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

function ajax_del_card(url) {
    fetch(url, {
		method: 'DELETE',
		headers : {
		    'X-CSRFToken': csrf_token,
		}
	})
	    .then(response => response.json())
	    .then(json => render_del_card(json))
};

//render functions

function render_del_theme(data){

       let card = document.getElementById(`theme_${data.deleted_objs[0].pk}`)
       card.remove()

}

function render_del_card(data){

       let card = document.getElementById(`card_${data.deleted_objs[0].pk}`)
       card.remove()

}
//const
const host = 'http://127.0.0.1:8000/'

// add listeners
let answer_triggers = document.querySelectorAll('.answer_trigger');
let del_comment_buttons = document.querySelectorAll('#del_comment');
let update_comment_buttons = document.querySelectorAll('#update_comment');

for (var i = 0; i<update_comment_buttons.length; i++){

    update_comment_buttons[i].onclick = add_update_comment_view

}

for (var i = 0; i < del_comment_buttons.length; i++){

    del_comment_buttons[i].onclick = del_comment

}

comment_form = document.getElementById('add_comment')
comment_url = comment_form.action
comment_form_button = comment_form.getElementsByTagName('button')[0]
comment_form_button.addEventListener('click', () => ajax_comment(comment_url, event, comment_form, false))


for (var i = 0; i < answer_triggers.length; ++i) {
    answer_triggers[i].onclick = show_add_comment_view
}

// functions that make ajax request
function add_update_comment_view(){
    if (this.parentNode.parentNode.getElementsByClassName('content')[0]){

        content = this.parentNode.parentNode.getElementsByClassName('content')[0].textContent

    }


    let edit_url = this.getElementsByTagName('a')[0].href
    if (this.parentNode.parentNode.getElementsByClassName('content')[0]){
        let form = document.createElement("form");
        form.method = 'POST'
        form.action = edit_url
        form.innerHTML =

        `
                    <input type='hidden' name='csrfmiddlewaretoken' value=${csrf_token}>\
                    <textarea name='content'>${content}</textarea>\
                    <button type='submit'>Изменить</button>\
        `
        formButton = form.getElementsByTagName('button')[0]
        console.log(edit_url)
        formButton.addEventListener('click', () => ajax_update_comment(edit_url, event, form))

        this.parentNode.parentNode.getElementsByClassName('content')[0].replaceWith(form)

    }else{


        let span = document.createElement("span");
        span.className = "content"
        span.textContent = content
        this.parentNode.parentNode.getElementsByTagName('form')[0].replaceWith(span)

    }


}


function del_comment(){


    let comment_id = this.parentNode.parentNode.parentNode.id
    let del_comment_url = this.getElementsByTagName('a')[0].href

    ajax_del_comment(del_comment_url)

}

function show_add_comment_view(){
        let answer_url = document.getElementById('add_answer_url').href
        let comment_pk = this.parentNode.id
        let csrf_token = document.getElementById('add_comment').getElementsByTagName('input')[0].value
        let obj = document.getElementById('add_comment').getElementsByTagName('input')[1].value
        let answer_blocks_div = document.getElementById(comment_pk).getElementsByClassName('answer_block')
        if(answer_blocks_div.length == 0){
            let div = document.createElement("div");
            div.className = "answer_block"
            div.innerHTML = `
                                <form action=${answer_url} method='POST'>\
                                    <input type='hidden' name='csrfmiddlewaretoken' value=${csrf_token}>\
                                    <textarea name='content'></textarea>\
                                    <input type='hidden' name='comment' value=${comment_pk}>\
                                    <input type='hidden' name='obj' value=${obj}>\
                                    <button id="answer_button" type='submit'>Ответить</button>\
                                </form>
                           `
            form = this.parentNode.insertBefore(div, this.nextSibling)
            .getElementsByTagName('form')[0]
            formButton = form.getElementsByTagName('button')[0]
            formButton.addEventListener('click', () => ajax_comment(answer_url, event, form, true))

        } else{
            answer_blocks_div[0].parentNode.removeChild(answer_blocks_div[0])
        }
}

// ajax_requests
function ajax_update_comment(url, event, form) {
    event.preventDefault()
    let form_data = new FormData(form)
    let span = document.createElement("span");
    span.className = "content"
    form.replaceWith(span)

    form.remove()

    fetch(url, {
		method: 'POST',
		body: form_data
	})
	    .then(response => response.json())
	    .then(json => render_update_comment(json))
};

function ajax_comment(url, event, form, is_sub_comment) {
    event.preventDefault()
    let form_data = new FormData(form)

    if (is_sub_comment){

        form.remove()

    }else{

        form.reset()

    }
    fetch(url, {
		method: 'POST',
		body: form_data
	})
	    .then(response => response.json())
	    .then(json => render_add_comment(json))
};

function ajax_del_comment(url) {
    fetch(url, {
		method: 'DELETE',
		headers : {
		    'X-CSRFToken': csrf_token,
		},
	})
	    .then(response => response.json())
	    .then(json => render_del_comment(json))
};

//render_functions
function render_update_comment(data){

    let comment_id = `comment_${data.updated_comment.pk}`
    comment = document.getElementById(comment_id)
    comment.getElementsByClassName('content')[0].textContent = data.updated_comment.content

}


function render_add_comment(data){
    if (data.authenticated == false){

        window.location.replace(`${host}${data.login_url}`);

    }

    let comment_json = data.comment

    obj = comment_json
    let pk = `comment_${comment_json.pk}`
    comment = document.createElement("div")
    comment.className = 'comment'
    comment.id = pk
    let request_user = data.comment.request_user

    Handlebars.registerHelper('if', function (v1, operator, v2, options) {

        switch (operator) {
            case '==':
                return (v1 == v2) ? options.fn(this) : options.inverse(this);
            case '!=':
                return (v1 != v2) ? options.fn(this) : options.inverse(this);
            case '||':
            return (v1 || v2) ? options.fn(this) : options.inverse(this);
            default:
                return options.inverse(this);
        }
    });

    is_sub_comment = false
    if (comment_json.sub_comment_to != null) is_sub_comment = true

    if (document.getElementById('is_theme').value == 'false'){
        del_comment_from_URL_postfix = 'del_comment_from_card'
        edit_comment_URL = 'http://127.0.0.1:8000/storage/edit_card_comment/'

    }else{

        del_comment_from_URL_postfix = 'del_comment_from_theme'
        edit_comment_URL = 'http://127.0.0.1:8000/storage/edit_theme_comment/'

    }

    console.log(edit_comment_URL)

    if (is_sub_comment){
         let comment_HTML = `

            {{#if ${request_user} '==' comment_json.user.pk }}
            <div>
                <div id="del_comment">
                     x
                     <a href='${host}storage/{{comment_json.pk}}/${del_comment_from_URL_postfix}'></a>
                </div>
                <div id="update_comment">
                       @
                       <a href="${edit_comment_URL}${comment_json.pk}"></a>
                </div>
            </div>
            {{/if}}
            {{#if ${request_user} '==' comment_json.user.pk }}
            <div><a href="${host}users/my_profile">{{comment_json.user.username}}</a></div>
            {{/if}}
            {{#if ${request_user} '!=' comment_json.user.pk }}
            <div><a href='${host}users/profile/{{comment_json.user.pk}}'>{{comment_json.user.username}}</a></div>
            {{/if}}
            <div>Ответ на <a href="#{{comment_json.sub_comment_to.pk}}">коментарий</a></div>
            Дорогой, <a href='${host}users/profile/{{comment_json.user.pk}}'>{{comment_json.sub_comment_to.user}}</a>
            <span class="content">{{comment_json.content}}</span>
            <div class="answer_trigger">
                 <input type="hidden" name="comment_pk" value="{{comment.pk}}" >
                 Ответить
            </div>
        `

        let template_comment = Handlebars.compile(comment_HTML);
        let sub_comment_to = `comment_${comment_json.sub_comment_to.pk}`
        let pk = `comment_${comment_json.pk}`
        let div = document.getElementById(sub_comment_to)
        comment.innerHTML = template_comment({comment_json:comment_json})
        div.parentNode.insertBefore(comment, div.nextSibling)

    }else{

        let comment_HTML = `
        {{#if ${request_user} '==' comment_json.user.pk }}
            <div>
                <div id="del_comment">
                     x
                     <a href='${host}storage/{{comment_json.pk}}/${del_comment_from_URL_postfix}'></a>
                </div>
                <div id="update_comment">
                       @
                       <a href="${edit_comment_URL}${comment_json.pk}"></a>
                </div>
            </div>
        {{/if}}
        {{#if ${request_user} '==' comment_json.user.pk }}
        <div><a href="${host}users/my_profile">{{comment_json.user.username}}</a></div>
        {{/if}}
        {{#if ${request_user} '!=' comment_json.user.pk }}
        <div><a href='${host}users/profile/{{comment_json.user.pk}}'>{{comment_json.user.username}}</a></div>
        {{/if}}
        <span class="content">{{comment_json.content}}</span>
        <div class="answer_trigger">
            Ответить
        </div>
    `

    let template_comment = Handlebars.compile(comment_HTML);
    comment.innerHTML = template_comment({comment_json:comment_json})
    document.getElementsByClassName('comments')[0].prepend(comment)
    }
    comment.getElementsByClassName('answer_trigger')[0].onclick = show_add_comment_view
    comment.firstElementChild.firstElementChild.onclick = del_comment
    comment.firstElementChild.lastElementChild.onclick = add_update_comment_view
}
function render_del_comment(data) {

    deleted_comments = data.deleted_objs
    deleted_comment_id = []
    deleted_comments.forEach(function(i){ deleted_comment_id.push(`comment_${i.pk}`)})

    for (i=0; i<deleted_comment_id.length; i++){

        document.getElementById(deleted_comment_id[i]).remove()

    }

}


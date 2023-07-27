let answer_triggers = document.querySelectorAll('.answer_trigger');

const csrf_token = document.getElementById('add_comment').getElementsByTagName('input')[0].value

comment_form = document.getElementById('add_comment')
comment_url = comment_form.action
comment_form_button = comment_form.getElementsByTagName('button')[0]
comment_form_button.addEventListener('click', () => ajax_comment(comment_url, event, comment_form, false))

for (var i = 0; i < answer_triggers.length; ++i) {
    answer_triggers[i].onclick = show_add_comment_view
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


function ajax_comment(url, event, form, is_sub_comment) {
    event.preventDefault()
    let form_data = new FormData(form)

    if (is_sub_comment){

        form.parentNode.removeChild(form)

    }else{

        form.reset()

    }

    fetch(url, {
		method: 'POST',
		body: form_data
	})
	    .then(response => response.json())
	    .then(json => render_comment(json))
};

function render_comment(data){

    let comment_json = JSON.parse(JSON.stringify(data.comment))
    let pk = comment_json.pk
    comment = document.createElement("div")
    comment.className = 'comment'
    comment.id = pk
    let host = 'http://127.0.0.1:8000/'
    let request_user = JSON.parse(JSON.stringify(data.comment.request_user))

    Handlebars.registerHelper('if', function (v1, operator, v2, options) {

        switch (operator) {
            case '==':
                return (v1 == v2) ? options.fn(this) : options.inverse(this);
            case '!=':
            default:
                return options.inverse(this);
        }
    });

    is_sub_comment = false
    if (comment_json.sub_comment_to != null) is_sub_comment = true

    if (is_sub_comment){
         let comment_HTML = `

            {{#if ${request_user} '==' comment_json.user.pk }}
            <div>
                   <a href='${host}storage/{{comment_json.pk}}/del_comment_from_card'>x</a>
                   <a href="">@</a>
            </div>
            {{/if}}
            {{#if ${request_user} '==' comment_json.user.pk }}
            <div><a href="${host}users/my_profile">{{comment_json.user.username}}</a></div>
            {{/if}}
            {{#if ${request_user} '!=' comment_json.user.pk }}
            <div><a href='${host}users/profile/{{comment_json.user.pk}}'>{{comment_json.user.username}}</a></div>
            {{/if}}
            <div>Ответ на <a href="#{{comment_json.sub_comment_to.pk}}">коментарий</a></div>
            Дорогой, <a href='${host}users/profile/{{comment_json.user.pk}}'>{{comment_json.sub_comment_to.user}}</a> {{comment_json.content}}
            <div class="answer_trigger">
                 <input type="hidden" name="comment_pk" value="{{comment.pk}}" >
                 Ответить
            </div>
        `

        let template_comment = Handlebars.compile(comment_HTML);
        let sub_comment_to = comment_json.sub_comment_to.pk
        let pk = comment_json.pk
        let div = document.getElementById(sub_comment_to)
        comment.innerHTML = template_comment({comment_json:comment_json})
        div.parentNode.insertBefore(comment, div.nextSibling)

    }else{

        let comment_HTML = `
        {{#if ${request_user} '==' comment_json.user.pk }}
        <div>
               <a href='${host}storage/{{comment_json.pk}}/del_comment_from_card'>x</a>
               <a href="">@</a>
        </div>
        {{/if}}
        {{#if ${request_user} '==' comment_json.user.pk }}
        <div><a href="${host}users/my_profile">{{comment_json.user.username}}</a></div>
        {{/if}}
        {{#if ${request_user} '!=' comment_json.user.pk }}
        <div><a href='${host}users/profile/{{comment_json.user.pk}}'>{{comment_json.user.username}}</a></div>
        {{/if}}
        {{comment_json.content}}
        <div class="answer_trigger">
            Ответить
        </div>
    `

    let template_comment = Handlebars.compile(comment_HTML);
    comment.innerHTML = template_comment({comment_json:comment_json})
    document.getElementsByClassName('comments')[0].prepend(comment)
    }

    comment.getElementsByClassName('answer_trigger')[0].onclick = show_add_comment_view

}


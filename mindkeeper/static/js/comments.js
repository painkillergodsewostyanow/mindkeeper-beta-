let answer_trigger = document.getElementById('answer_trigger');

answer_trigger.onclick = function(){

    let url = document.getElementById('url').href
    let div = document.getElementById('answer_block')
    let comment_pk = answer_trigger.getElementsByTagName('input')[0].value
    let csrf_token = document.getElementById('add_comment').getElementsByTagName('input')[0].value
    let obj = document.getElementById('add_comment').getElementsByTagName('input')[1].value
    div.innerHTML = `<form action=${url} method='POST'>\
                        <input type='hidden' name='csrfmiddlewaretoken' value=${csrf_token}>\
                        <textarea name='content'></textarea>\
                        <input type='hidden' name='comment' value=${comment_pk}>\
                        <input type='hidden' name='obj' value=${obj}>\
                        <button type='submit'>Ответить</button>\
                    </form>`

};
let answer_triggers = document.querySelectorAll('.answer_trigger');


for (var i = 0; i < answer_triggers.length; ++i) {
    answer_triggers[i].onclick = function(){
        let url = document.getElementById('add_comment_url').href
        let comment_pk = this.getElementsByTagName('input')[0].value
        let csrf_token = document.getElementById('add_comment').getElementsByTagName('input')[0].value
        let obj = document.getElementById('add_comment').getElementsByTagName('input')[1].value
        let div = document.createElement("div");
        div.className = "answer_block"
        div.innerHTML = `
                            <form action=${url} method='POST'>\
                                <input type='hidden' name='csrfmiddlewaretoken' value=${csrf_token}>\
                                <textarea name='content'></textarea>\
                                <input type='hidden' name='comment' value=${comment_pk}>\
                                <input type='hidden' name='obj' value=${obj}>\
                                <button type='submit'>Ответить</button>\
                            </form>
                       `
        this.parentNode.insertBefore(div, this.nextSibling)
    }
}

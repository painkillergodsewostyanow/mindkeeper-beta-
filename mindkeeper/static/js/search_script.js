function ajax_send(url, params) {
	fetch(`${url}?${params}`, {
		method: 'GET',
		headers : {
			'Content-Type': 'application/x-www-form-urlencoded'
		},
	})
	    .then(response => response.json())
	    .then(json => render_search(json))

};


let input = document.getElementById('input_query');

var timer;

input.oninput = function(){
    clearTimeout(timer);
    timer=setTimeout(function(){
         let url = document.getElementById('search_url').href
         let params = `query=${input.value.toString()}`;
         ajax_send(url, params)
      }, 500);
    };


function render_search(data){

    Handlebars.registerHelper('if', function (v1, operator, v2, options) {

        switch (operator) {
            case '==':
                return (v1 == v2) ? options.fn(this) : options.inverse(this);
            case '!=':
                return (v1 != v2) ? options.fn(this) : options.inverse(this);
            default:
                return options.inverse(this);
        }
    });

    let open_profile_URL = "http://127.0.0.1:8000/users/profile/"
    let open_theme_URL = "http://127.0.0.1:8000/storage/theme/"
    let del_theme_URL = "http://127.0.0.1:8000/storage/del_theme/"
    let change_theme_URL = "http://127.0.0.1:8000/storage/change_theme/"
    let open_card_URL = "http://127.0.0.1:8000/storage/card/"
    let del_card_URL = "http://127.0.0.1:8000/storage/del_card/"
    let change_card_URL = "http://127.0.0.1:8000/storage/change_card/"
    let domain = 'http://127.0.0.1:8000/'
    let cards_catalog = document.getElementById('cards_catalog')
    let themes_catalog = document.getElementById('themes_catalog')
    let authors_catalog = document.getElementById('authors_catalog')

    let themes = JSON.parse(JSON.stringify(data.themes))
    let cards = JSON.parse(JSON.stringify(data.cards))


    let theme_label = ""
    let card_label = ""
    let authors_label = ""

        if ('authors' in JSON.parse(JSON.stringify(data))){

        authors = JSON.parse(JSON.stringify(data.authors))

        if (Object.entries(authors).length != 0){
            authors_label = "Авторы: "
        }


    }


    if (Object.entries(themes).length != 0){
        theme_label = "Темы: "
    }
    if (Object.entries(cards).length != 0){
        card_label = "Карточки: "
    }
    if (theme_label === "" && card_label === "" && authors_label === ""){

        document.getElementById('message').innerHTML = "По данному запросу совпадени не найденно";

    }else{

        document.getElementById('message').innerHTML = "";

    }

    let theme_HTML = `
            <div class="label">${theme_label}</div>
            <ul class="catalog_place">
            {{#each themes}}
                        <li class="wrapper">
                        <div class="card">
                        <object>
                            <div id="del_theme" class="del_obj">
                                X
                                <a href="http://127.0.0.1:8000/storage/del_theme/{{this.pk}}"></a>
                            </div>
                        </object>
                        <object>
                                <a id="update_obj" href="http://127.0.0.1:8000/storage/theme/{{this.pk}}/change_theme">@</a>
                        </object>
                        <a href="${open_theme_URL}{{this.pk}}">

                            {{#if this.image '!=' ""}}
                                <div class="photo">
                                    <img src="{{this.image}}" alt="">
                                </div>
                            {{/if}}
                            {{#if this.image '==' ""}}
                            <div class="photo">
                                  <img src="" alt="potom">
                            </div>
                            {{/if}}
                            <p class="object_title">{{this.title}}</p>
                            <span class="views">{{this.views}}</span>
                            <span class="likes">{{this.likes}}</span>
                            <span class="count_comments">{{this.comments}}</span>
                        </div>
                        </a>
                        </li>
                    </ul>
            {{/each}}`

    let card_HTML = `
            <div class="label">${card_label}</div>
            <ul class="catalog_place">
            {{#each cards}}
                        <li class="wrapper">
                        <div class="card">
                        <object>
                            <div id="del_card" class="del_obj">
                                X
                                <a href="storage/del_card/{{this.pk}}"></a>
                            </div>
                        </object>
                        <object>
                                <a href="storage/card/{{ this.pk }}/change_card">@</a>
                        </object>
                        <a href="${open_card_URL}{{this.pk}}">
                            {{#if this.image '!=' ""}}
                                <div class="photo">
                                    <img src="{{this.image}}" alt="">
                                </div>
                            {{/if}}
                            {{#if this.image '==' ""}}
                            <div class="photo">
                                  <img src="" alt="potom">
                            </div>
                            {{/if}}
                            <p class="object_title">{{this.title}}</p>
                            <span class="views">{{this.views}}</span>
                            <span class="likes">{{this.likes}}</span>
                            <span class="count_comments">{{this.comments}}</span>
                        </div>
                        </a>
                        </li>

                    </ul>
            {{/each}}`


    if (authors_catalog) {

        authors_HTML =`
        <div class="label">${authors_label}</div>
        <ul class="catalog_place">
            {{#each authors }}
            <li class="wrapper">
                <a href="${open_profile_URL}{{this.pk}}">
                    <div class="card">
                            {{#if this.image '!=' ""}}
                                <div class="photo">
                                    <img src="{{this.image}}" alt="">
                                </div>
                            {{/if}}
                            {{#if this.image '==' ""}}
                            <div class="photo">
                                  <img src="" alt="potom">
                            </div>
                            {{/if}}
                        <p class="object_title">{{this.username}}</p>
                        <span class="views">{{this.get_user_s_subscribers_count}}</span>
                    </div>
                </a>
            </li>
            {{/each}}
            `

    }

    if (authors_catalog) {
        authors_block = Handlebars.compile(authors_HTML)
    }
    let themes_block = Handlebars.compile(theme_HTML);
    let cards_block = Handlebars.compile(card_HTML);



    themes_catalog.innerHTML = themes_block({themes: themes})
    cards_catalog.innerHTML = cards_block({cards: cards})

    if (authors_catalog){

        authors_catalog.innerHTML = authors_block({authors: authors})

    }
}
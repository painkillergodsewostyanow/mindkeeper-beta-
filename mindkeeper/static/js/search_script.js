function ajax_send(url, params) {
	fetch(`${url}?${params}`, {
		method: 'GET',
		headers : {
			'Content-Type': 'application/x-www-form-urlencoded'
		},
	})
	    .then(response => response.json())
	    .then(json => render_like(json))

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
//       let url = document.getElementById('search_url').href
//       let params = `query=${input.value.toString()}`;
//       ajax_send(url, params)
//};


function render_like(data){

    Handlebars.registerHelper('if', function (v1, operator, v2, options) {

        switch (operator) {
            case '==':
                return (v1 == v2) ? options.fn(this) : options.inverse(this);
            case '!=':
            default:
                return options.inverse(this);
        }
    });

    let open_theme_URL = "http://127.0.0.1:8000/storage/theme/"
    let del_theme_URL = "http://127.0.0.1:8000/storage/del_theme/"
    let change_theme_URL = "http://127.0.0.1:8000/storage/change_theme/"
    let open_card_URL = "http://127.0.0.1:8000/storage/card/"
    let del_card_URL = "http://127.0.0.1:8000/storage/del_card/"
    let change_card_URL = "http://127.0.0.1:8000/storage/change_card/"
    let card_catalog = document.getElementById('card_catalog')
    let theme_catalog = document.getElementById('theme_catalog')

    let themes = JSON.parse(JSON.stringify(data.themes))
    let cards = JSON.parse(JSON.stringify(data.cards))

    let theme_label = ""
    let card_label = ""


    if (Object.entries(themes).length != 0){
        theme_label = "Темы: "
    }
    if (Object.entries(cards).length != 0){
        card_label = "Карточки: "
    }
    if (theme_label === "" && card_label === ""){

        document.getElementById('message').innerHTML = "По данному запросу совпадени не найденно";

    }else{

        document.getElementById('message').innerHTML = "";

    }

    let theme_HTML = `
            <div class="label">${theme_label}</div>
            <ul class="catalog_place">
            {{#each themes}}
                        <li class="wrapper">
                        <a href="${open_theme_URL}{{this.pk}}">
                        <div class="card">
                            <object>
                                <a href="${del_theme_URL}{{this.pk}}" class="cross">X</a>
                            </object>
                             <object>
                                <a href="${change_theme_URL}{{this.pk}}" class="cross">@</a>
                            </object>
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
                        <a href="${open_card_URL}{{this.pk}}">
                        <div class="card">
                            <object>
                                <a href="${del_card_URL}{{this.pk}}" class="cross">X</a>
                            </object>
                             <object>
                                <a href="${change_card_URL}{{this.pk}}" class="cross">@</a>
                            </object>
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


    let themes_block = Handlebars.compile(theme_HTML);
    let cards_block = Handlebars.compile(card_HTML);



    theme_catalog.innerHTML = themes_block({themes: themes})
    card_catalog.innerHTML = cards_block({cards: cards})
}
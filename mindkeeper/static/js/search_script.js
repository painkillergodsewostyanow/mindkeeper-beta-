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

	let url = document.getElementById('search_url').href
	let params = `query=${input.value.toString()}`;
	ajax_send(url, params)

};


function render(data){

    Handlebars.registerHelper('if', function (v1, operator, v2, options) {

        switch (operator) {
            case '==':
                return (v1 == v2) ? options.fn(this) : options.inverse(this);
            case '===':
                return (v1 === v2) ? options.fn(this) : options.inverse(this);
            case '!=':
                return (v1 != v2) ? options.fn(this) : options.inverse(this);
            case '!==':
                return (v1 !== v2) ? options.fn(this) : options.inverse(this);
            case '<':
                return (v1 < v2) ? options.fn(this) : options.inverse(this);
            case '<=':
                return (v1 <= v2) ? options.fn(this) : options.inverse(this);
            case '>':
                return (v1 > v2) ? options.fn(this) : options.inverse(this);
            case '>=':
                return (v1 >= v2) ? options.fn(this) : options.inverse(this);
            case '&&':
                return (v1 && v2) ? options.fn(this) : options.inverse(this);
            case '||':
                return (v1 || v2) ? options.fn(this) : options.inverse(this);
            default:
                return options.inverse(this);
        }
    });

    let catalogs = document.getElementsByClassName('catalog_place')
    let media_URL = '/media/'
    let open_theme_URL = "http://127.0.0.1:8000/storage/theme/"
    let del_theme_URL = "http://127.0.0.1:8000/storage/del_theme/"
    let change_theme_URL = "http://127.0.0.1:8000/storage/change_theme/"
    let open_card_URL = "http://127.0.0.1:8000/storage/card/"
    let del_card_URL = "http://127.0.0.1:8000/storage/del_card/"
    let change_card_URL = "http://127.0.0.1:8000/storage/change_card/"
    let card_catalog = catalogs[1]
    let theme_catalog = catalogs[0]

    let theme_HTML = `
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
                                    <img src="${media_URL}{{this.image}}" alt="">
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
                        </div>
                        </a>
                        </li>
            {{/each}}`
    let card_HTML = `
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
                                    <img src="${media_URL}{{this.image}}" alt="">
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
                        </div>
                        </a>
                        </li>
            {{/each}}`

    let themes = JSON.parse(JSON.stringify(data.themes))
    let cards = JSON.parse(JSON.stringify(data.cards))
    let themes_block = Handlebars.compile(theme_HTML);
    let cards_block = Handlebars.compile(card_HTML);
    theme_catalog.innerHTML = themes_block({themes: themes})
    card_catalog.innerHTML = cards_block({cards: cards})
}
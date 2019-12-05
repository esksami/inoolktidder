# inoolktidder
Tietokantasovellus, 2019


# Kuvaus

Reddit-tyylinen julkinen keskustelufoorumi, jossa kuka tahansa sisään kirjautunut käyttäjä voi luoda postauksia sekä kommentoida niihin ja antaa niille tykkäyksiä. Postaukset näytetään listamuodossa heti etusivulla. Postauksia voi luonnollisesti klikata, jotta saadaan näkyviin niiden sisältö ja niihin luodut kommentit. Kommentteja voi luoda myös vastauksena muihin kommentteihin, jolloin niistä muodostuu esitysmuotonsa ansiosta kommenttiketjuja.


# Heroku-demo

[Tidd3r](https://tidd3r.herokuapp.com/)


# Käyttöohje

- Sovellus toimii lataamalla sovelluksen etusivun, johon postaukset on listattu ja klikkailemalla mieleisiä linkkejä.
- Linkit kirjautumiseen ja rekisteröitymiseen löytyvät oikeasta yläkulmasta.
- Rekisteröityminen vaatii vain uniikin käyttäjänimen sekä salasanan, joista molempien täytyy olla vähintään 3 merkkiä pitkiä.
- Linkki oman postauksen luomiseen on etusivulla, muiden postausten yläpuolella. Tämä toiminnallisuus vaatii oman käyttäjätunnuksen.
- Omia postauksia voi editoida käyttämällä 'edit'-linkkiä etusivulla tai postauksen tarkemmassa näkymässä. Samaten poistaminen onnistuu 'edit'-linkin vieressä olevalla 'delete'-linkillä.
- Kommentin luominen onnistuu kun postauksen tarkempaan näkymään on siirrytty etusivulta. Kommentin tekstikenttä löytyy joko suoraan postauksen alapuolelta tai ilmestyy klikkaamalla 'reply'-linkkiä missä tahansa kommentissa.
- Oman kommentin voi poistaa 'delete'-linkillä
- **Vihje**: kommenttiosioon pääsee nopeammin painamalla etusivulta 'comments'-linkkiä otsikon sijaan.

# Tietokantakaavio

![Tietokantakaavio](documentation/images/Tietokantakaavio.png)


# User storyt

- User can add a post
- User can view all posts
- User can like posts
- User can view content of a post
- User can edit the title and contents of a post


# Testitunnukset

username: hello, password: world
username: test, password: password
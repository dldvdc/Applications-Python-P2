from requests import get

URL = "http://books.toscrape.com"
book_url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

# Récupération de la réponse HTTP à partir de son url
response = get(book_url)

from requests import get
from bs4 import BeautifulSoup as Bs
from datetime import datetime
import re, csv

URL = "http://books.toscrape.com"
book_url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

# Récupération de la réponse HTTP à partir de son url
response = get(book_url)

# Récupération du code HTML dans un objet BeautifulSoup
book_soup = Bs(response.content, "html.parser")

# Scraping du numero UPC
book_upc = book_soup.find("th", string="UPC").next_sibling.text

# Scraping du titre
book_title = book_soup.h1.string

# Scraping du prix avec taxe
price_tax = book_soup.find("th", string="Price (excl. tax)").next_sibling.text
book_price_tax = float(price_tax[1:])

# Scraping du prix hors taxe
price = book_soup.find("th", string="Price (excl. tax)").next_sibling.text
book_price = float(price[1:])

# Scraping du nombre d'exemplaires disponibles
nbr_available = book_soup.find("th", string="Availability").next_sibling.next_sibling.text
book_nbr_a = int(nbr_available.strip("In stock(available)"))

# Scraping du paragraphe de description
try:
    book_description = book_soup.find(id="product_description").next_sibling.next_element.text
except AttributeError:
    book_description = "No description found"

# Scraping de la catégorie
book_category = book_soup.find("a", href=re.compile("^../category/books/")).text

# Scraping de la note globale
rating_values = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
rating_stars = book_soup.find("p", class_=re.compile("^star-rating "))
rating_stars_nbr = rating_stars["class"][1]
book_rating = rating_values[rating_stars_nbr]

# Scraping du lien de l'image
book_img = book_soup.find("img", alt=book_title)
book_img_url = URL + book_img["src"][5:]

# Synthèses des données scrapées
book_data = {"product_page_url": book_url,
             "universal_product_code (upc)": book_upc,
             "title": book_title,
             "price_including_tax": book_price_tax,
             "price_excluding_tax": book_price,
             "number_available": book_nbr_a,
             "product_description": book_description,
             "category": book_category,
             "review_rating": book_rating,
             "image_url": book_img_url}

# Récupération de la date
date = datetime.today().strftime("%m%d%Y")

s_char = "()¨^°*‘«»\"°`#{}[]<>|\\/=~+*%$€?:&#;,"
char = '[%s]+' % re.escape(s_char)
b_name = re.sub(char, '', book_title)
f_name = b_name.title().replace(" ", "_")

# Création du fichier csv
with open(f"{f_name}-BookToScrap-{date}.csv", "w", newline="", encoding="utf-8") as book_csv:

    # Ecriture des entêtes du fichier CSV
    writer = csv.DictWriter(book_csv, fieldnames=book_data.keys())
    writer.writeheader()
    # Ajout des données du livre au fichier CSV

    writer.writerow(book_data)

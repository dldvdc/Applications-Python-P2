from requests import get
from bs4 import BeautifulSoup as Bs
from datetime import datetime
import re
import csv
import os


URL = "http://books.toscrape.com"


# ------------------------------------- FONCTIONS ------------------------------------- #


def url_to_soup(url: str):
    # Récupération de la réponse HTTP à partir de son url
    response = get(url)
    # Récupération du code HTML dans un objet BeautifulSoup
    soup = Bs(response.content, "html.parser")
    return soup


def format_title(title: str) -> str:
    s_char = "()¨^°*‘«»\"°`#{}[]<>|\\/=~+*%$€?:&#;,"
    char = '[%s]+' % re.escape(s_char)
    title = re.sub(char, '', title)
    name = title.title().replace(" ", "_")

    return name


def scrap_book_data(url: str) -> dict:
    # Récupération du code HTML dans un objet BeautifulSoup
    book_soup = url_to_soup(url)

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

    # Enregistrement de l'image dans un dossier categorie
    img_title = format_title(book_title)
    category_title = format_title(book_category)

    os.makedirs(f"output/img/{category_title}", exist_ok=True)

    with open(f"output/img/{category_title}/{img_title}.jpg", 'wb') as img_file:
        response = get(book_img_url)
        img_file.write(response.content)

    # Synthèses des données scrapées
    book_data = {"product_page_url": url,
                 "universal_product_code (upc)": book_upc,
                 "title": book_title,
                 "price_including_tax": book_price_tax,
                 "price_excluding_tax": book_price,
                 "number_available": book_nbr_a,
                 "product_description": book_description,
                 "category": book_category,
                 "review_rating": book_rating,
                 "image_url": book_img_url}

    return book_data


def scrap_category_books_data(category_index_url: str) -> list:
    # Récupération du code HTML
    category_soup = url_to_soup(category_index_url)

    # Scraping du nombre de produits indexés à cette catégorie
    nbr_products = int(category_soup.find_all("strong")[1].text)

    # Détermination du nombre de pages de la catégorie
    nbr_pages = nbr_products // 20

    # Détermination de la racine url commune aux pages catégorie
    url_souche = category_index_url[:-10]

    # Initialisation de la liste des urls de chaque page de la catégorie à partir de son index
    category_urls = [category_index_url]

    # Récupération des urls de chaque page de la catégorie
    for i in range(2, nbr_pages + 2):
        category_urls.append(url_souche + "page-" + str(i) + ".html")

    # Initialisation de la liste de dictionnaires de données des livres scrapés
    category_books_data = []

    # Itération de chaque page de la catégorie
    for category_url in category_urls:

        # Récupération du code HTML
        category_soup = url_to_soup(category_url)

        # Récupération de la liste des livres de la page
        books_blocs = list(category_soup.find_all("article", class_="product_pod"))

        # Récupération des urls de chaque livre dans la page
        for i in range(len(books_blocs)):
            book_url = URL + "/catalogue" + books_blocs[i].find("a")["href"][8:]

            # Récupération des données de chaque livre avec une fonction
            category_books_data.append(scrap_book_data(book_url))

    return category_books_data


def category_data_to_csv(data: list):
    # Récupération de la date
    date = datetime.today().strftime("%m%d%Y")

    # Récupération du nom de la catégorie
    c_name = data[0]["category"]

    # Formatage du titre
    s_char = "()¨^°*‘«»\"°`#{}[]<>|\\/=~+*%$€?:&#;,"
    char = '[%s]+' % re.escape(s_char)
    c_name = re.sub(char, '', c_name)
    f_name = c_name.title().replace(" ", "_")

    # Création du fichier csv
    with open(f"output/csv/{f_name}-BooksToScrap-{date}.csv", "w", newline="", encoding="utf-8") as book_csv:
        # Ecriture des entêtes du fichier CSV
        writer = csv.DictWriter(book_csv, fieldnames=category_data[0].keys())
        writer.writeheader()

        # Ajout des données de chaque livre au fichier CSV
        for book_data in range(len(category_data)):
            writer.writerow(category_data[book_data])


def get_categories_dict(index_url: str) -> list:

    # Récupération du code HTML
    index_soup = url_to_soup(index_url)

    # Scraping du bloc contenant les noms et les urls de la catégorie
    category_bloc = index_soup.find("ul", class_="nav nav-list").find_all("a")

    categories_index = []

    # Récupération des urls de chaque catégorie
    for category in range(1, len(category_bloc)):

        # Récupération des urls de chaque catégorie en tant que valeur
        index = URL + "/" + category_bloc[category]["href"]

        # Synthèse des données
        categories_index.append(index)

    return categories_index


# ------------------------------------- CODE PRINCIPAL -------------------------------------------- #

# Création du dossier output
os.makedirs("output/csv", exist_ok=True)

# Récupération des index de chaque catégorie
categories = get_categories_dict(URL)

for category_index in categories:

    # Récupération des données de tous les livres de chaque catégorie
    category_data = scrap_category_books_data(category_index)

    # Exportation des données de chaque catégorie dans un fichier csv
    category_data_to_csv(category_data)

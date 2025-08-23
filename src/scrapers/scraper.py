import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://google.com"
}


main_url = [
    r'https://www.jumia.com.dz'
]

response = requests.get(main_url[0], headers=headers)

soup = BeautifulSoup(response.content, 'html.parser')

# print(soup.prettify())

links = soup.find('div', class_='flyout').find_all('a')


products_info = []

for link in links:
    span = link.find('span', class_='text')
    href = link.get('href')

    if not span or not href:
        continue

    category_name = span.get_text(strip=True)

    category_url = urljoin(main_url[0], href)

    categories_response = requests.get(category_url, headers=headers)
    category_soup = BeautifulSoup(categories_response.content,'html.parser')
    sub_categories = category_soup.find('div', class_='col4 -me-start -pvs').find_all('a', class_='-db -pvs -phxl -hov-bg-gy05')

    for sub_categorie in sub_categories:
        sub_categorie_url = main_url[0] + sub_categorie['href']
        sub_category_title = sub_categorie.get_text(strip=True)

        # fetch the subcategory page
        sub_categories_response = requests.get(sub_categorie_url, headers=headers)
        sub_categories_soup = BeautifulSoup(sub_categories_response.content, 'html.parser')

        products = sub_categories_soup.find('div', class_='-phs -pvxs row _no-g _4cl-3cm-shs') \
                                    .find_all('article', class_='prd _fb col c-prd')

        for product in products:
            product_url = main_url[0] + product.find('a', class_='core')['href']

            product_urls_response = requests.get(product_url, headers=headers)
            product_soup = BeautifulSoup(product_urls_response.content,'html.parser')

            # product_image = product_soup.find('img', class_='-fw -fh').get("data-src")
            img_tag = product_soup.find('img', class_='-fw -fh')
            product_image = img_tag.get("data-src") if img_tag else (img_tag.get("src") if img_tag else "")
            
            product_name = product_soup.find('h1').get_text(strip=True)

            brand = product_soup.find('a', class_='_more')
            product_brand = brand.get_text(strip=True) if brand else ""

            product_price_after_discount = product_soup.find('span', class_='-b -ubpt -tal -fs24 -prxs')
            product_price_after_discount = product_price_after_discount.get_text(strip=True).split(' ')[0] if product_price_after_discount else ""

            product_price_before_discount = product_soup.find('span', class_='-tal -gy5 -lthr -fs16 -pvxs -ubpt')
            product_price_before_discount = product_price_before_discount.get_text(strip=True).split(' ')[0] if product_price_before_discount else ""

            discount = product_soup.find('span', class_='bdg _dsct _dyn -mls')
            discount = discount.get_text(strip=True)[:-1] if discount else ""

            rating = product_soup.find('div', class_='stars _m _al')
            rating = rating.get_text(strip=True).split(' ')[0] if rating else ""

            product_info = {
                'product_image': product_image,
                'product_name': product_name,
                'product_brand': product_brand,
                'product_price_after_discount': product_price_after_discount,
                'product_price_before_discount': product_price_before_discount,
                'discount': discount,
                'rating': rating,
                'product_url': product_url,
                'category_name':category_name,
                'sub_category_title': sub_category_title 
            }
            products_info.append(product_info)


# insert products_info in a csv file 

# get the keys from the first element
keys = products_info[1].keys()
with open(r"../../data/external/jumia_products.csv", "w", newline="", encoding="utf-8") as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(products_info)
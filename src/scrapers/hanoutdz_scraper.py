import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin



main_url =  r'https://hanoutedz.com'
session = requests.Session()

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"}

response = requests.get(main_url, headers=headers)

soup = BeautifulSoup(response.content, 'html.parser')

links = soup.find('ul', id='menu-verticle-menu').find_all('a')


products_info = []
categories = []


for link in links:
    href = link.get('href')
    if not href:
        continue

    category_url = urljoin(main_url[0], href)
    categories.append(category_url)

    print('category', category_url)
    categories_response = session.get(category_url, headers=headers)
    category_soup = BeautifulSoup(categories_response.content, 'html.parser')

    product_links = category_soup.find_all(
        'a', class_='woocommerce-LoopProduct-link woocommerce-loop-product__link'
    )

    for product in product_links:
        product_url = product.get('href')
        if not product_url:
            continue

        print('product', product_url)
        product_response = session.get(product_url, headers=headers)
        product_soup = BeautifulSoup(product_response.content, 'html.parser')

        # ✅ Handle missing elements safely
        product_image = (
            product_soup.find('div', class_='woocommerce-product-gallery__image')
            .find('a')['href']
            if product_soup.find('div', class_='woocommerce-product-gallery__image')
            else ''
        )

        product_name = (
            product_soup.find('div', class_='content_product_detail')
            .find('h1').get_text(strip=True)
            if product_soup.find('div', class_='content_product_detail')
            else ''
        )

        prices = product_soup.find('p', class_='price')
        prices = prices.find_all('bdi') if prices else []
        product_price_before_discount = (
            prices[0].get_text(strip=True).split("د.ج")[-1] if len(prices) > 0 else ''
        )
        product_price_after_discount = (
            prices[1].get_text(strip=True).split("د.ج")[-1] if len(prices) > 1 else ''
        )

        product_category = (
            product_soup.find('div', class_='item-meta').find('a').get_text(strip=True)
            if product_soup.find('div', class_='item-meta')
            else ''
        )

        product_brand = ''
        desc = product_soup.find('div', id='tab-description')
        if desc:
            desc_lines = desc.get_text(separator="\n", strip=True).split("\n")
            if "Marque:" in desc_lines:
                idx = desc_lines.index("Marque:")
                product_brand = desc_lines[idx + 1] if idx + 1 < len(desc_lines) else ''

        product_info = {
            'product_image': product_image,
            'product_name': product_name,
            'product_brand': product_brand,
            'product_price_after_discount': product_price_after_discount,
            'product_price_before_discount': product_price_before_discount,
            'discount': "",
            'rating': "",
            'product_url': product_url,
            'category_name': product_category,
            'sub_category_title': ""
        }
        products_info.append(product_info)



keys = products_info[1].keys()
with open(r"../../data/external/hanoutdz_products.csv", "w", newline="", encoding="utf-8") as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(products_info)


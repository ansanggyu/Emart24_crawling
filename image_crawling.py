#2024-11-11 14:32
#수정자: 안상규
#설명: 이마트24홈페이지에서 이미지 크롤링
from bs4 import BeautifulSoup
from urllib.request import urlopen

page = 1
#max_page is 134...
max_page = 134

product_list = []

print("Crawling Starting.........................................")

while page <= max_page:
    url = f'https://emart24.co.kr/goods/event?search=&page={page}&category_seq=&align='
    response = urlopen(url)
    soup = BeautifulSoup(response, 'html.parser')

    print(f"\n-------------------------- Page {page} --------------------------\n")

    for item in soup.find_all('div', class_='itemWrap'):

        img_tag = item.find('img')
        img_src = img_tag.get('src', 'non')
        if img_src.startswith('https://'):
            name_tag = item.select_one('.itemtitle a')
            if name_tag:
                product_name = name_tag.get_text(strip=True)

                product = {
                    'img_src': img_src,
                    'product_name': product_name
                }

                product_list.append(product)

    page += 1

file_name = 'product_list.txt'
with open(file_name, 'w', encoding='utf-8') as file:
    for i, product in enumerate(product_list, 1):
        file.write(f"{i}. Image URL: {product['img_src']}\n")
        file.write(f"   Product Name: {product['product_name']}\n")
        file.write("\n")

print(f"Data has been saved to {file_name}.")
#2024-11-11 16:01
#수정자: 안상규
#설명: product_list.txt파일에서 url과 파일명을 지정하여 파일 다운로드
import os
import requests

save_folder = 'Emart24_downloaded_images'

if not os.path.exists(save_folder):
    os.makedirs(save_folder)

failed_downloads_file = os.path.join(save_folder, 'failed_downloads.txt')

with open(failed_downloads_file, 'w', encoding='utf-8') as f:
    f.write("Failed Downloads:\n")

with open('product_list.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

img_url = ""
product_name = ""

for line in lines:
    line = line.strip()
    
    if "Image URL:" in line:
        img_url = line.split('Image URL:')[1].strip()

    elif "Product Name:" in line:
        product_name = line.split('Product Name:')[1].strip()

    if img_url and product_name:
        try:
            response = requests.get(img_url, stream=True)

            if response.status_code == 200:
                safe_product_name = product_name.replace('/', '_').replace(' ', '_').replace(')', '').replace('(', '')

                file_path = os.path.join(save_folder, f"{safe_product_name}.jpg")

                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)

                print(f"Downloaded: {product_name}")
            else:
                print(f"Failed to download: {product_name} (Status Code: {response.status_code})")
                with open(failed_downloads_file, 'a', encoding='utf-8') as f:
                    f.write(f"{product_name} - {img_url}\n")
        except Exception as e:
            print(f"Error downloading {product_name}. Error: {e}")
            with open(failed_downloads_file, 'a', encoding='utf-8') as f:
                f.write(f"{product_name} - {img_url} - Error: {e}\n")

        # 다운로드 후 URL과 제품명 초기화
        img_url = ""
        product_name = ""

    else:
        print("\n")
# 🛒 Emart24 상품 이미지 크롤링

이 프로젝트는 이마트24의 상품 이미지를 자동으로 수집하는 파이썬 기반의 크롤러입니다. 웹 페이지에서 상품 목록을 추출하고, 각 상품의 이미지를 다운로드하여 로컬에 저장합니다.

## 📁 프로젝트 구조

```
Emart24_crawling/
├── image_crawling.py         # 상품 목록 크롤링 및 이미지 URL 추출
├── Download_ImageFIles.py    # 이미지 다운로드 및 저장
├── product_list.txt          # 크롤링된 상품명 목록
├── .gitignore                # Git 무시 파일 설정
```

## ⚙️ 사용 방법

1. **필수 라이브러리 설치**

```bash
pip install requests beautifulsoup4
```

2. **상품 목록 크롤링**

```bash
python image_crawling.py
```

실행 후 `product_list.txt` 파일에 상품 목록이 저장됩니다.

3. **이미지 다운로드**

```bash
python Download_ImageFIles.py
```

실행하면 각 상품의 이미지가 로컬 디렉토리에 저장됩니다.

## 📌 참고 사항

- 크롤링 대상 웹 페이지의 구조가 변경되면 코드 수정이 필요할 수 있습니다.
- 크롤링 시 웹사이트의 이용 약관을 준수하시기 바랍니다.

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 LICENSE 파일을 참고하세요.
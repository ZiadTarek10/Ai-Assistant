import requests
from bs4 import BeautifulSoup

def search_jumia_egypt_product_lowest_prices(product_name):
    search_url = f"https://www.jumia.com.eg/catalog/?q={product_name.replace(' ', '+')}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers'
    }

    print(f"Debug: Fetching URL: {search_url}")  # Debug statement

    try:
        response = requests.get(search_url, headers=headers)
        print(f"Debug: Response status code: {response.status_code}")  # Debug statement
    except Exception as e:
        print(f"Debug: Exception occurred: {e}")
        return []

    if response.status_code != 200:
        print("Failed to retrieve the page.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.find_all('article', {'class': 'prd _fb col c-prd'})

    prices_links = []

    for item in items:
        name_tag = item.find('a', {'class': 'core'})
        price_tag = item.find('div', {'class': 'prc'})
        
        if name_tag and price_tag:
            price_text = price_tag.text.strip().replace(',', '').replace('EGP', '').strip()
            try:
                price = float(price_text)
                link = 'https://www.jumia.com.eg' + name_tag['href']
                prices_links.append((price, link))
                print(f"Debug: Found price {price} with link {link}")  # Debug statement
            except ValueError:
                continue

    prices_links.sort(key=lambda x: x[0])
    
    return prices_links[:5]

def response():
    product_name = input("Enter product name: ")
    print("Results from Jumia in Egypt:")
    results = search_jumia_egypt_product_lowest_prices(product_name)
    for i, (price, link) in enumerate(results, start=1):
        print(f"{i}. Price: EGP {price:.2f}, Link: {link}")

# Call the function
response()

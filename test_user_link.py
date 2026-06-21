import requests
import urllib.parse
from bs4 import BeautifulSoup

def test_user_link():
    college_name = "Government College of Engineering, Amravati"
    query = f"what is the highest package of {college_name}"
    encoded_query = urllib.parse.quote_plus(query)
    
    url = f"https://www.google.com/search?q={encoded_query}&sxsrf=APpeQnuGAsJLOTMtMkmbzZ5xcPt6v6tZ1A%3A1781869766723&udm=50&aep=1&ntc=1&mstk=AUtExfC8uuKi95hbfk3XKxfB4nFajML24LVRBDKYLpgTmvezQrqZwozZXZ6EaxOEjVzEJzMSnp0FMtL_95fXOFX0_vTDcSawQLldQ2nZoiADxYO97eWUTKr8-lFnv4bsx-aem1hYUL4e6UCHUdvmSTMZ--qZjuiGorkM75084lr8_-txOhomQuRhZaO7y9AvUv0ktrJ7GlTvBQayVVjKoWKiVqNc8yo0NylJC74ED8-3Sm3DUG-2ZZyM5YaAbIQFMRmfGCnwuJC5KnqOX45xbKyzo7GzZax8E6B0e3D-KHOiK7St6tf4yL70Ic_ADbUEzvSulC2hvf6PQSkiyg&csuir=1&mtid=yyw1apuMKKyhseMP8pbGmQw"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    resp = requests.get(url, headers=headers)
    print("Status:", resp.status_code)
    
    soup = BeautifulSoup(resp.text, "html.parser")
    print(soup.text[:2000])

if __name__ == "__main__":
    test_user_link()

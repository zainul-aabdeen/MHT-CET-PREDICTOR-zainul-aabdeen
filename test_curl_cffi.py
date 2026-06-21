from curl_cffi import requests
from bs4 import BeautifulSoup
import urllib.parse

def test_curl():
    college_name = "Government College of Engineering, Amravati"
    query = f"what is the highest package of {college_name}"
    encoded_query = urllib.parse.quote_plus(query)
    
    url = f"https://www.google.com/search?q={encoded_query}&sxsrf=APpeQnuGAsJLOTMtMkmbzZ5xcPt6v6tZ1A%3A1781869766723&udm=50&aep=1&ntc=1&mstk=AUtExfC8uuKi95hbfk3XKxfB4nFajML24LVRBDKYLpgTmvezQrqZwozZXZ6EaxOEjVzEJzMSnp0FMtL_95fXOFX0_vTDcSawQLldQ2nZoiADxYO97eWUTKr8-lFnv4bsx-aem1hYUL4e6UCHUdvmSTMZ--qZjuiGorkM75084lr8_-txOhomQuRhZaO7y9AvUv0ktrJ7GlTvBQayVVjKoWKiVqNc8yo0NylJC74ED8-3Sm3DUG-2ZZyM5YaAbIQFMRmfGCnwuJC5KnqOX45xbKyzo7GzZax8E6B0e3D-KHOiK7St6tf4yL70Ic_ADbUEzvSulC2hvf6PQSkiyg&csuir=1&mtid=yyw1apuMKKyhseMP8pbGmQw"
    
    resp = requests.get(url, impersonate="chrome110")
    print("Status code:", resp.status_code)
    
    soup = BeautifulSoup(resp.text, "html.parser")
    print(soup.text[:2000])

if __name__ == "__main__":
    test_curl()

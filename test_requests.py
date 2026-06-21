from googlesearch import search

def test_googlesearch():
    query = "Amravati engineering college highest package"
    print("Searching...")
    try:
        # advanced=True fetches description, URL, and title
        results = search(query, num=3, stop=3, advanced=True)
        for res in results:
            print("Title:", res.title)
            print("URL:", res.url)
            print("Description:", res.description)
            print("-" * 20)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_googlesearch()

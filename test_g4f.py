from g4f.client import Client
import g4f.Provider

def test_g4f():
    providers = [
        g4f.Provider.Blackbox,
        g4f.Provider.DeepInfraChat,
        g4f.Provider.Liaobots,
        g4f.Provider.ChatGptEs,
        None
    ]
    
    for p in providers:
        print("Testing provider:", p)
        try:
            client = Client(provider=p)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Extract JSON: 'Highest is 45 LPA'. Output {"'"highest"'": 45}."}],
            )
            print("Response:", resp.choices[0].message.content)
            break
        except Exception as e:
            print("Failed:", e)

if __name__ == "__main__":
    test_g4f()

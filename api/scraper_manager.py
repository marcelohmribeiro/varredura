import pandas as pd
from pathlib import Path
from src.ingestion.twitter.py import (
    get_replies_from_tweet,
    get_tweets_from_profile,
    get_random_hashtag_tweets,
)from src.ingestion.youtube.py import get_youtube_comments
from src.ingestion.reddit.py import get_reddit_comments

DATA_PATH = Path("data")
DATA_PATH.mkdir(exist_ok=True)

def main():
    print("\n=== Scraper Manager ===")
    print("1 - Twitter")
    print("2 - YouTube")
    print("3 - Reddit\n")

    choice = input("Escolha a fonte (1/2/3): ")

    try:
        limit = int(input("Quantos resultados deseja coletar? (ex: 20): "))
    except ValueError:
        print("⚠️ Valor inválido, usando limite = 50")
        limit = 50

    df = None

    if choice == "1":
        print("\n--- Twitter ---")
        print("1 - Comentários de um tweet específico (link)")
        print("2 - Tweets de um perfil específico")
        print("3 - Tweets de hashtags aleatórias\n")

        sub = input("Escolha a opção (1/2/3): ")

        if sub == "1":
            url = input("Cole o link do tweet: ")
            df = get_replies_from_tweet(url, limit=limit)
        elif sub == "2":
            username = input("Digite o @ do perfil (sem @): ")
            df = get_tweets_from_profile(username, limit=limit)
        elif sub == "3":
            df = get_random_hashtag_tweets(limit=limit)

    elif choice == "2":
        print("\n--- YouTube ---")
        url = input("Cole o link do vídeo: ")
        df = get_youtube_comments(url, limit=limit)

    elif choice == "3":
        print("\n--- Reddit ---")
        url = input("Cole o link do post: ")
        df = get_reddit_comments(url, limit=limit)

    else:
        print("❌ Fonte inválida!")
        return

    if df is not None:
        print("\n✅ Resultados coletados:")
        print(df.head())

        salvar = input("\nDeseja salvar em CSV local? (s/n): ")
        if salvar.lower() == "s":
            filename = f"{df['source'].iloc[0]}_resultado.csv"
            df.to_csv(DATA_PATH / filename, index=False, encoding="utf-8")
            print(f"📁 Arquivo salvo em data/{filename}")

if __name__ == "__main__":
    main()

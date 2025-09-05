import os
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
from pathlib import Path
import argparse


def shorten_link(access_token, original_url):
    api_url = "https://api.vk.com/method/utils.getShortLink"
    params = {
        "url": original_url,
        "access_token": access_token,
        "v": "5.199"
    }
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        raise RuntimeError(data["error"].get("error_msg", "Unknown error"))
    return data["response"]["short_url"]


def count_clicks(access_token, short_url_key):
    api_url = "https://api.vk.com/method.utils.getLinkStats"
    params = {
        "key": short_url_key,
        "interval": "day",
        "intervals_count": 100,
        "access_token": access_token,
        "v": "5.199"
    }
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        raise RuntimeError(data["error"].get("error_msg", "Unknown error"))
    return sum(day["views"] for day in data["response"]["stats"])


def is_valid_vk_short_link(access_token, short_url_key):
    api_url = "https://api.vk.com/method/utils.getLinkStats"
    params = {
        "key": short_url_key,
        "access_token": access_token,
        "v": "5.199"
    }
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        return False
    return "response" in data


def is_shortened_vk_link(access_token, url):
    parsed = urlparse(url)
    short_url_key = parsed.path.lstrip('/')
    return parsed.netloc.lower() == "vk.cc" and len(short_url_key) > 0 and is_valid_vk_short_link(access_token, short_url_key)


def main():
    # Явно загружаем .env из директории скрипта
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)

    access_token = os.getenv("VK_ACCESS_TOKEN")
    if not access_token:
        raise RuntimeError("VK_ACCESS_TOKEN не найден! Проверь файл .env или переменные окружения.")

    parser = argparse.ArgumentParser(description="VK link shortener and click counter")
    parser.add_argument("url", help="URL для обработки: сокращение или подсчет кликов по VK ссылке")
    args = parser.parse_args()

    user_url = args.url.strip()

    try:
        if is_shortened_vk_link(access_token, user_url):
            key = urlparse(user_url).path.lstrip('/')
            clicks = count_clicks(access_token, key)
            print(clicks)
        else:
            short_url = shorten_link(access_token, user_url)
            print(short_url)
    except requests.exceptions.RequestException as e:
        print("Ошибка запроса:", e)
    except RuntimeError as e:
        print("Ошибка:", e)
    except Exception as e:
        print("Другая ошибка:", e)


if __name__ == "__main__":
    main()

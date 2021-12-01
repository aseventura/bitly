import os
import requests
from requests.models import HTTPError
from urllib.parse import urlparse
import argparse
from dotenv import load_dotenv
load_dotenv()


def parse_url_into_components(users_url: str):
    parse_result = urlparse(users_url)
    return parse_result.netloc + parse_result.path


def get_shorten_link(bitly_access_token: str, template_url: str, users_url: str) -> str:
    headers = {
        'Authorization': f'Bearer {bitly_access_token}',
    }
    body = {
        'long_url': users_url,
    }
    url = f'{template_url}shorten'
    response = requests.post(url=url,
                            json=body,
                            headers=headers)
    response.raise_for_status()
    bitlink_info = response.json()
    return bitlink_info['id']


def get_count_clicks(bitly_access_token: str, template_url: str, users_url: str) -> int:
    headers = {
        'Authorization': f'Bearer {bitly_access_token}'
    }
    payload = {
        'units': '-1',
    }
    bitlink_without_scheme = parse_url_into_components(users_url)
    url = f'{template_url}bitlinks/{bitlink_without_scheme}/clicks/summary'
    response = requests.get(url=url,
                            params=payload,
                            headers=headers)
    response.raise_for_status()
    clicks_count = response.json()['total_clicks']
    return clicks_count


def is_bitlink(bitly_access_token: str, template_url: str, users_url: str):
    headers = {
        'Authorization': f'Bearer {bitly_access_token}',
    }
    url_without_scheme = parse_url_into_components(users_url)
    url = f'{template_url}bitlinks/{url_without_scheme}'
    response = requests.get(url=url,
                            headers=headers)
    return response.ok


def get_parse_params():
    parser = argparse.ArgumentParser(
        description='Программа для сокращения введённых ссылок и подсчёта количества кликов'
        )
    parser.add_argument('url', nargs='+', help='URL-адреса, которые хотите сократить или проверить по ним количество кликов')
    return parser.parse_args().url


def main():
    BITLY_ACCESS_TOKEN = os.getenv('BITLY_ACCESS_TOKEN')
    template_url = 'https://api-ssl.bitly.com/v4/'
    users_url = get_parse_params()
    for url in users_url:
        try:
            if is_bitlink(BITLY_ACCESS_TOKEN, template_url, url):
                print(f'По вашей ссылке {url} прошли:', get_count_clicks(BITLY_ACCESS_TOKEN, template_url, url), 'раз(а)')
            else:
                print(f'Битлинк для ссылки {url} -', get_shorten_link(BITLY_ACCESS_TOKEN, template_url, url))
        except HTTPError:
            print('Некорректный адрес URL. Ссылка должна начинаться c протокола HTTP: https://URL, либо http://URL')


if __name__ == '__main__':
    main()
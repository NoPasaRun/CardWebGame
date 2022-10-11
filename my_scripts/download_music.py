from threading import Thread
from bs4 import BeautifulSoup as Soup
from requests import session


class Parser:
    def __init__(self, url):
        self.url = url
        self.session = session()

    def get_data(self, *args, **kwargs):
        response = self.session.get(self.url)
        music_links = self.parse_links(response.content, *args, **kwargs)
        return music_links

    @staticmethod
    def parse_links(str_data, _class=None):
        soup = Soup(str_data, features="html.parser")
        parsed_links = [link.get("href") for link in soup.find_all(attrs={"class": _class}) if link.get("href")]
        return parsed_links


def download_ans_save_music(download_link):
    ses = session()
    response = ses.get(download_link)
    file_name: str = download_link.split("/")[-1]
    if file_name.endswith(".mp3"):
        with open(f"music/{file_name}", "wb") as file:
            file.write(response.content)


if __name__ == '__main__':
    parser = Parser(url="https://ru.hitmotop.com/album/697048")
    links = parser.get_data(_class="track__download-btn")
    threads = [Thread(target=download_ans_save_music, args=(link,)) for link in links]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

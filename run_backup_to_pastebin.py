import configparser
import datetime
import os
import time

import requests
from bs4 import BeautifulSoup

from run_backup import RedditWikiBackup


class PastebinConfig:
    FILEPATH = 'pastebin.ini'
    SECTION = 'pastebin'


class PastebinConfigOption:
    DATE_FORMAT = 'date_format'
    KEEP_DAYS = 'keep_days'


class PbApiUrl:
    API_POST = 'https://pastebin.com/api/api_post.php'


class PbApiOption:
    PASTE = 'paste'
    LIST = 'list'
    DELETE = 'delete'


class PbApiPastePrivacy:
    PUBLIC = 0
    UNLISTED = 1
    PRIVATE = 2


class PastebinApi:
    def __init__(self) -> None:
        self.config = None
        self._creds = None
        self._session = None

    def read_config(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(PastebinConfig.FILEPATH)
        return

    def load_creds(self) -> None:
        self._creds = dict(api_dev_key=os.environ['PASTEBIN_DEV_KEY'], api_user_key=os.environ['PASTEBIN_USER_KEY'])
        return

    def open_session(self) -> None:
        self._session = requests.Session()
        return

    def create_new_paste_as_user(self, title: str, text: str) -> None:
        response = self._session.post(PbApiUrl.API_POST, data=dict(
            api_paste_name=title, api_paste_code=text, api_option=PbApiOption.PASTE,
            api_paste_private=PbApiPastePrivacy.PRIVATE, **self._creds,
        ))
        assert response.ok
        time.sleep(1)
        return

    def list_pastes_of_user(self) -> list:
        response = self._session.post(PbApiUrl.API_POST, data=dict(api_option=PbApiOption.LIST, **self._creds))
        assert response.ok
        time.sleep(1)
        pastes = BeautifulSoup(response.text, 'lxml').select('paste')
        return pastes

    def delete_paste(self, paste_key: str) -> None:
        response = self._session.post(PbApiUrl.API_POST, data=dict(
            api_paste_key=paste_key, api_option=PbApiOption.DELETE, **self._creds))
        assert response.ok
        time.sleep(1)
        return

    def delete_historic_pastes(self, pastes: list) -> None:
        keep_days = self.config.getint(PastebinConfig.SECTION, PastebinConfigOption.KEEP_DAYS)
        cutoff_date = datetime.date.today() - datetime.timedelta(days=keep_days)
        for paste in pastes:
            paste_date = datetime.date.fromtimestamp(int(paste.find('paste_date').text))
            if paste_date < cutoff_date:
                self.delete_paste(paste.find('paste_key').text)
        return


class RedditWikiBackupToPastebin(RedditWikiBackup):
    def run_backup(self) -> None:
        self._read_config()
        self._create_reddit_instance()
        self._create_pastebin_session()
        self._download_subreddit_wikis()
        self._clean_pastebin_history()
        return

    def _create_pastebin_session(self) -> None:
        self._pastebin = PastebinApi()
        self._pastebin.read_config()
        self._pastebin.load_creds()
        self._pastebin.open_session()
        return

    def _clean_pastebin_history(self) -> None:
        self._pastebin.delete_historic_pastes(self._pastebin.list_pastes_of_user())
        return

    def _download_one_subreddit_wiki(self, subreddit_name: str) -> None:
        subreddit = self._reddit.subreddit(subreddit_name)
        subreddit_wiki = subreddit.wiki
        today_str = datetime.date.today().strftime('%Y-%m-%d')

        try:
            os.mkdir(subreddit.display_name)
        except FileExistsError:
            pass

        for page_name in self._get_page_names(subreddit_name):
            page_content = subreddit_wiki[page_name].content_md
            filename = page_name.replace('/', '.')
            filepath = f'{subreddit.display_name}/{filename}.md'
            with open(filepath, 'w', encoding='utf8') as f:
                f.write(page_content)

            self._pastebin.create_new_paste_as_user(f'{filename}_{today_str}.md', open(
                filepath, encoding='utf8').read())
            time.sleep(1)

        return


if __name__ == '__main__':
    RedditWikiBackupToPastebin().run_backup()

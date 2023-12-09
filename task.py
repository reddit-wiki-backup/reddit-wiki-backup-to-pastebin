import configparser
import os

import praw


class RedditWikiBackup:
    def __init__(self) -> None:
        self._reddit = None
        self._config = None

    def run_backup(self) -> None:
        self._read_config()
        self._create_reddit_instance()
        self._download_subreddit_wikis()
        return

    def _download_subreddit_wikis(self) -> None:
        subreddit_names = list(self._config.keys())
        subreddit_names.remove(self._config.default_section)
        [self._download_one_subreddit_wiki(subreddit_name) for subreddit_name in subreddit_names]
        return

    def _read_config(self) -> None:
        self._config = configparser.ConfigParser()
        self._config.read('subreddits.ini')
        return

    def _create_reddit_instance(self) -> None:
        if self._reddit:
            return

        username = os.environ['USERNAME']
        self._reddit = praw.Reddit(
            client_id=os.environ['CLIENT_ID'],
            client_secret=os.environ['CLIENT_SECRET'],
            password=os.environ['PASSWORD'],
            user_agent=f'Backup subreddit wiki(s) on behalf of u/{username}',
            username=username,
        )
        return

    def _download_one_subreddit_wiki(self, subreddit_name: str) -> None:
        subreddit = self._reddit.subreddit(subreddit_name)
        subreddit_wiki = subreddit.wiki

        os.mkdir(subreddit.display_name)

        for page_name in self._get_page_names(subreddit_name):
            page_content = subreddit_wiki[page_name].content_md
            filename = page_name.replace('/', '.')
            with open(f'{subreddit.display_name}/{filename}.md', 'w', encoding='utf8') as f:
                f.write(page_content)

        return

    def _get_page_names(self, subreddit_name: str) -> list:
        page_names = self._reddit.get(f'/r/{subreddit_name}/wiki/pages/')['data']
        subreddit_section = self._config[subreddit_name]
        if not subreddit_section.getboolean('include_config_pages'):
            page_names = list(filter(lambda x: not x.startswith('config/'), page_names))
        return page_names


if __name__ == '__main__':
    RedditWikiBackup().run_backup()

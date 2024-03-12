import configparser
import os

import praw

_TASK_CONFIG_FILEPATH = 'subreddits.ini'
_WIKI_CONFIG_PAGES = ('config/', 'automoderator/')


class TaskConfigKeys:
    INCLUDE_CONFIG_PAGES = 'include_config_pages'
    INCLUDE_ONLY_PAGES = 'include_only_pages'
    EXCLUDE_PAGES = 'exclude_pages'


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
        self._config.read(_TASK_CONFIG_FILEPATH)
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

        try:
            os.mkdir(subreddit.display_name)
        except FileExistsError:
            pass

        for page_name in self._get_page_names(subreddit_name):
            page_content = subreddit_wiki[page_name].content_md
            filename = page_name.replace('/', '.')
            with open(f'{subreddit.display_name}/{filename}.md', 'w', encoding='utf8') as f:
                f.write(page_content)

        return

    def _get_page_names(self, subreddit_name: str) -> set:
        page_names = set(self._reddit.get(f'/r/{subreddit_name}/wiki/pages/')['data'])

        if not self._config.getboolean(subreddit_name, TaskConfigKeys.INCLUDE_CONFIG_PAGES):
            page_names = set(filter(lambda x: not x.startswith(_WIKI_CONFIG_PAGES), page_names))

        if pages_to_include := self._config.get(subreddit_name, TaskConfigKeys.INCLUDE_ONLY_PAGES):
            page_names = set(pages_to_include.split()).intersection(page_names)

        if pages_to_exclude := self._config.get(subreddit_name, TaskConfigKeys.EXCLUDE_PAGES):
            page_names = page_names.difference(set(pages_to_exclude.split()))

        return page_names


if __name__ == '__main__':
    RedditWikiBackup().run_backup()

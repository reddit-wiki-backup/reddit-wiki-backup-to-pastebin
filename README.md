# reddit-wiki-backup-template

## Perform regular or one-time backups of subreddit wikis

## How to Use

To set this up for subreddit(s) of your choice:

* Fork this repo.
* Authorize your Reddit account:
  * Follow the instructions [here](https://np.reddit.com/r/RequestABot/comments/cyll80/a_comprehensive_guide_to_running_your_reddit_bot/) under the **OAuth** section.
* (On GitHub) Go to Settings > Secrets > Actions (`https://github.com/YOUR_USERNAME/reddit-wiki-backup/settings/secrets/actions`) and add the following repository secrets:
  * `CLIENT_ID`
  * `CLIENT_SECRET`
  * `USERNAME`
  * `PASSWORD`
* In `subreddits.ini`, add entries for the subreddits whose wikis you want to back up.
  * The file contains examples.
  * You can only back up wiki pages that are visible to the authorized account.
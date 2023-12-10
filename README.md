# reddit-wiki-backup-template

## Perform regular or one-time backups of subreddit wikis

## How to Use

To set this up for subreddit(s) of your choice:

* Fork this repo.
* Authorize your Reddit account:
  * Follow the instructions [here](https://np.reddit.com/r/RequestABot/comments/cyll80/a_comprehensive_guide_to_running_your_reddit_bot/) under the **OAuth** section.
* In GitHub repository settings, go to Settings > Secrets > Actions and add the following repository secrets:
  * `CLIENT_ID`
  * `CLIENT_SECRET`
  * `USERNAME`
  * `PASSWORD`
* In `subreddits.ini`, add entries for the subreddits whose wikis you want to back up.
  * The file contains examples.
  * You can only back up wiki pages that are visible to the authorized account.
* Run the backup:
  * Run one-time backup: In GitHub repository, go to Actions > Run Backup > Run Workflow > Run Workflow
  * Schedule regular backup: In GitHub repository, go to [RunBackup.yml schedule lines](/.github/workflows/RunBackup.yml#L5). Uncomment these two lines.

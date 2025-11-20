"""
Tweet Scraper Module
Automatic tweet and replies scraping using tweet-harvest
"""

import pandas as pd
import subprocess
import os
import json
from typing import Dict, List, Optional
from pathlib import Path
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TweetScraper:
    """Class untuk scraping tweets dan replies menggunakan tweet-harvest"""

    def __init__(self, data_path: str = "/home/dimas/crawling_sosmed/tweets-data"):
        """
        Initialize TweetScraper

        Args:
            data_path: Path ke folder data
        """
        self.data_path = data_path
        self.tweet_file = f"{data_path}/tweet.xlsx"
        self.all_replies_file = f"{data_path}/replies.csv"

        # Load environment variables
        self.auth_token = os.getenv('TWITTER_AUTH_TOKEN', '')

        # Load scraping limits from env
        self.high_engagement_threshold = int(os.getenv('HIGH_ENGAGEMENT_THRESHOLD', 1000))
        self.high_engagement_limit = int(os.getenv('HIGH_ENGAGEMENT_LIMIT', 200))
        self.medium_engagement_threshold = int(os.getenv('MEDIUM_ENGAGEMENT_THRESHOLD', 500))
        self.medium_engagement_limit = int(os.getenv('MEDIUM_ENGAGEMENT_LIMIT', 150))
        self.low_engagement_limit = int(os.getenv('LOW_ENGAGEMENT_LIMIT', 50))

        # Create data directory if not exists
        os.makedirs(data_path, exist_ok=True)

    def check_data_exists(self) -> Dict[str, bool]:
        """
        Check apakah file data sudah ada

        Returns:
            Dictionary dengan status file
        """
        return {
            'tweet_xlsx_exists': os.path.exists(self.tweet_file),
            'all_replies_exists': os.path.exists(self.all_replies_file),
            'data_ready': os.path.exists(self.tweet_file) and os.path.exists(self.all_replies_file)
        }

    def calculate_dynamic_limit(self, likes: int, retweets: int) -> int:
        """
        Calculate dynamic limit based on engagement (likes + retweets)

        Args:
            likes: Number of likes
            retweets: Number of retweets

        Returns:
            Limit for replies to scrape
        """
        total_engagement = likes + retweets

        if total_engagement >= self.high_engagement_threshold:
            return self.high_engagement_limit
        elif total_engagement >= self.medium_engagement_threshold:
            return self.medium_engagement_limit
        else:
            return self.low_engagement_limit

    def check_nodejs_installed(self) -> bool:
        """Check apakah Node.js sudah terinstall"""
        try:
            result = subprocess.run(
                ['node', '-v'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def install_nodejs(self) -> Dict[str, any]:
        """
        Install Node.js jika belum ada

        Returns:
            Dictionary dengan status instalasi
        """
        try:
            print("Installing Node.js...")

            # Update apt
            subprocess.run(['apt-get', 'update'], check=True, timeout=300)

            # Install dependencies
            subprocess.run(
                ['apt-get', 'install', '-y', 'ca-certificates', 'curl', 'gnupg'],
                check=True,
                timeout=300
            )

            # Create keyrings directory
            subprocess.run(['mkdir', '-p', '/etc/apt/keyrings'], check=True)

            # Add NodeSource GPG key
            subprocess.run(
                'curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg',
                shell=True,
                check=True,
                timeout=60
            )

            # Add NodeSource repository
            subprocess.run(
                'echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list',
                shell=True,
                check=True
            )

            # Update apt again
            subprocess.run(['apt-get', 'update'], check=True, timeout=300)

            # Install Node.js
            subprocess.run(['apt-get', 'install', 'nodejs', '-y'], check=True, timeout=300)

            # Install Playwright dependencies
            subprocess.run(
                ['apt-get', 'install', '-y', 'libatk1.0-0', 'libatk-bridge2.0-0',
                 'libatspi2.0-0', 'libxcomposite1'],
                check=True,
                timeout=300
            )

            # Install Playwright
            subprocess.run(['npx', 'playwright', 'install-deps'], check=True, timeout=600)

            return {
                'success': True,
                'message': 'Node.js installed successfully'
            }

        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'message': f'Installation failed: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }

    def scrape_single_tweet_replies(
        self,
        conversation_id: str,
        auth_token: str,
        output_filename: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, any]:
        """
        Scrape replies dari single tweet

        Args:
            conversation_id: ID dari conversation (id_str dari tweet)
            auth_token: Twitter auth token
            output_filename: Nama file output (optional)
            limit: Limit jumlah replies yang diambil

        Returns:
            Dictionary dengan status scraping
        """
        try:
            if output_filename is None:
                output_filename = f"{self.data_path}/{conversation_id}_replies.csv"

            # Build command
            command = [
                'npx', '-y', 'tweet-harvest@2.6.1',
                '-o', output_filename,
                '-s', f'conversation_id:{conversation_id}',
                '--token', auth_token,
                '--limit', str(limit)
            ]

            print(f"Scraping replies for conversation {conversation_id}...")

            # Run scraping
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )

            if result.returncode == 0:
                # Check if file was created
                if os.path.exists(output_filename):
                    # Read to get count
                    df = pd.read_csv(output_filename)
                    return {
                        'success': True,
                        'conversation_id': conversation_id,
                        'output_file': output_filename,
                        'replies_count': len(df),
                        'message': f'Successfully scraped {len(df)} replies'
                    }
                else:
                    return {
                        'success': False,
                        'conversation_id': conversation_id,
                        'message': 'Scraping completed but file not found'
                    }
            else:
                return {
                    'success': False,
                    'conversation_id': conversation_id,
                    'message': f'Scraping failed: {result.stderr}'
                }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'conversation_id': conversation_id,
                'message': 'Scraping timeout (>10 minutes)'
            }
        except Exception as e:
            return {
                'success': False,
                'conversation_id': conversation_id,
                'message': f'Error: {str(e)}'
            }

    def scrape_all_tweets_replies(self) -> Dict[str, any]:
        """
        Scrape replies untuk semua tweets dari tweet.xlsx
        Uses auth token from .env and dynamic limit per post based on engagement

        Returns:
            Dictionary dengan hasil scraping
        """
        try:
            # Check if tweet.xlsx exists
            if not os.path.exists(self.tweet_file):
                return {
                    'success': False,
                    'message': f'tweet.xlsx not found at {self.tweet_file}'
                }

            # Read tweet.xlsx
            df_tweets = pd.read_excel(self.tweet_file, header=4)

            # Validate required columns
            required_columns = ['Permalink']
            missing_columns = [col for col in required_columns if col not in df_tweets.columns]
            if missing_columns:
                return {
                    'success': False,
                    'message': f'Missing columns in tweet.xlsx: {", ".join(missing_columns)}'
                }

            print(f"Found {len(df_tweets)} tweets to scrape")

            # Results tracking
            results = []
            all_replies_dfs = []

            # Scrape each tweet with dynamic limit
            for idx, row in df_tweets.iterrows():
                # Extract tweet ID from Permalink
                # Format: https://www.twitter.com/USER_ID/status/TWEET_ID
                permalink = str(row['Permalink'])
                conv_id = permalink.split('/status/')[-1] if '/status/' in permalink else None

                if not conv_id:
                    print(f"\n[{idx+1}/{len(df_tweets)}] Skipping - invalid permalink: {permalink}")
                    continue

                # Get Replies count from tweet data (actual reply count from Twitter)
                reply_count = int(row['Replies']) if 'Replies' in df_tweets.columns and pd.notna(row['Replies']) else 0

                # Get engagement data for fallback calculation
                likes = int(row['Likes']) if 'Likes' in df_tweets.columns and pd.notna(row['Likes']) else 0
                retweets = int(row['Retweets']) if 'Retweets' in df_tweets.columns and pd.notna(row['Retweets']) else 0

                # Calculate limit:
                # 1. If reply_count > 0, use reply_count + 10 (to ensure we get all replies)
                # 2. Otherwise, use dynamic limit based on engagement (likes + retweets)
                if reply_count > 0:
                    limit = reply_count + 10
                    print(f"\n[{idx+1}/{len(df_tweets)}] Processing conversation {conv_id}...")
                    print(f"  Replies count: {reply_count}")
                    print(f"  Limit: {limit} (reply_count + 10)")
                else:
                    limit = self.calculate_dynamic_limit(likes, retweets)
                    print(f"\n[{idx+1}/{len(df_tweets)}] Processing conversation {conv_id}...")
                    print(f"  Engagement: {likes} likes + {retweets} retweets = {likes + retweets}")
                    print(f"  Dynamic limit: {limit} replies")

                result = self.scrape_single_tweet_replies(
                    conversation_id=conv_id,
                    auth_token=self.auth_token,
                    limit=limit
                )

                results.append(result)

                # If successful, add to all_replies
                if result['success'] and os.path.exists(result['output_file']):
                    try:
                        df_reply = pd.read_csv(result['output_file'])
                        # Add reply_to_tweet_id column to track which tweet this reply belongs to
                        df_reply['reply_to_tweet_id'] = conv_id
                        all_replies_dfs.append(df_reply)
                    except Exception as e:
                        print(f"Error reading {result['output_file']}: {e}")

                # Sleep to avoid rate limiting
                if idx < len(df_tweets) - 1:
                    time.sleep(2)

            # Combine all replies into one file
            if all_replies_dfs:
                df_all_replies = pd.concat(all_replies_dfs, ignore_index=True)
                df_all_replies.to_csv(self.all_replies_file, index=False)

                total_replies = len(df_all_replies)
                successful_scrapes = sum(1 for r in results if r['success'])

                return {
                    'success': True,
                    'total_tweets': len(df_tweets),
                    'successful_scrapes': successful_scrapes,
                    'total_replies': total_replies,
                    'output_file': self.all_replies_file,
                    'message': f'Successfully scraped {total_replies} replies from {successful_scrapes}/{len(df_tweets)} tweets',
                    'details': results
                }
            else:
                return {
                    'success': False,
                    'message': 'No replies were scraped successfully',
                    'details': results
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error during scraping: {str(e)}'
            }

    def initialize_platform_data(self) -> Dict[str, any]:
        """
        Initialize platform dengan scraping data jika belum ada
        Uses auth token from .env and dynamic limit per post

        Returns:
            Dictionary dengan status initialization
        """
        # Check data status
        data_status = self.check_data_exists()

        # If replies.csv already exists, skip scraping
        if data_status['all_replies_exists']:
            return {
                'success': True,
                'message': 'replies.csv already exists, no scraping needed',
                'data_status': data_status,
                'scraping_needed': False,
                'skipped': True
            }

        if data_status['data_ready']:
            return {
                'success': True,
                'message': 'Data already exists, platform ready',
                'data_status': data_status,
                'scraping_needed': False
            }

        # Check if tweet.xlsx exists
        if not data_status['tweet_xlsx_exists']:
            return {
                'success': False,
                'message': 'tweet.xlsx not found. Please upload tweet.xlsx first.',
                'data_status': data_status,
                'scraping_needed': False
            }

        # Check if auth token is configured
        if not self.auth_token:
            return {
                'success': False,
                'message': 'TWITTER_AUTH_TOKEN not found in .env file. Please configure it first.',
                'data_status': data_status,
                'scraping_needed': False
            }

        # Check Node.js
        if not self.check_nodejs_installed():
            print("Node.js not found, installing...")
            install_result = self.install_nodejs()
            if not install_result['success']:
                return {
                    'success': False,
                    'message': f'Node.js installation failed: {install_result["message"]}',
                    'data_status': data_status,
                    'scraping_needed': True
                }

        # Scrape all replies
        print("Starting scraping process...")
        scrape_result = self.scrape_all_tweets_replies()

        if scrape_result['success']:
            return {
                'success': True,
                'message': 'Platform initialized successfully',
                'data_status': self.check_data_exists(),
                'scraping_result': scrape_result,
                'scraping_needed': True
            }
        else:
            return {
                'success': False,
                'message': f'Scraping failed: {scrape_result["message"]}',
                'data_status': data_status,
                'scraping_result': scrape_result,
                'scraping_needed': True
            }

    def get_scraping_status(self) -> Dict[str, any]:
        """
        Get status dari scraping process

        Returns:
            Dictionary dengan status lengkap
        """
        data_status = self.check_data_exists()
        nodejs_installed = self.check_nodejs_installed()

        # Get file stats if exists
        file_stats = {}
        if data_status['tweet_xlsx_exists']:
            try:
                df_tweets = pd.read_excel(self.tweet_file, header=4)
                file_stats['total_tweets'] = len(df_tweets)
            except Exception:
                file_stats['total_tweets'] = None

        if data_status['all_replies_exists']:
            try:
                df_replies = pd.read_csv(self.all_replies_file)
                file_stats['total_replies'] = len(df_replies)
            except Exception:
                file_stats['total_replies'] = None

        return {
            'data_ready': data_status['data_ready'],
            'tweet_xlsx_exists': data_status['tweet_xlsx_exists'],
            'all_replies_exists': data_status['all_replies_exists'],
            'nodejs_installed': nodejs_installed,
            'file_stats': file_stats,
            'data_path': self.data_path
        }

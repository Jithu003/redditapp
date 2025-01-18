import praw
import requests
import schedule
import time
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(filename="reddit_bot.log", level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize Reddit API
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent="RedditBot by u/" + os.getenv("REDDIT_USERNAME")
)

# Generate content using Groq AI
def generate_content():
    groq_api_url = "https://api.groq.com/v1/generate"  # Replace with the actual endpoint
    headers = {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"}
    payload = {"prompt": "Generate a daily motivational Reddit post"}
    try:
        response = requests.post(groq_api_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise error for bad responses
        return response.json().get("content", "Default content: AI failed to generate.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Groq API error: {e}")
        return "Error generating content."

# Post to Reddit
def post_to_reddit():
    subreddit_name = "test"  # Replace with your target subreddit
    content = generate_content()
    try:
        reddit.subreddit(subreddit_name).submit("Daily AI Post", selftext=content)
        logging.info(f"Post submitted to r/{subreddit_name}")
    except Exception as e:
        logging.error(f"Reddit post error: {e}")

# Comment on Reddit posts
def comment_on_posts():
    subreddit = reddit.subreddit("test")  # Replace with your target subreddit
    for submission in subreddit.hot(limit=5):
        try:
            comment_content = generate_content()
            submission.reply(comment_content)
            logging.info(f"Commented on post: {submission.title}")
        except Exception as e:
            logging.error(f"Error commenting: {e}")

# Schedule tasks
schedule.every().day.at("10:00").do(post_to_reddit)
schedule.every().day.at("12:00").do(comment_on_posts)

if __name__ == "__main__":
    logging.info("Reddit bot started.")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Wait 60 seconds before checking again

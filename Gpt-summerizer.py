import feedparser
import os
import requests
import openai
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

# OpenAI credentials
openai.api_key = "YOUR_API_KEY"

# Email credentials
email_address = "YOUR_EMAIL_ADDRESS"
email_password = "YOUR_EMAIL_PASSWORD"

# RSS feed URL
feed_url = "https://techcommunity.microsoft.com/plugins/custom/microsoft/o365/custom-blog-rss?tid=-2665027495767423092&board=MicrosoftEndpointManagerBlog&size=25"

# Check for new posts
feed = feedparser.parse(feed_url)
latest_post = feed.entries[0]
with open("latest_post.txt", "r+") as file:
    latest_post_saved = file.read()
    if latest_post_saved != latest_post.link:
        # Extract text from new post link using Beautiful Soup
        response = requests.get(latest_post.link)
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.find("div", attrs={"id": "bodydisplay"}).get_text()

        # Get summary of text using OpenAI API
        summary = openai.Completion.create(
            engine="text-davinci-002",
            prompt=text,
            max_tokens=60,
            n=1,
            stop=None,
            temperature=0.5
        ).choices[0].text

        # Compose email with summary
        message = MIMEText(summary)
        message["Subject"] = latest_post.title
        message["From"] = email_address
        message["To"] = email_address

        # Send email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.sendmail(email_address, email_address, message.as_string())

        # Update latest post saved
        file.seek(0)
        file.write(latest_post.link)
        file.truncate()

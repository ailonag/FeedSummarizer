import feedparser
import os
import requests
import openai
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

# OpenAI credentials
openai.api_key = "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"

# Email credentials
email_address = "ailona@ailona.com"
email_password = "J@ckL0rdistough"
email_toaddress = "erichgellert@gmail.com"

# RSS feed URL
feed_url = "https://techcommunity.microsoft.com/plugins/custom/microsoft/o365/custom-blog-rss?tid=-2665027495767423092&board=MicrosoftEndpointManagerBlog&size=25"

# Check for new posts
feed = feedparser.parse(feed_url)
latest_post = feed.entries[4]
with open("lastpost.txt", "r+") as file:
    latest_post_saved = file.read()
    if latest_post_saved != latest_post.link:
        # Extract text from new post link using Beautiful Soup
        response = requests.get(latest_post.link)
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.find("div", attrs={"class": "lia-message-body"}).get_text()
        

        try:
            summary = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Please summarize this for a second-grade student:\n{text}\n\nSummary:",
                temperature=0.7,
                max_tokens=64,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
                ).choices[0].text
        except Exception as e:
            print("Error generating summary:", e)
            summary = "Error generating summary"

         # Compose email with summary and link
        message_body = f"{summary}\n\n{latest_post.link}"
        message = MIMEText(message_body)
        message["Subject"] = latest_post.title
        message["From"] = email_address
        message["To"] = "erichgellert@gmail.com, ergeller@microsoft.com, russ.rimmerman@microsoft.com"
        

        # Send email
        with smtplib.SMTP("10.0.0.67", 587) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.sendmail(email_address, email_toaddress, message.as_string())

        # Update latest post saved
        file.seek(0)
        file.write(latest_post.link)
        file.truncate()


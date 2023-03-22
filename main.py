import feedparser
import os
import requests
import openai
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup


try:
    G_SECRET = os.environ["G_SECRET"]
except KeyError:
    G_SECRET = "Token not available!"
try:
    O_SECRET = os.environ["OPENAI_SECRET"]
except KeyError:
    O_SECRET = "Token not available!"

# OpenAI credentials
openai.api_key = O_SECRET

# Email credentials
email_address = "erichgellert@gmail.com"
email_password = G_SECRET
email_toaddress = "erich.gellert@microsoft.com"

# RSS feed URL
feed_url = "https://techcommunity.microsoft.com/plugins/custom/microsoft/o365/custom-blog-rss?tid=-2665027495767423092&board=MicrosoftEndpointManagerBlog&size=25"

# Check for new posts
feed = feedparser.parse(feed_url)
latest_post = feed.entries[0]
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
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.sendmail(email_address, email_toaddress, message.as_string())

        # Update latest post saved
        file.seek(0)
        file.write(latest_post.link)
        file.truncate()


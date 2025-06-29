import logging
from livekit.agents import function_tool, RunContext
import requests
from langchain_community.tools import DuckDuckGoSearchRun
import os
import smtplib
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText
from typing import Optional
from datetime import datetime
import pytz
import feedparser

@function_tool()
async def getweather(
    context: RunContext,  # type: ignore
    city: str) -> str:
    """
    Get the current weather for a given city.
    """
    try:
        response = requests.get(
            f"https://wttr.in/{city}?format=3")
        if response.status_code == 200:
            logging.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()   
        else:
            logging.error(f"Failed to get weather for {city}: {response.status_code}")
            return f"Could not retrieve weather for {city}."
    except Exception as e:
        logging.error(f"Error retrieving weather for {city}: {e}")
        return f"An error occurred while retrieving weather for {city}." 

@function_tool()
async def searchweb(
    context: RunContext,  # type: ignore
    query: str) -> str:
    """
    Search the web using DuckDuckGo.
    """
    try:
        results = DuckDuckGoSearchRun().run(tool_input=query)
        logging.info(f"Search results for '{query}': {results}")
        return results
    except Exception as e:
        logging.error(f"Error searching the web for '{query}': {e}")
        return f"An error occurred while searching the web for '{query}'."    

@function_tool()    
async def sendemail(
    context: RunContext,  # type: ignore
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[str] = None
) -> str:
    """
    Send an email through Gmail.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        message: Email body content
        cc_email: Optional CC email address
    """
    try:
        # Gmail SMTP configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Get credentials from environment variables
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")  # Use App Password, not regular password
        
        if not gmail_user or not gmail_password:
            logging.error("Gmail credentials not found in environment variables")
            return "Email sending failed: Gmail credentials not configured."
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add CC if provided
        recipients = [to_email]
        if cc_email:
            msg['Cc'] = cc_email
            recipients.append(cc_email)
        
        # Attach message body
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS encryption
        server.login(gmail_user, gmail_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(gmail_user, recipients, text)
        server.quit()
        
        logging.info(f"Email sent successfully to {to_email}")
        return f"Email sent successfully to {to_email}"
        
    except smtplib.SMTPAuthenticationError:
        logging.error("Gmail authentication failed")
        return "Email sending failed: Authentication error. Please check your Gmail credentials."
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return f"Email sending failed: SMTP error - {str(e)}"
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return f"An error occurred while sending email: {str(e)}"

@function_tool()
async def gettimeincountry(
    context: RunContext,  # type: ignore
    country: str) -> str:
    """
    Get the current date and time for a specified country.
    
    Args:
        country: The name of the country or its timezone.
    """
    try:
        # Get the timezone for the country
        timezone = pytz.timezone(country)
        current_time = datetime.now(timezone)
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"Current time in {country}: {formatted_time}")
        return f"The current date and time in {country} is: {formatted_time}"
    except pytz.UnknownTimeZoneError:
        logging.error(f"Unknown timezone: {country}")
        return f"Could not retrieve time for {country}: Unknown timezone."
    except Exception as e:
        logging.error(f"Error retrieving time for {country}: {e}")
        return f"An error occurred while retrieving time for {country}."





@function_tool()
async def getjoke(context: RunContext) -> str:
       """
       Fetch a random joke.
       """
       try:
           response = requests.get("https://official-joke-api.appspot.com/random_joke")
           if response.status_code == 200:
               joke = response.json()
               return f"{joke['setup']} - {joke['punchline']}"
           else:
               return "Failed to retrieve a joke."
       except Exception as e:
           return f"An error occurred: {str(e)}"
   



@function_tool()
async def getnewsheadlines(
    context: RunContext,  # type: ignore
    source: str = "bbc") -> str:
    """
    Fetch news headlines from RSS feeds of major news sources.
    
    Args:
        source: News source (bbc, cnn, reuters, techcrunch)
    """
    try:
        rss_feeds = {
            "bbc": "http://feeds.bbci.co.uk/news/rss.xml",
            "cnn": "http://rss.cnn.com/rss/cnn_topstories.rss",
            "reuters": "http://feeds.reuters.com/reuters/topNews",
            "techcrunch": "http://feeds.feedburner.com/TechCrunch/"
        }
        
        if source not in rss_feeds:
            return f"Invalid source. Available options: {', '.join(rss_feeds.keys())}"
            
        feed = feedparser.parse(rss_feeds[source])
        headlines = [f"{entry.title} ({source.upper()})" for entry in feed.entries[:5]]
        return f"Latest headlines from {source.upper()}:\n" + "\n".join(headlines)
    except Exception as e:
        return f"An error occurred while fetching news: {str(e)}"


@function_tool()
async def getstockprice(
    context: RunContext,  # type: ignore
    stock_symbol: str) -> str:
    """
    Get the current stock price for a given stock symbol using the Alpha Vantage API.
    
    Args:
        stock_symbol: The stock symbol (e.g., 'AAPL' for Apple).
    """
    try:
        api_key = "1WKLBUHQSE9FRK1T"  # Replace with your Alpha Vantage key
        response = requests.get(f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock_symbol}&apikey={api_key}")
        if response.status_code == 200:
            data = response.json().get('Global Quote', {})
            price = data.get('05. price', 'N/A')
            return f"The current price of {stock_symbol} is: ${price}"
        else:
            return f"Failed to retrieve stock price: {response.status_code}"
    except Exception as e:
        return f"An error occurred while retrieving stock price: {str(e)}"



@function_tool()
async def getrandomquote(context: RunContext) -> str:
    """
    Fetch a random inspirational quote using the Quotable API.
    """
    try:
        response = requests.get("https://api.quotable.io/random")
        if response.status_code == 200:
            quote = response.json()
            return f"{quote['content']} - {quote['author']}"
        else:
            return "Failed to retrieve a quote."
    except Exception as e:
        return f"An error occurred: {str(e)}"


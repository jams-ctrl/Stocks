# Stocks
Hello! My name is James, and this is my rendition of a stock bot made with the goal of attending Horizons Polaris! I am totally new to hack club, so forgive me if there are some issues with my github - I had to switch folders midway through because I did not know how to merge :(.<br>

Motivation:<br>
At the start of summer, I made the hard decision to refuse my full-time job offer as a summer camp counsellor in favour of a learning-centered summer. My summer is now very full with sports, math, and friends, but coding takes up most of my time, and I have devoted all that time to this project.
I have always been interested in stocks, a seemingly get-rich-quick method, and with the AI-boom, I wondered if I could use neural networks and their self-learning aspect to be trained on stock data.
Aside from wanting to be a millionare, I also had the idea to incorporate news into the website, given how powerful authortative figures seem to govern our world (and drastically sway stocks) in this time and day. 
Therefore, I create a user interface with the end goal of allowing users to search up any stock in the S&P 500 (Now changed to the top 100 + 50 tech companies) and get a detailed description and summary about the current stock outlook and surroudning news, with the goal of helping to inform people's decisions when buying/selling an important stock.<br>

Description: <br>
Upon entering a stock into the search box, the user will be greeted with the verdict from the company-based AI model (to be expanded on), and outputs from news sources such as CNBC, Yahoo Entertainment, and 24/7 Wall Street (courtesy of news api), as well as SEC filings and posts from a reddit-like stock forum, StockTwits. Under each of these sources are a list of articles with the title, date, and short shapshot of body text, followed by a link, with the user can click on if interested, sending them to the exact page the article is on.<br>
The user can then click the right-arrow navigation button to take them to the news panel, a news hotspot where the user can access over 10 different news sources to inform their decision on the stock, and is able to click on each box to expand it

How-It-Works: <br>
AI model: 
The confidence rating is how confident the model is on the stock's future movement/trend. Any chance above 40% is considered "high", and any chance below 30% is considered "low".
The model uses a combination of given stock features such as dates, volumes, and closing prices, and calculated features like returns, moving averages, volatilities, and volume changes to form a csv of the stock dating back 5 years. 
Then, a sequential tensorflow model with 3 dense layers is used to train the model given labels "buy", "sell", and "hold" over 50 iterations and saves a unique model to each company<br>

Top-right (News) box: <br>
Does a newsAPI call per ticker and adds the results to a grand sqlite3 database titled "mentions.db" including rows 
    ticker
    source_type
    source_name
    author
    external_id 
    url 
    title
    text 
    published_at
    fetched_at 
    raw_json 
    follower_count
    UNIQUE(source_type, external_id)
To keep track of authority/authenticity as well as the date, url, title, and other key aspects of the article. Then uses these key aspects and cuts to body paragraph to a reader-friendly version which is displayed on the html page.<br>

Bottom-right(SMedia) box: <br>
Uses edgar API and logs it in the above database before showing a summarized version to the reader
Uses stocktwits API and logs it in the database about before showing a summarized verion to the reader<br>

News Panel: <br>
Capitalizing on the idea of news dicating the stock market, I sought to increase the amount of sources with the addition of the news panel. 8 Boxes are arranged in a gridlike fashion, <br>
each containing its own news source, with a description and capability to expand and retract the view frame on-click. I took some liberties on adding a graph and table for the <br>
google trends and insider trades respectively, and with the help of claude for the graph, and my experience for the table, I am happy with how they turned out. I had to additionally incorporate the API for these elements into my code, yielding the creation of finnhub_scraper and serpapi_scraper which grants me access to this data. <br> Finnhub is really nice!

Tech Stack:<br>
Frontend: HTML, CSS, Javascript <br>
Backend: Flask, Jinja, Python <br>
Database & Data-handling: Python, Sqlite3 <br>

AI use: 
Asked Claude ~30 questions concerning debugging,how to write complex functions like compute_z_score, using html to create the google trends graph, and generating ticker lists, but all of the code is handwritten. 

Hope you enjoy interacting with my project! Please do not hesitate to contact me!

Screenshots:
<img width="1470" height="796" alt="Screenshot 2026-07-28 at 3 53 50 PM" src="https://github.com/user-attachments/assets/ac37363a-f2ca-44f1-8a05-0860062b6a6d" />
<img width="1470" height="799" alt="Screenshot 2026-07-28 at 3 52 39 PM" src="https://github.com/user-attachments/assets/ce718003-a015-4efa-b17f-6d0131388ba7" />
<img width="1470" height="799" alt="Screenshot 2026-07-28 at 3 52 39 PM" src="https://github.com/user-attachments/assets/2c625254-49f1-439c-9d0b-5d39c6bba64c" />

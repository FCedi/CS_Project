# Sources

This file contains citations and references for the external tools and resources used in the development of our app.
Throughout the creation and testing of the application's code, we relied on external documentation, tutorials, and open-source tools to guide our implementation.
Additionally, we downloaded/scraped data to build and train a rental price estimation model using a Random Forest Regressor.

### Data

We used the Google Chrome extension "[Instant Data Scraper](https://chromewebstore.google.com/detail/instant-data-scraper/ofaokhiedipichpaobibbnahnkdoiiah?pli=1)" to scrape information about apartments in Geneve, Lausanne, St. Gallen and Zurich from [RealAdvisor.ch](https://realadvisor.ch/de/immobilien-mieten). In total we collected around 500 apartment listings from each city, 2000 aapartments in total.
We used the collected data to train our estimation model after converting the collected data into CSV files with our Conversion csv.py program and then creating the price_estimator.pkl and model_diagnostics.pkl with our train_model_all_cities.py.

The price_estimator.pkl is used for our price estimation and the model_diagnostics.pkl is used to genetate the diagram which compares the collected rents versus the rent from the user. 

### Pictures and Graphics 

All Graphics we use are created from the the collected data, no external diagrams or pictures are used.


# Sources

This file contains citations and references for the external tools and resources used in the development of our app.
Throughout the creation and testing of the application's code, we relied on external documentation, tutorials, and open-source tools to guide our implementation.
Additionally, we downloaded/scraped data to build and train a rental price estimation model using a Random Forest Regressor.

## Data

We used the Google Chrome extension "[Instant Data Scraper](https://chromewebstore.google.com/detail/instant-data-scraper/ofaokhiedipichpaobibbnahnkdoiiah?pli=1)" to scrape information about apartments in Geneve, Lausanne, St. Gallen and Zurich from [RealAdvisor.ch](https://realadvisor.ch/de/immobilien-mieten). In total we collected around 450 apartment listings from each city, 1800 aapartments in total.
We used the collected data to train our estimation model after converting the collected data into CSV files with our Conversion csv.py program and then creating the price_estimator.pkl and model_diagnostics.pkl with our train_model_all_cities.py.

The price_estimator.pkl is used for our price estimation and the model_diagnostics.pkl is used to genetate the diagram which compares the collected rents versus the rent from the user. 

## Pictures and Graphics 

All Graphics we use are created from the the collected data, no external diagrams or pictures are used.

## ChatGPT

For certain problems we asked ChatGPT for help, these where the cases we used it and what code implementations it lead to:
- Fair_Rental_Price_Evaluator.py
    - "when I submit the form and am directed to the result page, the results only show for a second and then start to "flicker". How can I prevent this?"
        -> Led to the implementation of `st.session_state.xy` to save the entered values when swithcing between pages
    - 
- Specific_Amenities_Finder.py
- train_model_all_cities.py
- Conversion csv.py
    - After filtering the scraped data (.xlsx files) by hand to have the information we needed to enter it in our training model it didn't work as we excepted. Because there where around 1800 lines of code to filter, we aked ChatGPT to write us a program to filter the .xlsx files and provide a cleaned up CSV file. We provided ChatGPT with the format we needed the CSV to be so we could enter it in our training model.
    In short, ChatGPT build Conversion csv.py based on the format we needed the CSV files to be for our training model.

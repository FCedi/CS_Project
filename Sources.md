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
        -> Led to the implementation of `st.session_state.` to save the entered values when swithcing between pages
    - 
- Specific_Amenities_Finder.py
    - 
- train_model_all_cities.py
    - As we wanted to detect different price influencing features in ceveral columns of the csv files, we asked ChatGPT to defin us a function to look for different keywords in defined columns. We asked: "Write a python function to search for different keyword groups in the rows char.1, char.2 and char.3" From this we got a custom function we integrated in our code. We could define different keywords (`xy_keywords`) and replace `keywords` when recaling the function to detect for these keywords in the defined rows
    ```
    def detect_feature(row, keywords):
        values = [str(row['char.1']).lower(), str(row['char.2']).lower(), str(row['char.3']).lower()]
        return int(any(any(k in v for k in keywords) for v in values))
    ```
    - After runing into problems when feeding our csv files into the RandomForrestRegressor because of unknown values, we entered the issue into ChatGPT. after some more inputs we got this function from ChatGPT to put before the RandomForrestRegressor avoid the error of unknown values
    ````
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['place_type'])
        ],
        remainder='passthrough'
    )
    ```
- Conversion csv.py
    - After filtering the scraped data (.xlsx files) by hand to have the information we needed to enter it in our training model it didn't work as we excepted. Because there where around 1800 lines of code to filter, we aked ChatGPT to write us a program to filter the .xlsx files and provide a cleaned up CSV file. We provided ChatGPT with the format we needed the CSV to be so we could enter it in our training model.
    In short, ChatGPT build Conversion csv.py based on the format we needed the CSV files to be for our training model.
    - Certain elements of the Conversion csv program where reused in other parts of our project, these elements include:
        - `str.extract(r'(?:(\d+(?:\.\d+)?)\s*rooms?)?\s*•?\s*(\d+)\s*m²\s*•?\s*(.*)')` and `str.extract(r'^(.*),\s*(\d{4}\s+\w+.*)$')` to extract different elements conected to room number and size and also differnt address elements
        - `str.replace(r'[^\d.]', '', regex=True)` and `str.replace(r'\s+', ' ', regex=True)` to replace anything unwanted in a single cell

## Other Sources

- train_model_all_cities.py
    - To correctly implement the RandomForrestRegressor, we used the guide from [geeksforgeeks.org](https://www.geeksforgeeks.org/random-forest-regression-in-python/). this heled us to use the correct Parameters.
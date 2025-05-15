# Fair Rental Price Evaluator

This is the CS Project of Group 07.10

This app gives you an overview if your rent is comparable to other available apartments in **Geneva, Zürich, Lausanne, or St. Gallen** according to key indicators such as size (m²), number of rooms, location (evaluated by Zip Code), outdoor space, if it's renovated/new and if there is a parking opportunity included. It also enables you to locate key amenities around your new potential flat, and calculates the distance to spesific amenities of your choice such as a new workplace or your university. Our app uses machine learning based on historical rental listings to predict a rent range (±10%) for the entered apartment.

## Key Features

- A trained rent estimation model trained with ~1.800 listings from 4 cities (~450 each)
- Inclusion of different features to estimate rent:
  - Location (Zip Code)
  - Apartment Size (in m²)
  - Number of Rooms
  - Outdoor Space
  - Renovated/New
  - Parking Availability
- A bar plot comparing the annual price per m² from the entered apartment and the zip code of the entered apartment is in.
- A scatter plot displaying the entered apartment and the 100 outcomes of our Random Forest Regression and the ideal prediction line.
- A comparable rent estimation (±10%) for the entered apartment.
- Visual map of the property location with selected amenities in a defined radius around the entered apartment.
- A tool to see the distance between specific amenities such as a place of work or university

## Requirements to Open, Run or Expand our App

### Open the App

Open our app through this [link](https://fairrentalpriceevaluator.streamlit.app). Here the app is hosted on one of our devices.

### Run the App

Download the CS_Projects-07.10.zip file or clone the github repository through accessing the app through the link above and install it on your local device and run the streamlit app from there.
To make sure the app can run on your local device, make sure the `requirements.txt` are installed before opening/creating the local streamlit app.

### Expand our App

If you collected more data to train our model and want to include it in our `price_estimator.pkl` and `model_diagnostics.pkl`, you have everything at your disposal to do so. There is just one requirement, you need the scraped data as an .xlsx file, otherwise our `Conversion csv.py` program won't work.

#### 1. Make the Correct CSV Files

Run your .xlsx file through our `Conversion csv.py` program to receive a csv file which is structured in a way our other programs can gather the correct data. For this you need to change the input and output file (Ln 5 and 6) in the `Conversion csv.py` program.

#### 2. Create new .pkl Files

First you need to delete the current `price_estimator.pkl` and `model_diagnostics.pkl` files to make room for the new ones. After this, you need to add the name of the new training csv file to `city_files = [`HERE`]`(Ln 12) in the `train_model_all_cities.py` program without removing any of the current files.

Afterwards you need to instal the `requirements.txt` file on your device before running the `train_model_all_cities.py` on your local device to create new and improved versions of the `price_estimator.pkl` and `model_diagnostics.pkl` files.

#### 3. Run the Streamlit App

Once you created the new `price_estimator.pkl` and `model_diagnostics.pkl` files and saved them in the same place as the other files you can reboot or create a new version of the streamlit app using this `Fair_Rental_Price_Evaluator.py` file as the main file path. `Fair_Rental_Price_Evaluator.py` will automatically use the new `price_estimator.pkl` and `model_diagnostics.pkl` files, there is no requirement to change any code.

## Limitations

Due to the limited experience and knowledge in coding, our app has it's limitations. Some of them are because we use free API's, which despite using a timer and user-agent to access them, there are still limitations with requests in a short amount of time from the same IP address.

Another  limitation we encountered was related to the spesific amenities finder page. The sometimes there is an issue with the address text fields, as in the german letter ä, ö and ü work and sometimes they don't. Even the adaptations, ae, oe and ue don't work for the address.

A very obvious limitation is the amount of data the model is trained with. Currentls we use ~450 rent listings from Geneve, Lausann, St. Gallen and Zurich. There are ways to get and use more data, but for the scope of this project ~1800 listings is enough.
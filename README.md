# Swiss Real Estate Price Estimator

This is the CS Project of Group 07.10

This app gives you an overview if your rent is comparable to other available apartments in **Geneva, Zürich, Lausanne, or St. Gallen** according to key indicators such as size (m²), number of rooms, location (evaluated by Zip Code), outdoor space, if it's renovated/new and if there is a prking opportunity included. It also enables you to locate key amenities around your new potential flat, and calculates the distance to a key points of your choice such as a new place of workplace or your university. Our app uses machine learning based on historical rental listings to predict a rent range (+- 10%) for the entered apartment.

## Key Features

- A trained rent estimation model traind with ~1.800 listings from 4 cities (~450 each)
- Inclusion of different features to estimate rent:
  - Location (Zip Code)
  - Apartment Size (in m²)
  - Number of Rooms
  - Outdoor Space
  - Renovated/New
  - Parking Availability
- A bar plot comparing the annual price per m² from the entered apartment and the zip code our aparment is in.
- A scatter plot displaying the entered apartment and the 100 outcomes of our RandomForrestRegression and the ideal prediction line.
- A comparable rent estimation (±10%) for the entered apartment.
- Visual map of the property location with selected amenities in a defined radius around the entered apartment.
- A tool to see the distance beteween a selected amenities such as a place of work or university

## Requirements to open, run or expand our program

### Prerequisites

- Python 3.8+ recommended
- Pip (Python package installer)

### 1. Clone or download the project

```bash
git clone <your-repository-url>
cd CS_Project-07.10
```

### 2. Install required Python packages

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

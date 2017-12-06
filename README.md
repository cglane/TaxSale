Implementation of webparsing and machine learning techniques to predict outcomes for taxsales in Charleston County.


## How To
- git clone https://github.com/cglane/taxsale.git
- source virt/bin/activate
- pip install -r requirements.txt
- python manage.py runserver
- http://localhost:8000/

## Tools

- Django
- BeautifulSoup
- Mechanize
- Pandas
- Support Vector Machine(SVM)
- Naive Bayes
- Decision Trees


## Creating Databases

- Queries Charleston County Governmax website based on property PIN
- Queries https://api.census.gov/ for property location and census tract demographic information
- Queries https://maps.googleapis.com/maps/api/geocode/ for location if census location finder fails

## UI

- Django template displaying potential fields and algorithms for training data
- Returns stats about results (false positives, true positives, etc.)

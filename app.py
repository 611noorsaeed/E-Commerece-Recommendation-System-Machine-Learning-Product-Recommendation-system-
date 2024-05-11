from flask import Flask, render_template
import pandas as pd
import random
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np
import pickle

# create app======================================================================================================
app = Flask(__name__)
pipe = pickle.load(open('models/pipe.pkl','rb'))

# database configuration---------------------------------------
app.secret_key = "Secret Key"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/ProductDB"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Define your model class for the 'signup' table
class Signup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Define your model class for the 'signup' table
class Signin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)


# load files===========================================================================================================
trending_products = pd.read_csv("models/trending_products.csv")
train_data = pd.read_csv("models/clean_data.csv")


# Recommendations functions============================================================================================
# Function to truncate product name
def truncate(text, length):
    if len(text) > length:
        return text[:length] + "..."
    else:
        return text

def content_based_recommendations(train_data, item_name, top_n=10):
    # Check if the item name exists in the training data
    if item_name not in train_data['Name'].values:
        return pd.DataFrame()  # Return an empty DataFrame if the item is not found

    # Create a TF-IDF vectorizer for item descriptions
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')

    # Apply TF-IDF vectorization to item descriptions
    tfidf_matrix_content = tfidf_vectorizer.fit_transform(train_data['Tags'])

    # Calculate cosine similarity between items based on descriptions
    cosine_similarities_content = linear_kernel(tfidf_matrix_content, tfidf_matrix_content)

    # Find the index of the item
    item_index = train_data[train_data['Name'] == item_name].index[0]

    # Get the cosine similarity scores for the item
    similar_items = list(enumerate(cosine_similarities_content[item_index]))

    # Sort similar items by similarity score in descending order
    similar_items = sorted(similar_items, key=lambda x: x[1], reverse=True)

    # Get the top N most similar items (excluding the item itself)
    top_similar_items = similar_items[1:top_n + 1]

    # Get the indices of the top similar items
    recommended_item_indices = [x[0] for x in top_similar_items]

    # Get the details of the top similar items
    recommended_items_details = train_data.iloc[recommended_item_indices][['Name', 'ReviewCount', 'Brand', 'ImageURL', 'Rating']]

    return recommended_items_details


def pred(custid, prodcategory, prodprice, quantity, totalamount, paymentmethod, custage, returns, age, gender,
         purchaseyear, purchasemonth, purchaseday, purchasehour):
    # Once preprocessing is done, create a feature vector
    feature_vector = [custid, prodcategory, prodprice, quantity, totalamount, paymentmethod, custage, returns, age,
                      gender, purchaseyear, purchasemonth, purchaseday, purchasehour]

    # Make prediction using your model
    prediction = pipe.predict([feature_vector])

    # You can return the prediction
    return prediction[0]

# routes================================================================================================================
# List of predefined image URLs
random_image_urls = [
    "static/img/img_1.png",
    "static/img/img_2.png",
    "static/img/img_3.png",
    "static/img/img_4.png",
    "static/img/img_5.png",
    "static/img/img_6.png",
    "static/img/img_7.png",
    "static/img/img_8.png",
]
# List of prices
prices = [40, 50, 150, 70, 100, 200, 106, 100]

# def is_signed_in():
#     return Signin.query.first() is not None
#
#
# def is_signed_up():
#     return Signup.query.first() is not None
#
# def last_added_signup():
#     return Signup.query.order_by(Signup.id.desc()).first()
#
#
# def last_added_signin():
#     return Signin.query.order_by(Signin.id.desc()).first()


@app.route('/')
def index():
    # Create a list of random image URLs for each product
    random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
    price = [40,50,60,70,100,122,106,50,30,50]
    return render_template('index.html', trending_products=trending_products.head(8), truncate=truncate,
                           random_product_image_urls=random_product_image_urls, random_price = random.choice(prices))

@app.route('/main')
def main():
    return render_template('main.html')


@app.route('/index')
def index1():
    # Create a list of random image URLs for each product
    random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
    print(trending_products)
    price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
    return render_template('index.html', trending_products=trending_products.head(8), truncate=truncate,
                           random_product_image_urls=random_product_image_urls, random_price=random.choice(prices))

# Route for signup page
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        new_signup = Signup(username=username, email=email,password=password)
        db.session.add(new_signup)
        db.session.commit()

        # Create a list of random image URLs for each product
        random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
        print(trending_products)
        price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
        return render_template('index.html', trending_products=trending_products.head(8), truncate=truncate,
                               random_product_image_urls=random_product_image_urls, random_price=random.choice(prices),
                               signup_message='User signed up successfully!'
                               )

# Route for signup page
@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if request.method == 'POST':
        username = request.form['signinUsername']
        password = request.form['signinPassword']
        new_signup = Signin(username=username,password=password)
        db.session.add(new_signup)
        db.session.commit()

        # Create a list of random image URLs for each product
        random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
        price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
        return render_template('index.html', trending_products=trending_products.head(8), truncate=truncate,
                               random_product_image_urls=random_product_image_urls, random_price=random.choice(prices),
                               signup_message='User signed in successfully!'
                               )


@app.route("/recommendations", methods=['POST', 'GET'])
def recommendations():
    if request.method == 'POST':
        prod = request.form.get('prod')
        nbr = int(request.form.get('nbr'))
        content_based_rec = content_based_recommendations(train_data, prod, top_n=nbr)
        if content_based_rec.empty:
            message = "No recommendations available for this product."
            return render_template('main.html', message=message)
        else:
            # Create a list of random image URLs for each recommended product
            random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
            print(content_based_rec)
            print(random_product_image_urls)

            price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
            return render_template('main.html', content_based_rec=content_based_rec, truncate=truncate,
                                   random_product_image_urls=random_product_image_urls, random_price=random.choice(price))

# python main===========================================================================================================
if __name__ == '__main__':
    app.run(debug=True)

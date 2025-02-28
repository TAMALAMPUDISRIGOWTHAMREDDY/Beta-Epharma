import joblib
import mysql.connector
import requests
from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure key

# Load the trained model
model = joblib.load('model.pkl')

# MySQL Database Connection Config
db_config = {
    'host': 'localhost',
    'user': 'root',  # Change if needed
    'password': 'password'  # Set your MySQL password
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Function to create the database and tables if they don’t exist
def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("CREATE DATABASE IF NOT EXISTS epharma")
    cursor.close()
    conn.close()
    
    db_config["database"] = "epharma"
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()

initialize_database()

@app.route('/', methods=['GET'])
def home():
    """ Redirect to login page by default """
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session['user'] = username
            return redirect(url_for('index'))  # Redirect to index after login
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')
#signup.html route
@app.route('/signup_page', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            cursor.close()
            conn.close()
            return render_template('signup.html', error="Username already exists!")

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('main_page'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))
#index.html route
@app.route('/main_page', methods=['GET', 'POST'])
def main_page():
    """ Allow access to index even if the user is not logged in """
    if request.method == 'POST':
        try:
            age = request.form.get('age')
            gender = request.form.get('Gender')
            symptoms = request.form.get('symptoms', '').strip()

            if not age or not symptoms:
                return render_template('index.html', error="Please provide valid inputs.")

            symptom_list = [sym.strip() for sym in symptoms.split() if sym.strip()]
            if len(symptom_list) < 1 or len(symptom_list) > 3:
                return render_template('index.html', error="Please enter 1 to 3 symptoms.")

            while len(symptom_list) < 3:
                symptom_list.append('')

            symptom_string = ' '.join(symptom_list[:3])
            prediction = model.predict([symptom_string])
            medicine = prediction[0]

            return render_template('results.html', gender=gender, age=age, symptoms=symptoms, medicine=medicine)
        except ValueError:
            return render_template('index.html', error="Please enter valid data for age.")
    
    return render_template('index.html', user=session.get('user'))
#Route for cpr as I am using url_for('guide1') insted of direct "cpr.html"
@app.route("/guide1")
def guide1():
    return render_template("first_aid/cpr.html")

#guide 2-snake_bite
@app.route("/guide2")
def guide2():
    return render_template("first_aid/snake_bites.html")
#guide3-fire_accidents
@app.route("/guide3")
def guide3():
    return render_template("first_aid/fire_accidents.html")
#guide4-electric_shocks
@app.route("/guide4")
def guide4():
    return render_template("first_aid/electric_shocks.html")



if __name__ == "__main__":
    app.run(debug=True)

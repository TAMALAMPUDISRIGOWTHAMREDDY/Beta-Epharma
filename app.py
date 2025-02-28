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
    'password': 'Gowtham@2203'  # Set your MySQL password
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Function to create the database and tables if they don’t exist
def initialize_database():
    # Connect without specifying a database to create `epharma`
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create database if it does not exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS epharma")
    cursor.close()
    conn.close()
    
    # Now connect to `epharma`
    db_config["database"] = "epharma"
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Create `users` table if it doesn’t exist
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

# Call this function before starting the app
initialize_database()



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
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
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

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            age = int(request.form['age'])
            gender = request.form['Gender']
            symptoms = request.form['symptoms'].strip()

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

    return render_template('index.html')  


'''@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            age = int(request.form['age'])
            gender = request.form['Gender']
            symptoms = request.form['symptoms'].strip()

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

    return render_template('index.html')'''

@app.route("/cpr")
def cpr():
    return render_template("first_aid/cpr.html")

@app.route("/electric_shock")
def electric_shock():
    return render_template("first_aid/electric_shocks.html")

@app.route("/fire_accidents")
def fire_accidents():
    return render_template("first_aid/fire_accidents.html")

@app.route("/snake_bites")
def snake_bites():
    return render_template("first_aid/snake_bites.html")

if __name__ == "__main__":
    app.run(debug=True)





'''import joblib
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
    # Connect without specifying a database to create `epharma`
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create database if it does not exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS epharma")
    cursor.close()
    conn.close()
    
    # Now connect to `epharma`
    db_config["database"] = "epharma"
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Create `users` table if it doesn’t exist
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

# Call this function before starting the app
initialize_database()

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
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
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

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            age = int(request.form['age'])
            gender = request.form['Gender']
            symptoms = request.form['symptoms'].strip()

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

    return render_template('index.html')

@app.route("/cpr")
def cpr():
    return render_template("first_aid/cpr.html")

@app.route("/electric_shock")
def electric_shock():
    return render_template("first_aid/electric_shocks.html")

@app.route("/fire_accidents")
def fire_accidents():
    return render_template("first_aid/fire_accidents.html")

@app.route("/snake_bites")
def snake_bites():
    return render_template("first_aid/snake_bites.html")

if __name__ == "__main__":
    app.run(debug=True)'''

import joblib
import mysql.connector
import requests 
import wikipediaapi
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

def get_wikimedia_image(medicine_name):
    """
    Fetch the most relevant medicine or molecular structure image from Wikimedia.
    """
    search_url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&titles=File:{medicine_name}.jpg|File:{medicine_name}.png&origin=*&iiprop=url"
    
    response = requests.get(search_url)
    
    if response.status_code == 200:
        data = response.json()
        pages = data.get("query", {}).get("pages", {})

        for page in pages.values():
            if "imageinfo" in page:
                img_url = page["imageinfo"][0]["url"]
                return img_url  # Return the first valid image found
    
    return None  # If no image found, return None

def get_molecular_structure(medicine_name):
    """
    Fetch molecular structure image if no medicine image is found.
    """
    search_url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srsearch={medicine_name} chemical structure&origin=*"
    
    response = requests.get(search_url)
    
    if response.status_code == 200:
        data = response.json()
        search_results = data.get("query", {}).get("search", [])
        
        if search_results:
            first_result = search_results[0]["title"]
            return f"https://commons.wikimedia.org/wiki/Special:FilePath/{first_result.replace(' ', '_')}"
    
    return None

def get_medicine_symptoms(medicine_name):
    """
    Fetch symptoms related to a medicine from Wikipedia.
    """
    user_agent = "ePharmaBot/1.0 (contact: your-email@example.com)"  # Set your own user-agent
    wiki_wiki = wikipediaapi.Wikipedia(language='en', user_agent=user_agent)
    
    page = wiki_wiki.page(medicine_name)

    if page.exists():
        summary = page.summary
        sentences = summary.split(". ")  # Split into sentences
        
        if len(sentences) > 2:
            return ". ".join(sentences[:2]) + "."  # Return first 2 sentences, ensuring completeness
        else:
            return summary  # If short, return as is

    return "Did you enter correct Medicine? Because no symptoms found for this medicine."

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
            return redirect(url_for('main_page'))  # Redirect to index after login
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
            symptom_list = [sym.strip() for sym in symptoms.split(",") if sym.strip()]
            if len(symptom_list) < 1 or len(symptom_list) > 3:
                return render_template('index.html', error="Please enter 1 to 3 symptoms.")
            symptom_string = ' '.join(symptom.lower() for symptom in symptom_list)
            while len(symptom_list) < 3:
                symptom_list.append("null")
            symptom_string = ' '.join(symptom_list[:3])
            prediction = model.predict([symptom_string])
            medicine = prediction[0]  

            # Try fetching a real medicine image
            medicine_image = get_wikimedia_image(medicine.replace(" ", "_"))

            # If no medicine image found, fallback to molecular structure
            if not medicine_image:
                medicine_image = get_molecular_structure(medicine.replace(" ", "_"))

            return render_template('results.html', gender=gender, age=age, symptoms=symptoms, medicine=medicine, medicine_image=medicine_image)
        except ValueError:
            return render_template('index.html', error="Please enter valid data for age.")

    return render_template('index.html', user=session.get('user'))

@app.route('/search_medicine', methods=['GET', 'POST'])
def search_medicine():
    symptoms = None
    medicine_name = None

    if request.method == 'POST':
        medicine_name = request.form.get('medicine', '').strip()

        if medicine_name:
            symptoms = get_medicine_symptoms(medicine_name)

    return render_template('index.html', medicine=medicine_name, symptoms=symptoms)

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

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import os
import mysql.connector
import bcrypt
import hashlib
import pickle
import joblib
from flask_session import Session
# from flask import session
import pickle
import numpy as np





symp = ['back_pain','constipation','abdominal_pain','diarrhoea','mild_fever','yellow_urine',
'yellowing_of_eyes','acute_liver_failure','fluid_overload','swelling_of_stomach',
'swelled_lymph_nodes','malaise','blurred_and_distorted_vision','phlegm','throat_irritation',
'redness_of_eyes','sinus_pressure','runny_nose','congestion','chest_pain','weakness_in_limbs',
'fast_heart_rate','pain_during_bowel_movements','pain_in_anal_region','bloody_stool',
'irritation_in_anus','neck_pain','dizziness','cramps','bruising','obesity','swollen_legs',
'swollen_blood_vessels','puffy_face_and_eyes','enlarged_thyroid','brittle_nails',
'swollen_extremeties','excessive_hunger','extra_marital_contacts','drying_and_tingling_lips',
'slurred_speech','knee_pain','hip_joint_pain','muscle_weakness','stiff_neck','swelling_joints',
'movement_stiffness','spinning_movements','loss_of_balance','unsteadiness',
'weakness_of_one_body_side','loss_of_smell','bladder_discomfort','foul_smell_of urine',
'continuous_feel_of_urine','passage_of_gases','internal_itching','toxic_look_(typhos)',
'depression','irritability','muscle_pain','altered_sensorium','red_spots_over_body','belly_pain',
'abnormal_menstruation','dischromic _patches','watering_from_eyes','increased_appetite','polyuria','family_history','mucoid_sputum',
'rusty_sputum','lack_of_concentration','visual_disturbances','receiving_blood_transfusion',
'receiving_unsterile_injections','coma','stomach_bleeding','distention_of_abdomen',
'history_of_alcohol_consumption','fluid_overload','blood_in_sputum','prominent_veins_on_calf',
'palpitations','painful_walking','pus_filled_pimples','blackheads','scurring','skin_peeling',
'silver_like_dusting','small_dents_in_nails','inflammatory_nails','blister','red_sore_around_nose',
'yellow_crust_ooze']

prognosis = ['Fungal infection','Allergy','GERD','Chronic cholestasis','Drug Reaction',
'Peptic ulcer diseae','AIDS','Diabetes','Gastroenteritis','Bronchial Asthma','Hypertension',
' Migraine','Cervical spondylosis',
'Paralysis (brain hemorrhage)','Jaundice','Malaria','Chicken pox','Dengue','Typhoid','hepatitis A',
'Hepatitis B','Hepatitis C','Hepatitis D','Hepatitis E','Alcoholic hepatitis','Tuberculosis',
'Common Cold','Pneumonia','Dimorphic hemmorhoids(piles)',
'Heartattack','Varicoseveins','Hypothyroidism','Hyperthyroidism','Hypoglycemia','Osteoarthristis',
'Arthritis','(vertigo) Paroymsal  Positional Vertigo','Acne','Urinary tract infection','Psoriasis',
'Impetigo']





app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'disease_pred'

mysql = MySQL(app)



@app.route("/")  # this sets the route to this page
def home():

    return render_template("index.html")
# Flask application file


model = pickle.load(open("model.pkl", "rb"))

@app.route("/predict", methods=["POST",'GET'])
def predict():
        if request.method == "POST":
            # Get the selected symptoms from the form data
            selected_symptoms = request.form.getlist("symptom")
            print(selected_symptoms)
            # Create a binary representation of the selected symptoms
            symptoms = np.zeros(len(symp))
            for i, symptom in enumerate(symp):
                if symptom in selected_symptoms:
                    symptoms[i] = 1
            # Use the model to make a prediction
            result = model.predict(symptoms.reshape(1, -1))
            # Return the prediction result to the HTML template
            return render_template("predict.html", result=prognosis[result[0]])
        return render_template("predict.html")










@app.route("/blood")  # this sets the route to this page
def blood():
    return render_template("blood.html")

@app.route("/ngo")  # this sets the route to this page
def ngo():
    return render_template("ngo.html")

@app.route("/add_checkups", methods=['GET', 'POST'])  # this sets the route to this page
def add_checkups():
    #ngo wrk
    if request.method == "POST":
        details = request.form
        ngo_name = details['ngo_name']
        type_check = details['type_check']
        date = details['date']
        time = details['time']

        contact = details['contact']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO add_check(ngo_name, type_check, date,time, contact) VALUES (%s, %s, %s, %s, %s)",
                    (ngo_name, type_check, date,time, contact))
        mysql.connection.commit()
        cur.close()
        # return 'success'

        return '<script>alert("CHECK-UP TYPE ADDED SUCCESFULLY");window.location="/ngo_server"</script>'

    return render_template("add_checkups.html")



@app.route('/ngo_sign_up', methods=['GET', 'POST'])
def ngo_sign_up():
    if request.method == 'POST':
        # Fetch form data
        userDetails = request.form
        ngo_name = userDetails['ngo_name']
        type1 = userDetails['type1']
        pass1 = userDetails['pass1']
        number = userDetails['number']

        hashed_password = bcrypt.hashpw(pass1.encode('utf-8'), bcrypt.gensalt())

        # Initialize cursor
        # conn = mysql.connect()
        # cursor = conn.cursor()
        cursor = mysql.connection.cursor()
        # Insert user details into the table
        cursor.execute("INSERT INTO ngo_users(ngo_name, type1, pass1, number) VALUES(%s, %s, %s, %s)", (ngo_name, type1, hashed_password, number))
        mysql.connection.commit()
        cursor.close()

        # Redirect to login page
        return '<script>alert("ngo registered successfully");window.location="/ngo_login"</script>'

    return render_template('ngo_sign_up.html')


@app.route('/ngo_login', methods=['POST','GET'])
def login_post():
    if request.method == 'POST':
        # Get form data
        ngo_name = request.form['ngo_name']
        pass1 = request.form['pass1']

        # Initialize cursor
        cursor = mysql.connection.cursor()

        # Execute the query to check if the user exists
        query = "SELECT * FROM ngo_users WHERE ngo_name = %s"
        cursor.execute(query, (ngo_name,))
        user = cursor.fetchone()

        # Close the cursor
        cursor.close()

        # Check if the user exists and verify the password
        if user and bcrypt.checkpw(pass1.encode('utf-8'), user[1].encode('utf-8')):
            # Create the session
            # session['p_name'] = p_name

            # Redirect the user to a protected page
            return '<script>alert("Logged in successfully");window.location="/ngo_server"</script>'

        else:
            # If the user does not exist or password is incorrect, redirect to login page
            return '<script>alert("Wrong username or password");window.location="/ngo_login"</script>'
    #
    # if request.method == 'POST':
    #     # Get form data
    #     ngo_name = request.form['ngo_name']
    #     pass1 = request.form['pass1']
    #
    #     # Initialize cursor
    #     cursor = mysql.connection.cursor()
    #
    #     # Execute the query to check if the user exists
    #     query = "SELECT * FROM ngo_users WHERE ngo_name = %s"
    #     cursor.execute(query, (ngo_name,))
    #     user = cursor.fetchone()
    #
    #     # Close the cursor
    #     cursor.close()
    #
    #     # Check if the user exists and verify the password
    #     if user and bcrypt.checkpw(pass1.encode('utf-8'), user['pass1']):
    #
    #         # Create the session
    #         session['ngo_name'] = ngo_name
    #
    #         # Redirect the user to a protected page
    #         return '<script>alert("Logged in successfully");window.location="/ngo_server"</script>'
    #
    #     else:
    #         # If the user does not exist or password is incorrect, redirect to login page
    #         return '<script>alert("Wrong username or password");window.location="/ngo_login"</script>'

    return render_template('ngo_login.html')



# @app.route('/ngo_logout')
# def ngo_logout():
#     #clear the session data
#     session.clear()
#     return redirect(url_for('ngo_login'))

@app.route("/ngo_server")
def ngo_server():
    return render_template("ngo_server.html")


#patient sign up
# @app.route("/patient_sign_up" ,methods=['POST','GET'])
# def patient_sign_up():
#     if request.method == 'POST':
#         # Fetch form data
#         userDetails = request.form
#         p_name = userDetails['p_name']
#         email = userDetails['email']
#         pass1 = userDetails['pass']
#         number = userDetails['number']
#         address = userDetails['address']
#
#         hashed_password = bcrypt.hashpw(pass1.encode('utf-8'), bcrypt.gensalt())
#
#         # Initialize cursor
#         # conn = mysql.connect()
#         # cursor = conn.cursor()
#         cursor = mysql.connection.cursor()
#         # Insert user details into the table
#         cursor.execute("INSERT INTO patient_users(p_name, email, pass, number, address) VALUES(%s, %s, %s, %s, %s)",
#                        (p_name, email, hashed_password, number, address))
#         mysql.connection.commit()
#         cursor.close()
#
#         # Redirect to login page
#         return '<script>alert(" Registered successfully");window.location="/user_login"</script>'
#
#     return render_template("patient_sign_up.html")
@app.route("/patient_sign_up" ,methods=['POST','GET'])
def patient_sign_up():
    if request.method == 'POST':
        # Fetch form data
        userDetails = request.form
        p_name = userDetails['p_name']
        email = userDetails['email']
        password1 = userDetails['password1']
        number = userDetails['number']
        address = userDetails['address']

        hashed_password = bcrypt.hashpw(password1.encode('utf-8'), bcrypt.gensalt())

        # Initialize cursor
        cursor = mysql.connection.cursor()
        # Insert user details into the table
        cursor.execute("INSERT INTO patient_users(p_name, email, password1, number, address) VALUES(%s,  %s,%s, %s, %s)",
                       (p_name, email, hashed_password, number, address))
        mysql.connection.commit()
        cursor.close()

        # Redirect to login page
        return '<script>alert("Registered successfully");window.location="/patient_login"</script>'

    return render_template("patient_sign_up.html")


#login patient

# @app.route('/patient_login', methods=['GET', 'POST'])
# def patient_login():
#     if request.method == 'POST':
#         #get the form data
#         p_name = request.form['p_name']
#         password1 = request.form['password1']
#
#
#         cur = mysql.connection.cursor()
#         #
#
#        # execute the query to check if the user exists
#         query = "SELECT * FROM patient_users WHERE p_name=%s AND password1=%s"
#         cur.execute(query, (p_name, password1))
#         user = cur.fetchone()
#
#      #   close the cursor and the connection
#         cur.close()
#
#
#         #check if the user exists
#         if user:
#             #create the session
#             session['p_name'] = p_name
#
#             #redirect the user to a protected page
#             return '<script>alert(" Registered successfully");window.location="/"</script>'
#
#         else:
#             #if the user does not exist, redirect the user back to the login page
#             return '<script>alert(" Wrong password");window.location="/patient_login"</script>'
#     return render_template('patient_login.html')
#doc sign
@app.route('/patient_login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        # Get form data
        p_name = request.form['p_name']
        password1 = request.form['password1']

        # Initialize cursor
        cursor = mysql.connection.cursor()

        # Execute the query to check if the user exists
        query = "SELECT * FROM patient_users WHERE p_name = %s"
        cursor.execute(query, (p_name,))
        user = cursor.fetchone()

        # Close the cursor
        cursor.close()

        # Check if the user exists and verify the password
        if user and bcrypt.checkpw(password1.encode('utf-8'), user[4].encode('utf-8')):
            # Create the session
            # session['p_name'] = p_name

            # Redirect the user to a protected page
            return '<script>alert("Logged in successfully");window.location="/"</script>'

        else:
            # If the user does not exist or password is incorrect, redirect to login page
            return '<script>alert("Wrong username or password");window.location="/patient_login"</script>'

    return render_template('patient_login.html')

@app.route("/doc_sign_up" ,methods=['GET', 'POST'])
def doc_sign_up():
    if request.method == 'POST':
        # Fetch form data
        userDetails = request.form
        d_name = userDetails['d_name']
        passwrd1 = userDetails['passwrd1']
        email = userDetails['email']
        special = userDetails['special']

        number = userDetails['number']
        address = userDetails['address']

        hashed_password = bcrypt.hashpw(passwrd1.encode('utf-8'), bcrypt.gensalt())

        # Initialize cursor
        # conn = mysql.connect()
        # cursor = conn.cursor()
        cursor = mysql.connection.cursor()
        # Insert user details into the table
        cursor.execute("INSERT INTO doc_user(d_name, email, passwrd1, number, address,special) VALUES(%s, %s, %s, %s, %s, %s)",
                       (d_name, email, hashed_password, number, address, special))
        mysql.connection.commit()
        cursor.close()

        # Redirect to login page
        return '<script>alert(" Registered successfully");window.location="/"</script>'

    return render_template("doc_sign_up.html")





# 



@app.route("/donate", methods=['GET', 'POST'])  # this sets the route to this page blood donation
def donate():
        if request.method == "POST":
            details = request.form
            Name = details['name']
            age = details['age']
            blood_group = details['blood_group']
            past_illness = details['past_illness']
            mobile = details['mobile']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO b_donation(Name, age, blood_group, past_illness, mobile) VALUES (%s, %s, %s, %s, %s)", (Name, age, blood_group, past_illness, mobile))
            mysql.connection.commit()
            cur.close()
            # return 'success'

            return '<script>alert("EVERY DROP MATTERS!! Note:you will get a call within 7 days");window.location="/blood"</script>'

        return render_template('donate.html')


@app.route("/receive")  # this sets the route to this page
def receive():

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM b_donation")
    fetchdata = cur.fetchall()
    cur.close()
    return render_template("receive.html" , data = fetchdata)

@app.route("/doc_list")  # this sets the route to this page
def doc_list():

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM doc_user")
    fetchdata = cur.fetchall()
    cur.close()
    return render_template("doc_list.html" , data = fetchdata)


@app.route("/ngo_list")
def ngo_list():

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ngo_users")
    fetchdata = cur.fetchall()
    cur.close()
    return render_template("ngo_list.html", data = fetchdata)

@app.route("/upcomin_check")
def upcomin_check():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM add_check")
    fetchdata = cur.fetchall()
    cur.close()
    # patients view
    return render_template("upcomin_check.html", data=fetchdata)



if __name__ == "__main__":
    app.run(debug=True)

    # things which r done
    #
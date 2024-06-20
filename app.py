# Import necessary libraries
import numpy as np
import pickle
import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector

# Set page configuration
st.set_page_config(page_title="Health Assistant", layout="wide", page_icon="🧑‍⚕️")

# Initialize logged_in in session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Load the saved machine learning models
diabetes_model = pickle.load(open("C:/Anaconda/envs/Machinelearning/Model_deployment/Model/diabetes_disease_detection_model.sav", 'rb'))
heart_disease_model = pickle.load(open("C:/Anaconda/envs/Machinelearning/Model_deployment/Model/heart_disease_detection_model.sav", 'rb'))
parkinsons_model = pickle.load(open("C:/Anaconda/envs/Machinelearning/Model_deployment/Model/parkinsons_disease_detection_model.sav", 'rb'))
liver_disease_model = pickle.load(open("C:/Anaconda/envs/Machinelearning/Model_deployment/Model/liver_disease_detection_model.sav", 'rb'))

# Connect to MySQL database
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="health_assistant")

# Function to handle user login
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Connect to the database
        connection = connect_to_database()
        cursor = connection.cursor()

        # Check username and password against the database
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()

        if result:
            st.success("Login successful!")
            # Set user session variable to indicate that the user is logged in
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.email = result[3]  # Assuming email is stored in the second column of the users table
            st.session_state.phone = result[2]  # Assuming phone is stored in the third column of the users table
        else:
            st.error("Invalid username or password")

        # Close the database connection
        cursor.close()
        connection.close()

# Function to handle user signup
def signup():
    st.title("Signup")
    # Add signup form fields (e.g., username, password, email, phone number, etc.)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    if st.button("Signup"):
        # Connect to the database
        connection = connect_to_database()
        cursor = connection.cursor()

        # Insert user information into the database
        cursor.execute("INSERT INTO users (username, phone_no, email, password) VALUES (%s, %s, %s, %s)", (username, phone, email, password))
        connection.commit()

        st.success("Signup successful! Please login.")

        # Close the database connection
        cursor.close()
        connection.close()
        
        # Set session state variables
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.email = email
        st.session_state.phone = phone
        
# Function to edit user profile
def edit_profile():
    st.title("Edit Profile")
    # Retrieve user information from session state
    username = st.session_state.username
    email = st.session_state.email
    phone = st.session_state.phone
    
    # Input fields to edit profile
    new_email = st.text_input("New Email", email)
    new_phone = st.text_input("New Phone Number", phone)
    
    if st.button("Save Changes"):
        # Connect to the database
        connection = connect_to_database()
        cursor = connection.cursor()
        
        # Update user information in the database
        cursor.execute("UPDATE users SET email = %s, phone_no = %s WHERE username = %s", (new_email, new_phone, username))
        connection.commit()
        
        # Update session state variables
        st.session_state.email = new_email
        st.session_state.phone = new_phone
        
        st.success("Profile updated successfully!")
        
        # Close the database connection
        cursor.close()
        connection.close()
        
# Function to delete user account along with their test results and feedback
def delete_account():
    if st.button("Delete Account"):
        # Connect to the database
        connection = connect_to_database()
        cursor = connection.cursor()

        # Delete user account from the database
        cursor.execute("DELETE FROM users WHERE username = %s", (st.session_state.username,))
        
        # Delete user's test results from all relevant tables
        cursor.execute("DELETE FROM diabetes_test_results WHERE username = %s", (st.session_state.username,))
        cursor.execute("DELETE FROM heart_disease_test_results WHERE username = %s", (st.session_state.username,))
        cursor.execute("DELETE FROM parkinsons_test_results WHERE username = %s", (st.session_state.username,))
        cursor.execute("DELETE FROM liver_disease_test_results WHERE username = %s", (st.session_state.username,))
        
        # Delete user's feedback from the feedback table
        cursor.execute("DELETE FROM feedback WHERE username = %s", (st.session_state.username,))
        
        # Delete user's appointments from the appointments table
        cursor.execute("DELETE FROM appointments WHERE username = %s", (st.session_state.username,))
        
        connection.commit()

        st.success("Your account, test results, feedback, and appointments have been deleted.")

        # Close the database connection
        cursor.close()
        connection.close()

        # Logout the user
        logout()

# Function to handle user logout
def logout():
    # Remove user session variable to indicate that the user is logged out
    st.session_state.logged_in = False
    st.success("You have been logged out.")

#Function to handle chatbot query  
def health_assistant_chatbot(input_message):
    # Define responses based on health-related input messages
    health_responses = {
        "hi": "Hello! How can I assist you today?",
        "how are you?": "I'm just a chatbot, but thank you for asking!",
        "bye": "Goodbye! Take care of yourself.",
        "diabetes": "Diabetes is a chronic condition that affects how your body regulates blood sugar levels. It's essential to manage diabetes through lifestyle changes, medication, and regular monitoring of blood sugar levels.",
        "diabetic diet": "A diabetic diet focuses on controlling blood sugar levels by eating foods that are low in sugar and carbohydrates. It typically includes plenty of fruits, vegetables, whole grains, lean proteins, and healthy fats.",
        "diabetes exercise": "Regular exercise is crucial for managing diabetes as it helps control blood sugar levels, improves insulin sensitivity, and promotes overall health. Aim for at least 30 minutes of moderate-intensity exercise most days of the week.",
        "diabetes medication": "Medications for diabetes include insulin, metformin, sulfonylureas, and others. These medications help lower blood sugar levels and prevent complications. It's essential to take medications as prescribed by your healthcare provider.",
        "diabetes complications": "Complications of diabetes include heart disease, stroke, kidney disease, nerve damage, and eye problems. Managing blood sugar levels, blood pressure, cholesterol, and adopting a healthy lifestyle can help prevent complications.",
        "diabetes symptoms": "Common symptoms of diabetes include increased thirst, frequent urination, unexplained weight loss, fatigue, blurred vision, and slow wound healing. If you experience any of these symptoms, consult your doctor for evaluation.",
        "heart disease": "Heart disease refers to various conditions that affect the heart's function and blood vessels. It's crucial to manage risk factors such as high blood pressure, high cholesterol, diabetes, obesity, smoking, and lack of physical activity.",
        "heart-healthy diet": "A heart-healthy diet includes plenty of fruits, vegetables, whole grains, lean proteins, and healthy fats. It's low in sodium, saturated fats, trans fats, and cholesterol. Eating a balanced diet can help lower the risk of heart disease.",
        "heart disease prevention": "Preventing heart disease involves adopting a healthy lifestyle, including regular exercise, maintaining a healthy weight, eating a balanced diet, quitting smoking, limiting alcohol intake, managing stress, and getting regular check-ups.",
        "heart disease symptoms": "Symptoms of heart disease vary but may include chest pain or discomfort, shortness of breath, palpitations, fatigue, dizziness, nausea, and sweating. Seek immediate medical attention if you experience these symptoms.",
        "parkinson's": "Parkinson's disease is a progressive nervous system disorder that affects movement. Symptoms include tremors, stiffness, slowness of movement, and impaired balance. Treatment aims to manage symptoms and improve quality of life.",
        "parkinson's exercise": "Regular exercise can help improve mobility, flexibility, balance, and overall well-being in people with Parkinson's disease. It's essential to include a combination of aerobic, strength, flexibility, and balance exercises.",
        "parkinson's medication": "Medications such as levodopa, dopamine agonists, MAO-B inhibitors, and others are used to manage Parkinson's symptoms. These medications help increase dopamine levels in the brain and alleviate motor symptoms.",
        "parkinson's symptoms": "Common symptoms of Parkinson's disease include tremors, rigidity, bradykinesia (slowness of movement), postural instability, and freezing of gait. Non-motor symptoms may also occur, such as mood changes, sleep disturbances, and cognitive problems.",
        "parkinson's support": "Joining a support group for Parkinson's disease can provide emotional support, practical advice, and resources for coping with the challenges of the condition. Connecting with others who understand can be helpful for patients and caregivers.",
        "liver disease": "Liver disease encompasses a range of conditions that affect the liver's structure and function. Causes include viral infections, alcohol abuse, fatty liver disease, autoimmune conditions, and genetic factors.",
        "liver-friendly diet": "A liver-friendly diet includes foods that support liver health, such as fruits, vegetables, whole grains, lean proteins, and healthy fats. It's important to limit processed foods, sugary snacks, and alcohol.",
        "liver disease prevention": "Preventing liver disease involves avoiding excessive alcohol consumption, maintaining a healthy weight, getting vaccinated against hepatitis viruses, practicing safe sex, and avoiding exposure to toxins and harmful chemicals.",
        "liver disease symptoms": "Symptoms of liver disease vary depending on the underlying cause but may include fatigue, weakness, jaundice, abdominal pain, swelling in the abdomen, nausea, vomiting, and dark urine. Seek medical attention if you experience these symptoms.",
        "diabetes myths": "There are many myths surrounding diabetes, such as eating too much sugar causes it, or only overweight individuals get diabetes. It's important to separate fact from fiction and rely on evidence-based information.",
        "heart disease myths": "Common myths about heart disease include believing it only affects older adults or that heart attacks always present with severe chest pain. Education and awareness are key to dispelling these myths and promoting heart health.",
        "parkinson's myths": "Myths about Parkinson's disease include the belief that it's solely an elderly person's condition or that it's always associated with tremors. Dispelling these myths can help raise awareness and improve understanding of the disease.",
        "liver disease myths": "Misconceptions about liver disease may include thinking it only affects heavy drinkers or that symptoms always manifest early. Educating oneself about liver health and risk factors can help debunk these myths.",
        "default": "I'm sorry, I don't have information on that topic. Please consult a healthcare professional for assistance."
    }
    
    # Check if the input message matches any health-related keywords
    matched_responses = [response for keyword, response in health_responses.items() if keyword in input_message.lower()]
    
    if matched_responses:
        return matched_responses[0]  # Return the first matched response
    else:
        return health_responses["default"]  # If no matching keyword is found, return a default response
    
# Function to recommend medication based on the health condition
def recommend_medication(condition):
    # Implement your medication recommendation logic here
    if condition == "Diabetes":
        return "Common medications for diabetes include Metformin, Insulin, and Sulfonylureas. Please consult your healthcare provider for proper prescription and dosage."
    elif condition == "Heart Disease":
        return "Medications such as Beta-Blockers, ACE Inhibitors, and Statins are commonly used for heart disease management. Your doctor will prescribe the appropriate medication based on your condition."
    elif condition == "Parkinson's Disease":
        return "Levodopa, Dopamine Agonists, and MAO-B Inhibitors are often prescribed for Parkinson's disease. Your neurologist will determine the best treatment plan for you."
    elif condition == "Liver Disease":
        return "Treatment for liver disease varies depending on the underlying cause. Your doctor may recommend medications to manage symptoms and slow disease progression."
    else:
        return "No specific medication recommendation available."

# Function to suggest additional tests based on the health condition
def suggest_additional_tests(condition):
    # Implement your additional test suggestion logic here
    if condition == "Diabetes":
        return "Consider scheduling an HbA1c test to assess your average blood sugar levels over the past few months."
    elif condition == "Heart Disease":
        return "An echocardiogram or cardiac stress test may provide more detailed information about your heart function and cardiovascular health."
    elif condition == "Parkinson's Disease":
        return "A DaTscan or MRI may be recommended for a more accurate diagnosis and assessment of Parkinson's disease progression."
    elif condition == "Liver Disease":
        return "Liver function tests, imaging studies (e.g., ultrasound, MRI), or liver biopsy may be necessary to evaluate liver function and determine the extent of liver damage."
    else:
        return "No specific additional test recommendation available."

# Function to make predictions using the diabetes model
def diabetes_prediction(input_data, username, email, phone):
    input_data_as_numpy_array = np.asarray(input_data)
    input_data_reshaped = input_data_as_numpy_array.reshape(1, -1)
    prediction = diabetes_model.predict(input_data_reshaped)
    if prediction[0] == 1:
        result = 'Positive'
        recommendations = "Follow a diabetic diet, exercise regularly, and consult a healthcare professional for medication."
        medication_recommendation = recommend_medication("Diabetes")
        additional_tests = suggest_additional_tests("Diabetes")
    else:
        result = 'Negative'
        recommendations = "No medication recommendations at this time."
        medication_recommendation = None
        additional_tests = None

    # Insert the test result into the database
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO diabetes_test_results (username, email, phone, results) VALUES (%s, %s, %s, %s)", (username, email, phone, result))
    connection.commit()
    cursor.close()
    connection.close()
    return result, recommendations, medication_recommendation, additional_tests

# Function to make predictions using the heart disease model
def heart_disease_prediction(input_data, username, email, phone):
    input_data_as_numpy_array = np.asarray(input_data)
    input_data_reshaped = input_data_as_numpy_array.reshape(1, -1)
    prediction = heart_disease_model.predict(input_data_reshaped)
    if prediction[0] == 1:
        result = 'Positive'
        recommendations = "Consult a cardiologist for further evaluation and medication."
        medication_recommendation = recommend_medication("Heart Disease")
        additional_tests = suggest_additional_tests("Heart Disease")
    else:
        result = 'Negative'
        recommendations = "No medication recommendations at this time."
        medication_recommendation = None
        additional_tests = None
    # Insert the test result into the database
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO heart_disease_test_results (username, email, phone, results) VALUES (%s, %s, %s, %s)", (username, email, phone, result))
    connection.commit()
    cursor.close()
    connection.close()
    return result, recommendations, medication_recommendation, additional_tests


# Function to make predictions using the Parkinson's disease model
def parkinsons_prediction(input_data, username, email, phone):
    input_data_as_numpy_array = np.asarray(input_data)
    input_data_reshaped = input_data_as_numpy_array.reshape(1, -1)
    prediction = parkinsons_model.predict(input_data_reshaped)
    if prediction[0] == 1:
        result = "Positive"
        recommendations = "Consult a neurologist for further evaluation and medication."
        medication_recommendation = recommend_medication("Parkinson's Disease")
        additional_tests = suggest_additional_tests("Parkinson's Disease")
    else:
        result = "Negative"
        recommendations = "No medication recommendations at this time."
        medication_recommendation = None
        additional_tests = None

    # Insert the test result into the database
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO parkinsons_test_results (username, email, phone, results) VALUES (%s, %s, %s, %s)", (username, email, phone, result))
    connection.commit()
    cursor.close()
    connection.close()
    return result, recommendations, medication_recommendation, additional_tests


#Function to make predictions using the Parkinson's disease model
def liver_disease_prediction(input_data, username, email, phone):
    input_data_as_numpy_array = np.asarray(input_data)
    input_data_reshaped = input_data_as_numpy_array.reshape(1, -1)
    prediction = liver_disease_model.predict(input_data_reshaped)
    if prediction[0] == 1:
        result = "Positive"
        recommendations = "Consult a hepatologist for further evaluation and medication."
        medication_recommendation = recommend_medication("Liver Disease")
        additional_tests = suggest_additional_tests("Liver Disease")
    else:
        result = "Negative"
        recommendations = "No medication recommendations at this time."
        medication_recommendation = None
        additional_tests = None
    # Insert the test result into the database
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO liver_disease_test_results (username, email, phone, results) VALUES (%s, %s, %s, %s)", (username, email, phone, result))
    connection.commit()
    cursor.close()
    connection.close()
    return result, recommendations, medication_recommendation, additional_tests

# Appointment creation function
def create_appointment(username, email, phone, appointment_date, reason):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO appointments (username, email, phone, appointment_date, reason) VALUES (%s, %s, %s, %s, %s)", (username, email, phone, appointment_date, reason))
    connection.commit()
    cursor.close()
    connection.close()
    return "Appointment created successfully!"

# Function to display user feedback form
def feedback_form(username):
    st.write("We value your feedback! Please share your experience with us.")
    feedback_text = st.text_area("Enter your feedback here", height=200)
    if st.button("Submit Feedback"):
        # Save feedback to the database
        connection = connect_to_database()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO feedback (username, feedback) VALUES (%s, %s)", (username, feedback_text))
        connection.commit()
        cursor.close()
        connection.close()
        st.success("Thank you for your feedback!")

# Main function to define the Streamlit web application
def main():
    with st.sidebar:
        options = ['Home', 'Diabetes Prediction', 'Heart Disease Prediction', 'Parkinsons Prediction','Liver Disease Prediction','Profile','Create Appointment','Health Assistant','Feedback','About']
        selected = option_menu('Multiple Disease Prediction System',
                               options,
                               menu_icon='hospital-fill', icons=['house-door', 'activity', 'heart', 'person','file-medical','person-circle','calendar','robot','chat-left-text','info-circle'], default_index=0)
    # Home Page    
    if selected == 'Home':
        st.title('Welcome to Health Assistant')
        st.write("Use the sidebar to navigate to different prediction pages.")
        st.write("Choose a prediction category from the sidebar to get started.")
        st.subheader("Available Predictions:")
        st.write("- Diabetes Prediction 🩸")
        st.write("- Heart Disease Prediction ❤️")
        st.write("- Parkinson's Disease Prediction 🧠")
        st.write("- Liver Disease Prediction 🍃")
        st.subheader("About Health Assistant:")
        st.write("Health Assistant is an application that uses machine learning models to predict the likelihood of having certain health conditions.")
        st.write("It provides predictions for Diabetes, Heart Disease, and Parkinson's Disease based on user-provided input.")
        st.subheader("How to Use:")
        st.write("1. Select a prediction category from the sidebar.")
        st.write("2. Enter the required information.")
        st.write("3. Click on the 'Test Result' button to get the prediction.")
  
    # Diabetes Prediction Page
    elif selected == 'Diabetes Prediction':
        st.title('Diabetes Prediction using ML')
        if st.session_state.logged_in:
            col1, col2, col3 = st.columns(3)
            with col1:
               Glucose = st.text_input('Glucose Level')
            with col2:
                BloodPressure = st.text_input('Blood Pressure value')
            with col3:
               SkinThickness = st.text_input('Skin Thickness value')
            with col1:
               Insulin = st.text_input('Insulin Level')
            with col2:
               BMI = st.text_input('BMI value')
            with col3:
               DiabetesPedigreeFunction = st.text_input('Diabetes Pedigree Function value')
            with col1:
               Age = st.text_input('Age of the Person')
            diab_diagnosis = ''
            if st.button('Diabetes Test Result'):
                user_input = [Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age]
                user_input = [float(x) for x in user_input]
                diab_diagnosis, recommendations, medication_recommendation, additional_tests = diabetes_prediction(user_input, st.session_state.username, st.session_state.email, st.session_state.phone)
                st.success(f"Diabetes Test Result: {diab_diagnosis}")
                st.info(recommendations)
                if medication_recommendation:
                    st.info(f"Medication Recommendation: {medication_recommendation}")
                if additional_tests:
                    st.info(f"Suggested Additional Tests: {additional_tests}")
        else:
            st.write("Please login to access this feature.")
     

    # Heart Disease Prediction Page
    elif selected == 'Heart Disease Prediction':
            st.title('Heart Disease Prediction using ML')
            if st.session_state.logged_in:
                col1, col2, col3 = st.columns(3)
                with col1:
                    age = st.text_input('Age')
                with col2:
                    sex = st.text_input('Sex(0=Female and 1=Male)')
                with col3:
                    cp = st.text_input('Chest Pain types')
                with col1:
                    trestbps = st.text_input('Resting Blood Pressure(in mm Hg on admission to the hospital)')
                with col2:
                    chol = st.text_input('Serum Cholestoral in mg/dl')
                with col3:
                    fbs = st.text_input('Fasting Blood Sugar > 120 mg/dl(1 = true; 0 = false)')
                with col1:
                    restecg = st.text_input('Resting Electrocardiographic results')
                with col2:
                    thalach = st.text_input('Maximum Heart Rate achieved')
                with col3:
                    exang = st.text_input('Exercise Induced Angina(1 = yes; 0 = no)')
                with col1:
                    oldpeak = st.text_input('ST depression induced by exercise')
                with col2:
                    slope = st.text_input('Slope of the peak exercise ST segment')
                with col3:
                    ca = st.text_input('Major vessels (0-3) colored by flourosopy')
                with col1:
                    thal = st.text_input('thal: 1 = normal; 2 = fixed defect; 3 = reversable defect')
                heart_diagnosis = ''
                if st.button('Heart Disease Test Result'):
                    user_input = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]
                    user_input = [float(x) for x in user_input]
                    heart_diagnosis, recommendations, medication_recommendation, additional_tests = heart_disease_prediction(user_input, st.session_state.username, st.session_state.email, st.session_state.phone)
                    st.success(f"Heart Disease Test Result: {heart_diagnosis}")
                    st.info(recommendations)
                    if medication_recommendation:
                        st.info(f"Medication Recommendation: {medication_recommendation}")
                    if additional_tests:
                        st.info(f"Suggested Additional Tests: {additional_tests}")
            else:
                st.write("Please login to access this feature.")
            
    # Parkinson's Prediction Page
    elif selected == "Parkinsons Prediction":
            st.title("Parkinson's Disease Prediction using ML")
            if st.session_state.logged_in:
                col1, col2, col3 = st.columns(3)
                with col1:
                    fo = st.text_input('MDVP Fo(Hz) ')
                with col2:
                    fhi = st.text_input('MDVP Fhi(Hz)')
                with col3:
                    flo = st.text_input('MDVP Flo(Hz)')
                with col1:
                    Jitter_percent = st.text_input('MDVP Jitter(%)')
                with col2:
                    Jitter_Abs = st.text_input('MDVP Jitter(Abs)')
                with col3:
                    RAP = st.text_input('MDVP RAP')
                with col1:
                    PPQ = st.text_input('MDVP PPQ')
                with col2:
                    DDP = st.text_input('Jitter DDP')
                with col3:
                    Shimmer = st.text_input('MDVP Shimmer')
                with col1:
                    Shimmer_dB = st.text_input('MDVP Shimmer(dB)')
                with col2:
                    APQ3 = st.text_input('Shimmer APQ3')
                with col3:
                    APQ5 = st.text_input('Shimmer APQ5')
                with col1:
                    APQ = st.text_input('MDVP APQ')
                with col2:
                    DDA = st.text_input('Shimmer DDA')
                with col3:
                    NHR = st.text_input('NHR')
                with col1:
                    HNR = st.text_input('HNR')
                with col2:
                    RPDE = st.text_input('RPDE')
                with col3:
                    DFA = st.text_input('DFA')
                with col1:
                    spread1 = st.text_input('spread1')
                with col2:
                    spread2 = st.text_input('spread2')
                with col3:
                    D2 = st.text_input('D2')
                with col1:
                    PPE = st.text_input('PPE')
                parkinsons_diagnosis = ''
                if st.button("Parkinson's Test Result"):
                    user_input = [fo, fhi, flo, Jitter_percent, Jitter_Abs, RAP, PPQ, DDP, Shimmer, Shimmer_dB, APQ3, APQ5, APQ, DDA, NHR, HNR, RPDE, DFA, spread1, spread2, D2,PPE]
                    user_input = [float(x) for x in user_input]
                    parkinsons_diagnosis, recommendations, medication_recommendation, additional_tests = parkinsons_prediction(user_input, st.session_state.username, st.session_state.email, st.session_state.phone)
                    st.success(f"Parkinson's Test Result: {parkinsons_diagnosis}")
                    st.info(recommendations)
                    if medication_recommendation:
                        st.info(f"Medication Recommendation: {medication_recommendation}")
                    if additional_tests:
                        st.info(f"Suggested Additional Tests: {additional_tests}")
            else:
                st.write("Please login to access this feature.")
    
    #Liver Prediction Page
    elif selected == 'Liver Disease Prediction':
        st.title("Liver Disease Prediction using ML")
        if st.session_state.logged_in:
            col1, col2, col3 = st.columns(3)
            with col1:
                age=st.text_input('Age of the patient')
            with col2:
                gender=st.text_input('Gender of the patient(1=Male and 0=Female)')
            with col3:
                Total_Billirubin=st.text_input('Total Billirubin in mg/dL')
            with col1:
                Direct_Bilirubin=st.text_input('Conjugated Billirubin in mg/dL')
            with col2:
                Alkaline_Phosphotase=st.text_input('Alkaline Phosphotase in IU/L')
            with col3:
                Alamine_Aminotransferase=st.text_input('Alamine Aminotransferase in IU/L')
            with col1:
                Aspartate_Aminotransferase=st.text_input('Aspartate Aminotransferase in IU/L')
            with col2:
                Total_Protiens=st.text_input('Total Proteins g/dL')
            with col3:
                Albumin=st.text_input('Albumin in g/dL')
            with col1:
                Albumin_and_Globulin_Ratio=st.text_input('Albumin and Globulin ratio')
            liver_diagnosis=''
            if st.button("Liver Diesase Test Result"):
                user_input=[age,gender,Total_Billirubin,Direct_Bilirubin,Alkaline_Phosphotase,Alamine_Aminotransferase,Aspartate_Aminotransferase,Total_Protiens,Albumin,Albumin_and_Globulin_Ratio]
                user_input = [float(x) for x in user_input]
                liver_diagnosis, recommendations, medication_recommendation, additional_tests = liver_disease_prediction(user_input, st.session_state.username, st.session_state.email, st.session_state.phone)
                st.success(f"Liver Disease Test Result: {liver_diagnosis}")
                st.info(recommendations)
                if medication_recommendation:
                    st.info(f"Medication Recommendation: {medication_recommendation}")
                if additional_tests:
                    st.info(f"Suggested Additional Tests: {additional_tests}")
        else:
            st.write("Please login to access this feature.")

    #profile page
    elif selected == 'Profile':
        st.title("Profile")
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
        if st.session_state.logged_in:
            st.write("Welcome to your profile!")
            option = st.radio("Select an option:", ("View Profile", "Change Password","Edit Profile","Delete Account"))
            if option == "Change Password":
                # Show password change form
                st.write("Enter your new password below:")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    # Update password in the database
                    connection = connect_to_database()
                    cursor = connection.cursor()
                    cursor.execute("UPDATE users SET password = %s WHERE username = %s", (new_password, st.session_state.username))
                    connection.commit()
                    cursor.close()
                    connection.close()
                st.button("Password changed")
            elif option=="Edit Profile":
                edit_profile()
            elif option == "Delete Account":
                delete_account()  
            else:
                # Show user profile
                st.write(f"Username: {st.session_state.username}")
                st.write(f"Email: {st.session_state.email}")
                st.write(f"Phone: {st.session_state.phone}")
                # Fetch and display test results from the database
                connection = connect_to_database()
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM diabetes_test_results WHERE username=%s", (st.session_state.username,))
                diabetes_results = cursor.fetchall()
                cursor.execute("SELECT * FROM heart_disease_test_results WHERE username=%s", (st.session_state.username,))
                heart_disease_results = cursor.fetchall()
                cursor.execute("SELECT * FROM parkinsons_test_results WHERE username=%s", (st.session_state.username,))
                parkinsons_results = cursor.fetchall()
                cursor.execute("SELECT * FROM liver_disease_test_results WHERE username=%s",(st.session_state.username,))
                liver_disease_result=cursor.fetchall()
                # Fetch and display user's appointments
                cursor.execute("SELECT * FROM appointments WHERE username=%s", (st.session_state.username,))
                appointments = cursor.fetchall()
                connection.close()
                st.subheader("Test Results:")
                if diabetes_results:
                    st.write("**Diabetes Test Result:**", diabetes_results[-1][-1])  # Displaying the latest result
                else:
                    st.write("No diabetes test results available.")
                if heart_disease_results:
                    st.write("**Heart Disease Test Result:**", heart_disease_results[-1][-1])  # Displaying the latest result
                else:
                    st.write("No heart disease test results available.")
                if parkinsons_results:
                    st.write("**Parkinson's Test Result:**", parkinsons_results[-1][-1])  # Displaying the latest result
                else:
                    st.write("No Parkinson's disease test results available.")
                if liver_disease_result:
                    st.write("**Liver disease Test Result:**", liver_disease_result[-1][-1])  # Displaying the latest result
                else:
                    st.write("No Liver disease test results available.")
                st.subheader("Appointments:")
                if appointments:
                    for appointment in appointments:
                        st.write(f"Date: {appointment[4]}, Reason: {appointment[5]}")
                        if st.button(f"Delete Appointment No: {appointment[0]}"):
                           # Delete the appointment from the database
                            connection = connect_to_database()
                            cursor = connection.cursor()
                            cursor.execute("DELETE FROM appointments WHERE id=%s", (appointment[0],))
                            connection.commit()
                            connection.close()
                            st.write("Appointment deleted successfully!")
                else:
                    st.write("No appointments scheduled.")
                st.button("Logout", on_click=logout)
        else:
            st.write("Please login to view your profile.")
            login_or_signup = st.radio("Not registered yet? Signup here:", ("Login", "Signup"))
            if login_or_signup == "Login":
                login()
            else:
                signup()
    
    # Appointment Creation Page
    elif selected== 'Create Appointment':
        st.title('Create Appointment')
        if st.session_state.logged_in:
            with st.form(key='appointment_form'):
                col1, col2 = st.columns(2)
                with col1:
                    appointment_date = st.date_input('Appointment Date')
                with col2:
                    reason = st.text_area('Reason for Appointment')
                submit_button = st.form_submit_button('Create Appointment')
                if submit_button:
                    result = create_appointment(st.session_state.username, st.session_state.email, st.session_state.phone, appointment_date, reason)
                    st.success(result)
        else:
            st.write("Please login to access this feature.")

    
    # About Page
    elif selected == 'About':
        st.title('About Health Assistant')
        st.write("Health Assistant is a machine learning-powered application designed to assist in predicting the likelihood of specific health conditions.")
        st.write("It aims to provide users with quick and accessible predictions related to Diabetes, Heart Disease,Parkinson's Disease and Liver Disease.")
        st.subheader("Features:")
        st.write("- **Diabetes Prediction:** Predicts whether a person is diabetic or not based on input features.")
        st.write("- **Heart Disease Prediction:** Predicts the likelihood of having heart disease.")
        st.write("- **Parkinson's Disease Prediction:** Predicts whether a person has Parkinson's disease.")
        st.write("- **Liver Disease Prediction:** Predicts whether a person has Liver disease.")
        st.subheader("How it Works:")
        st.write("The application uses pre-trained machine learning models for each health condition.")
        st.write("Users input relevant health data, and the models make predictions based on this input.")
        st.write("The results are displayed on the respective prediction pages.")
        st.subheader("Disclaimer:")
        st.write("Health Assistant is not a substitute for professional medical advice, diagnosis, or treatment.")
        st.write("Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.")
    
    # Feedback Page
    elif selected == 'Feedback':
        st.title("Feedback Form")
        if st.session_state.logged_in:
            feedback_form(st.session_state.username)
        else:
            st.write("Please login to access this feature.")
    
    #Health assistant chatbot
    elif selected == "Health Assistant":
        st.subheader("Health Assistant Chatbot")
        st.write("Please type your question or query below:")
    
        message = st.text_input("You:", "")
    
        if st.button("Send"):
            response = health_assistant_chatbot(message)
            st.text_area("Health Assistant:", value=response, height=100)  # Display chatbot response
    else:
        st.write("Please select a valid option.")



# Run the main function if the script is executed
if __name__ == '__main__':
    main()

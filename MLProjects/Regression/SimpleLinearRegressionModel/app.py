import streamlit as st
import pickle
import numpy as np

#Load the trained model
model = pickle.load(open('C:\\Users\\roshn\\OneDrive\\Documents\\GitHub\\DataScience\\MLProjects\\Regression\\SimpleLinearRegressionModel\\LinearRegressionModel.pkl', 'rb'))

st.title("Salary Prediction based on Experience")

#Add brief description
st.write("This app predicts the salary of an individual based on their years of experience using a simple linear regression model.")    

#Add input field for years of experience
years_of_experience = st.number_input("Enter Years of Experience", min_value=0, max_value=50, value=5)  

#Make a prediction
if st.button("Predict Salary"):
    prediction = model.predict(np.array([[years_of_experience]]))
    st.success(f"Predicted Salary: ${prediction[0]:,.2f}")

    #Display the results
    st.write(f"Based on {years_of_experience} years of experience, the predicted salary is ${prediction[0]:,.2f}.") 
    
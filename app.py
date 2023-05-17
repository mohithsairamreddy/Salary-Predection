from flask import Flask, request, render_template
import os
import pickle as pickle
import requests
from bs4 import BeautifulSoup

app = Flask(__name__,template_folder="templates")  
env_config = os.getenv("PROD_APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if request.form['page'] == 'input':
            return render_template('input.html')
        elif request.form['page'] == 'predict':
            return render_template('calculate.html')
    return render_template('index.html')

with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

@app.route('/Salary', methods=['GET', 'POST'])
def Salary():
    if request.method == 'POST':
        # Get the input data from the form
        age = int(request.form['age'])
        gender = int(request.form['gender'])
        education = int(request.form['education'])
        job_title = int(request.form['job_title'])
        experience = int(request.form['experience'])

        # Make a prediction using the model
        input_data = [[age, gender, education, job_title, experience]]
        prediction = model.predict(input_data)[0]

        # Render the output template with the prediction
        return render_template('prediction.html', prediction=int(prediction))

    

@app.route('/Jobs_List', methods=['POST'])
def Jobs_List():
    job_role = request.form['job_role']
    location = request.form['location']
    job_type = request.form['job_type']
    experience = request.form['experience']

    url = f"https://www.linkedin.com/jobs/search/?keywords={job_role}&location={location}&f_TPR={job_type}&f_E={experience}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    job_listings = soup.find_all(class_="base-search-card__info")

    data = []
    for job in job_listings:
        title = job.find(class_="base-search-card__title").text.strip()
        company = job.find(class_="base-search-card__subtitle").text.strip()
        location = job.find(class_="job-search-card__location").text.strip()
        try:
            salary = job.find(class_="job-search-card__salary-info").text.strip()
        except:
            salary = "Not available"
        job_url = job.find("a")["href"]
        data.append({'title': title, 'company': company, 'location': location, 'salary': salary, 'url': job_url})

    return render_template('output.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
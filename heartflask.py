from flask import Flask, render_template, jsonify, request
import numpy as np
import pandas as  pd
import sklearn 
import json
import pickle as p 
import requests 


app  = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route("/heartprediction", methods = ['POST'])
def predictheart():
    data = request.get_json()
    prediction = np.array2string(model.predict(data))
    return jsonify(prediction)

@app.route("/heartcondition", methods = ['POST'])
def heartcondition():
    url = "http://localhost:5000/heartprediction"


    age = float(request.form["age"])
    sex = float(request.form["sex"])
    cp = float(request.form["cp"])
    trestbps = float(request.form["trestbps"])
    chol = float(request.form["chol"])
    fbs  = float(request.form["fbs"]) 
    restecg = float(request.form["restecg"])
    thalach = float(request.form["thalach"])
    exang = float(request.form["exang"])
    oldpeak = float(request.form["oldpeak"])
    slope = float(request.form["slope"])
    ca = float(request.form["ca"])
    thal = float(request.form["thal"])

    
    data = {"age":[age],"sex":[sex],"cp":[cp],"trestbps":[trestbps],"chol":[chol],
            "fbs":[fbs], "restecg":[restecg],"thalach":[thalach],"exang":[exang],
            "oldpeak":[oldpeak],"slope":[slope],"ca" : [ca],"thal":[thal]}

    data = pd.DataFrame(data)
    heart = pd.read_csv('heart.csv')
    x_test = heart.iloc[:,0:13]
    x_test = pd.concat([x_test,data],axis = 0)
    x_test = x_test.reset_index(drop = True) 
    # handling label data
    # ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'ca', 'thal']
    cat_col = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'ca', 'thal']
    x_test_new = pd.get_dummies(x_test, columns = cat_col)

    # scaling
    # ["age", "trestbps", "chol", "thalach", "oldpeak"]
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    scale_col = ["age", "trestbps", "chol", "thalach", "oldpeak"]
    x_test_new[scale_col] = scaler.fit_transform(x_test[scale_col]) 

    a = x_test_new.iloc[-1,:]
    new_data = []
     
    for i in range(len(a.index)):
        new_data.append(a[i])

    new_data = [new_data]
    j_data = json.dumps(new_data)

    headers = {'content-type':'application/json','Accept-Charset':'UTF-8'}
    r = requests.post(url, data = j_data, headers = headers)
    r1 = list(r.text)
    stat = ""

    if r1[2] == str(0):
        stat = "patient is not affected with heart disease"
    elif r1[2] == str(1):
        stat = "patient is affected with heart disease"
    else:
        stat = "Error in encoding input"

    return render_template("result.html", result = stat)

if __name__ == '__main__':

    model_file='heart_disease.pickle'
    model=p.load(open(model_file,'rb'))
    app.run(debug = True, host = '0.0.0.0')

    
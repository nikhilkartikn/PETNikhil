from flask import Flask, render_template, request, redirect, url_for, Response,session
import requests
import json
import random
import time
from datetime import datetime
from datetime import timedelta


app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes = 15)
app.secret_key = "hggsfdsffjg"
random.seed()  # Initialize the random number generator


# Function to add a specific expense for a user - AWS API Add Expense for a user
def setExpenses(params): 
    print(params)
    url = "https://8l94nd81q0.execute-api.us-east-1.amazonaws.com/API_deploy_push_expense_data?"+params
    status = requests.request("GET",url)
    print(type(status))
    print(status.json())
    return status.json()

# Function to fetch expenses of a user - AWS API Expense Summary
def fetchExpenses(params):
    url="https://ho7nzjgyl3.execute-api.us-east-1.amazonaws.com/API_deploy_fetchexpensedata?"+params
    status = requests.request("GET",url)
    print(status.json())
    return status.json()

# Function to fetch wallet balance - AWS API Wallet Balance
def walletBalance(params):
    url="https://y8becolo7a.execute-api.us-east-1.amazonaws.com/API_deploy_retrieve_walletbalance?"+params
    print(url)
    status = requests.request("GET",url)
    print(status.json())
    return status.json()


# Function to check user credentials - AWS API User Details
def check(user):
    url="https://rskojd57v6.execute-api.us-east-1.amazonaws.com/API_deploy_fetchUserDetails?user="+user  
    status = requests.request("GET",url)
    print(status.json())
    return status.json()

# Function to add amount to wallet - AWS API Add Money to Wallet
def updatewallet(params):
    url="https://mdxaatgdq5.execute-api.us-east-1.amazonaws.com/API_deploy_add_money_to_wallet?"+params 
    print(url)
    status = requests.request("GET",url)
    print(status.json())
    return status.json()

@app.route('/')
@app.route('/home')
def home():
    title = "Personal Expense Tracker"
    
    return render_template("dchart.html", title = title)

@app.route('/chart-data')
def dchart():
    def generate_random_data():
        while True:
            json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': random.random() * 100})
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')

@app.route('/wallet')
def wallet():
    return render_template('addmoney.html')

# Function to fetch current wallet balance - AWS API Wallet Balance
@app.route('/dashboard')
def dashboard():
    print(session["user"])
    user = session["user"] 
    params="user="+user
    print(params)
    data=walletBalance(params)
    print(type(data))
    #print(data)
    result = data.split("+")
    wbalance=result[0] 
    message=result[1]
    print(wbalance,message)    
    if('errorType' in result):
          return render_template('login.html', pred="Wallet could not be updated. Your wallet balance has not changed.")
    else:
        return render_template('dashboard.html', pred=wbalance, message=message)

# Function to add amount to wallet - AWS API Add money to wallet
@app.route('/addmoneypage', methods=['GET','POST'])
def addmoneypage() :
    if request.method == 'POST':
        user=request.form['user']
        amount = request.form['amount']
        print(user)
        print(amount)
        #Add validation to user and amount fields before submit
        params = "user="+user+"&amount="+amount
        print(params)
        data = updatewallet(params)
        print(type(data))
    
    if('errorType' in data):
        return render_template('addmoney.html', pred="Wallet could not be updated. Your wallet balance has not changed.")
    else:
        return render_template('addmoney.html', pred="Wallet has been updated successfully and your "+data)
    

@app.route("/chart", methods=['GET','POST'])
def chart():
    user=session["user"]
    #expense_date_from='a'
    #expense_date_to='b'
    params = "user="+user   #+"&expense_date_from="+expense_date_from+"&expense_date_to="+expense_date_to
    print(params)
    series_new=fetchExpenses(params)
    print(type(series_new))
    exp_dates = []
    for d in series_new:
        for k,v in d.items():
            if k == 'user+date':
                temporary = v.split("+")
                exp_dates.append(temporary[1])
    print(exp_dates)
    home_expenses = []
    for d in series_new:
        for k,v in d.items():
            if k == 'home_expenses':
                home_expenses.append(int(v))
    print(home_expenses)
    medical_expenses = []
    for d in series_new:
        for k,v in d.items():
            if k == 'medical_expenses':
                medical_expenses.append(int(v))
    print(medical_expenses)
    vehicle_expenses = []
    for d in series_new:
        for k,v in d.items():
            if k == 'vehicle_expenses':
                vehicle_expenses.append(int(v))
    print(vehicle_expenses)
    travel_expenses = []
    for d in series_new:
        for k,v in d.items():
            if k == 'travel_expenses':
                travel_expenses.append(int(v))
    food_expenses = []
    for d in series_new:
        for k,v in d.items():
            if k == 'food_expenses':
                food_expenses.append(int(v))
    
    legend1 = 'Home Expenses'
    legend2 = 'Vehicle Expenses'
    legend3 = 'Medical Expenses'
    legend4 = 'Travel Expenses'
    legend5 = 'Food Expenses'
    labels = exp_dates             
    
    return render_template('chart.html', labels=labels, legend1=legend1, legend2=legend2, legend3=legend3,legend4=legend4,legend5=legend5, home_expenses=home_expenses, vehicle_expenses= vehicle_expenses, medical_expenses=medical_expenses, travel_expenses = travel_expenses,food_expenses = food_expenses)
 
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/loginpage', methods=['POST'])
def loginpage():
    user = request.form['user']
    passw = request.form['passw']
    print(user,passw)
    data = check(user)
    print(type(data))
    checker = isinstance(data,str) #written to check whether a particular value is a string or not. Returns true or false
    #print(type(checker))
    #print(str(checker))
    if(checker == True):
        print("why the hell am i coming here")
        return render_template('login.html', pred="The username is not found, recheck the spelling or please register.")
    else:
        if(passw==data['passw']):
            session.permanent = True #session timelimit
            session["user"] = user
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', pred="Login unsuccessful. You have entered the wrong password.")
    
@app.route('/expense')
def expense():
    return render_template('expense.html')

@app.route('/expensepage', methods=['POST'])
def expensepage() :
    user=request.form['user']
    expensedate = request.form['expensedate']
    category = request.form['expensetype']
    expenseamount = request.form['expenseamount']
    if request.method == 'POST':
        # Check which type of expense is being updated
        if(category=='medical_expenses'):
            #medical_expenses = request.form['expenseamount']
            params = "user="+user+"&expensedate="+expensedate+"&medical_expenses="+expenseamount+"&home_expenses="+"0"+"&vehicle_expenses="+"0"+"&travel_expenses="+"0"+"&food_expenses="+"0"
        elif(category=='home_expenses'):
            #home_expenses = request.form['expenseamount']
            params = "user="+user+"&expensedate="+expensedate+"&medical_expenses="+"0"+"&home_expenses="+expenseamount+"&vehicle_expenses="+"0"+"&travel_expenses="+"0"+"&food_expenses="+"0"
        elif(category=='vehicle_expenses'):
            #vehicle_expenses = request.form['expenseamount']
            params = "user="+user+"&expensedate="+expensedate+"&medical_expenses="+"0"+"&home_expenses="+"0"+"&vehicle_expenses="+expenseamount+"&travel_expenses="+"0"+"&food_expenses="+"0"
        elif(category=='travel_expenses'):
            params =  "user="+user+"&expensedate="+expensedate+"&medical_expenses="+"0"+"&home_expenses="+"0"+"&vehicle_expenses="+"0"+"&travel_expenses="+expenseamount+"&food_expenses="+"0"
        elif(category=='travel_expenses'):
            params =  "user="+user+"&expensedate="+expensedate+"&medical_expenses="+"0"+"&home_expenses="+"0"+"&vehicle_expenses="+"0"+"&travel_expenses="+"0"+"&food_expenses="+expenseamount
        else:
            render_template('expense.html', pred="Expense type is unauthorized in system.")

        response = setExpenses(params)

        json_object = json.dumps(response)
        print(json_object)
        if('errorType' in json_object):
            return render_template('expense.html', pred="Expense could not be added. Your wallet balance has not changed.")
        else:
            return render_template('expense.html', pred=str(json_object))
    	     
	
@app.route('/registration')
def registration():
    return render_template('register.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        user = request.form.get('user')
        phone = request.form.get('phone')
        city = request.form.get('city')
        occupation = request.form.get('occupation')
        passw = request.form.get('passw')
        params="name="+name+"&user="+user+"&phone="+phone+"&city="+city+"&occupation="+occupation+"&passw="+passw
        print(params)
        data = check(user)
        res = isinstance(data,str)
        if(str(res)):
            url = "https://kuyucjcq7a.execute-api.us-east-1.amazonaws.com/API_deploy_register_userinfo?"+params
            response = requests.request("GET",url)
            print(response.json())
            return render_template('login.html', pred="Registration Successful, please login using your details")
        else:
            return render_template('register.html', pred="You are already a member, please login using your details")
        
@app.route("/logout")
def logout():   
   #logout_user()        # Delete Flask-Login's session cookie       
   session.pop("user", None)
   return redirect(url_for('login'))        

if __name__ == "__main__":
	app.run(host='0.0.0.0',port='8060')

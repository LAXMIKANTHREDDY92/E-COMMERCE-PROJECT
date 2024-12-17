from flask import Flask,render_template,request
import random
from  pymysql import connect
#importing libraries for email otp verification
import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import razorpay
razorpay_key_id="rzp_test_KyBKn0VlKMhbk8"
razorpay_key_secret="ulGP1iuLM5ILr2joF6tPBnAC"
client=razorpay.Client(auth=(razorpay_key_id,razorpay_key_secret))

verifyotp="0"
db_config= {
    'host' : "localhost" ,
    'database' :'royalshop' ,
    'user' : 'root' ,
    'password' : 'Klkr@123'
}

app = Flask(__name__)
@app.route("/")
def landing():
    return render_template("home.html")

@app.route("/home")
def home():
    return render_template("home.html")

#creating routes for contact  pages
@app.route("/contactus")
def contactus():
    return render_template("contactus.html")

#creating route for about us page:
@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/registerdata",methods=['POST','GET'])
def registerdata():
    if request.method=='POST':
       name=request.form['name']
       username=request.form['username']
       email=request.form['email']
       mobile=request.form['mobile']
       password=request.form['password']
       cpassword=request.form['confirm-password']
       if password == cpassword:
           otp=random.randint(111111,999999)
           global verifyotp 
           verifyotp = str(otp)


           smtp_server = 'smtp.gmail.com'
           smtp_port = 587
           mailusername = '21eg506206@anurag.edu.in'
           mailpassword = 'yswv fmir jnrd rbay'
           from_email = '21eg506206@anurag.edu.in'
           to_email = email
           subject = "otp for verification"
           body = f'The otp for login is {verifyotp}'

           msg =  MIMEMultipart()
           msg['From'] = from_email
           msg['To'] = to_email
           msg['subject'] = subject
           msg.attach(MIMEText(body,'plain'))

           server = smtplib.SMTP(smtp_server,smtp_port)
           server.starttls()
           server.login(mailusername,mailpassword)
           server.send_message(msg)
           server.quit()

           return render_template("verifyemail.html",name=name,username=username,email=email,mobile=mobile,password=password)
       else:
           return "make sure password and cpassword to be same"
    else:
        return "<h3>Data got in wrong manner</h3>"

@app.route("/verifyemail",methods=['POST','GET'])
def verifyemail():
    if request.method == 'POST':
        name=request.form['name']
        username =request.form['username']
        email=request.form['email']
        mobile=request.form['mobile']
        password=request.form['password']
        otp = request.form['otp']
        if otp == verifyotp:
            try:
                conn = connect(**db_config)
                cursor = conn.cursor()
                q="insert into users values (%s,%s,%s,%s,%s)"
                cursor.execute(q,(name,username,email,mobile,password))
                conn.commit()
            except:
                return "error occured while storing the data in database or user already exists"
            else:
                return render_template('login.html')
        else:
            return 'wrong otp'

    else:
        return  "<h3 style='color:red'>Data got in wrong manner</h3>"
    
@app.route("/userlogin",methods = ['POST','GET'])
def userlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = connect(**db_config)
            cursor = conn.cursor()
            q = "select * from users where username = (%s)"
            cursor.execute(q,(username))
            row = cursor.fetchone()
            if row == None:
                return 'User doesnot exist, Create account first..!'
            else:
                if row[4] != password:
                    return 'wrong password !' 
                else:
                    return render_template("userhome.html",name=username)

        except:
            return 'error occurred while retrieving data'
        
    else:
        return "data occured in incorect way"

@app.route("/add_to_cart",methods = ["POST","GET"])
def add_to_cart():
    if request.method == 'POST':
        username = request.form['username']
        productname = request.form['productname']
        quantity = request.form['quantity']
        price = request.form['price']
        totalprice = int(quantity)*int(price)
        totalprice=str(totalprice)
        try:
            conn=connect(**db_config)
            cursor = conn.cursor()
            q="insert into cart values (%s,%s,%s,%s,%s)"
            cursor.execute(q,(username,productname,quantity,price,totalprice))
            conn.commit()
        except:
            return "error occured while storing data into database"
        else:
            return render_template("userhome.html",name=username)

    else:
        return "data occured in incorrect way"
    
@app.route("/cartpage",methods=['GET'])
def cartpage():
    username = request.args.get('username')
    try:
        conn = connect(**db_config)
        cursor = conn.cursor()
        q = "select * from cart where username =(%s)"
        cursor.execute(q,(username))
        rows = cursor.fetchall()
        print(rows)
        subtotal=0
        for i in rows:
            subtotal = subtotal + int(i[4])
        result=subtotal * 100
        order=client.order.create({
            'amount' : result,
            'currency':'INR',
            'payment_capture' : '1'
        })
        print(order)
    except:
        return 'error occurred while retrieving the data'
    else:
        return render_template("cart.html",data=rows,grandtotal=subtotal,order=order)
@app.route("/sucess",methods=["POST","GET"])
def sucess():
    payment_id = request.form.get("razorpay_payment_id")
    order_id = request.form.get("razorpay_order_id")
    signature=request.form.get("razorpay_signature")
    dict1={
        'razorpay_order_id':order_id,
        'razorpay_payment_id':payment_id,
        'razorpay_signature':signature
    }
    try:
        client.utility.verify_payment_signature(dict1)
        return render_template('success.html')
    except:
        return render_template('failed.html')

if __name__ == "__main__":
    app.run(port=5006)

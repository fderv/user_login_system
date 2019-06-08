from flask import Flask, render_template, request, redirect, url_for, session
from flaskext.mysql import MySQL

import bcrypt

mysql = MySQL()

app = Flask(__name__)
app.secret_key = 'abc123'
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_PERMANENT"] = False

app.config['MYSQL_DATABASE_HOST'] = 'WILL_BE_REPLACED'
app.config['MYSQL_DATABASE_USER'] = 'WILL_BE_REPLACED'
app.config['MYSQL_DATABASE_PASSWORD'] = 'WILL_BE_REPLACED'
app.config['MYSQL_DATABASE_DB'] = 'WILL_BE_REPLACED'
mysql.init_app(app)

conn = mysql.connect()


if __name__ == '__main__':
    app.run(debug=True)

@app.route('/mainpage.html', methods=["GET", "POST"])
def home():
    cur = conn.cursor()
    if request.method == 'POST':
        pass_o = request.form['passwordo']
        pass_n = request.form['passwordn']
        if bcrypt.hashpw(pass_o.encode('utf-8'), session['hashpass']) == session['hashpass'] and pass_n != "":
            values = (bcrypt.hashpw(pass_n.encode('utf-8'), session['hashpass'].encode('utf-8')), session['hashpass'].encode('utf-8'))
            cur.execute("UPDATE user_table SET password = %s WHERE password= %s;", values)
            conn.commit()
            return redirect(url_for("main"))
        else:
            return render_template("mainpage.html")
    else:
        return render_template("mainpage.html")

@app.route('/', methods=["GET", "POST"])
def main():
    cur = conn.cursor()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        cur.execute("SELECT * FROM user_table WHERE username=%s",username)
        userCount = cur.rowcount
        user = cur.fetchone()

        if userCount != 0:
            if bcrypt.hashpw(password, user[1].encode('utf-8')) == user[1]:
                session['username'] = user[0]
                session['email'] = user[2]
                session['phone'] = user[3]
                session['city'] = user[4]
                session['hashpass'] = user[1]
                return redirect(url_for('home'))
            else:
                return render_template("index.html", error="Incorrect password")
        else:
            return render_template("index.html", error="Incorrect username or password")

    else:
        return render_template('index.html')




@app.route('/signup', methods=["GET","POST"])
def signup():
    cur = conn.cursor()
    if request.method == 'GET':
        return render_template("signup.html", error="")
    else:

        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        city = request.form['city']

        cur.execute("SELECT COUNT(username) FROM user_table WHERE username=%s", username)
        countOfUsername = cur.fetchone()[0]

        cur.execute("SELECT COUNT(username) FROM user_table WHERE email='"+email+"'")
        countOfEmail = cur.fetchone()[0]
        if countOfUsername > 0 or countOfEmail > 0 or username=="" or email== "":
            return render_template("signup.html", error="Error")
        else:
            password = request.form['password'].encode('utf-8')
            hash_password = bcrypt.hashpw(password, bcrypt.gensalt())


            insert = "INSERT INTO user_table (username, password, email, phone, city)" \
                     "VALUES (%s, %s, %s, %s, %s)"
            data = (username, hash_password, email, phone, city)
            cur.execute(insert, data)
            conn.commit()
            session['username'] = username
            session['email'] = email
            return redirect(url_for("main"))

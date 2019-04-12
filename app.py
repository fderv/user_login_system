from flask import Flask, render_template, request, redirect, url_for, session
from flaskext.mysql import MySQL
import bcrypt

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '724672'
app.config['MYSQL_DATABASE_DB'] = 'user_info'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql.init_app(app)

@app.route('/', methods=["GET", "POST"])
def main():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        cur = mysql.get_db().cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM user_table WHERE username=%s", (username))
        user = cur.fetchone()
        cur.close()

        if len(user) > 0:
            if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"]:
                session['username'] = user['username']
                session['email'] = user['email']
                return render_template("home.html")
            else:
                return render_template("index.html", error="Incorrect password")
        else:
            return render_template("index.html", error="Incorrect username")

    else:
        return render_template('index.html')




@app.route('/signup', methods=["GET","POST"])
def signup():
    if request.method == 'GET':
        return render_template("signup.html", error="")
    else:

        cur = mysql.get_db().cursor()
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        city = request.form['city']

        cur.execute("SELECT COUNT(username) FROM user_table WHERE username='"+username+"'")
        countOfUsername = cur.fetchone()[0]

        cur.execute("SELECT COUNT(username) FROM user_table WHERE email='"+email+"'")
        countOfEmail = cur.fetchone()[0]
        if countOfUsername > 0 or countOfEmail > 0 or username=="" or email== "":
            return render_template("signup.html", error=str(countOfEmail)+" "+str(countOfUsername))
        else:
            password = request.form['password'].encode('utf-8')
            hash_password = bcrypt.hashpw(password, bcrypt.gensalt())


            insert = "INSERT INTO user_table (username, password, email, phone, city)" \
                     "VALUES (%s, %s, %s, %s, %s)"
            data = (username, hash_password, email, phone, city)
            cur.execute(insert, data)
            mysql.get_db().commit()
            session['username'] = username
            session['email'] = email
            return redirect(url_for("main"))

if __name__ == '__main__':
    app.secret_key = "ABC123"
    app.run(debug=True)

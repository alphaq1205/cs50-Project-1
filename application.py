import os
from flask import Flask, session, redirect, url_for, render_template, request
import requests
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "secretkey"
#Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

avg_rating=''
work_rating=''
title=''
author=''
year=''
isbn=''
b_id=''
u_id=''


""" *********************************************DATA INSERTION:- CSV TO SQL**************************************************** """


@app.route('/insert')
def insert():
    f = open('books.csv')
    reader = csv.reader(f)
    for isbn,title,author,years in reader:
        db.execute("INSERT INTO books(isbn,title,author,years) VALUES(:isbn, :title, :author, :years)",
                    {"isbn": isbn, "title": title, "author": author, "years": years})
        print(f'isbn: {isbn}  title: {title} author: {author} year: {years}')
        db.commit()
        



''' ************************************************FRONT PAGE MODULE***********************************************************'''


@app.route("/")
def index():
    return render_template('front_page.html')


''' ********************************************LOGIN MODULE********************************************************************* '''


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def loginData():
    useremail = request.form.get('email')
    userpassword = request.form.get('password')
    userData = db.execute('SELECT * FROM users WHERE email=:email and password=:password',{'email':useremail, 'password':userpassword}).fetchall()
    
    if(userData):
        for udata in userData:
            u_id=udata.id
            session['u_id']=udata.id   
        return redirect('homepage')
    else:
        print('no result found')
        fmsg='email or password is incorrect try again'
        return render_template('login.html',fail_message=fmsg)
    

''' **************************************************REGISTRATION MODULE******************************************************** '''


@app.route('/registration',methods=['GET'])
def register():
    return render_template('registration.html')


@app.route('/registration', methods=['POST'])
def regData():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    db.execute("INSERT INTO users(name,email,password) VALUES(:name, :email, :password)",
                    {'name':name, 'email':email, 'password':password})
    db.commit()
    msg='you have successfully registered'
    return redirect(url_for('login',message=msg))     


''' *****************************************************HOMEPAGE********************************************************************* '''


@app.route('/homepage')
def homepage():
    if('u_id' in session):
        return render_template('table.html')
    else:
        return render_template('error.html')



''' *****************************************************SEARCH FILTER MODULE************************************************************ '''


@app.route('/homepage',methods=['POST'])
def filterData():
    if('u_id' in session):
        searchData = request.form.get('search')
        booksData = db.execute('SELECT * FROM books WHERE isbn=:isbn or title=:title or author=:author or years=:years',{'isbn':searchData, 'title':searchData, 'author':searchData, 'years':searchData}).fetchall()
        filterData = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn or title LIKE :title or author LIKE :author or years LIKE :years ",{'isbn':'%'+searchData+'%', 'title':'%'+searchData+'%', 'author':'%'+searchData+'%', 'years':'%'+searchData+'%'}).fetchall()
        if(booksData):
            return render_template('table.html',filterData=booksData)
        elif(filterData):
            return render_template('table.html',filterData=filterData)
        else:
            fmsg='No Data Found'
            return render_template('table.html',fail_tmsg=fmsg) 
    else:
        return render_template('error.html')

""" ********************************************************BOOK DETAIL MODULE************************************************************ """


@app.route('/bookdetail/<string:isbn>')
def bdetails(isbn):
    if('u_id' in session):
        bookData = db.execute('SELECT * FROM books WHERE isbn=:isbn',{'isbn':isbn}).fetchall()
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "V17OhDrftCbEGpN1WmWIA", "isbns": isbn})
        x=res.json()['books']
        if(bookData and res.json()):
            for data in x:
                avg_rating=data['average_rating']
                work_rating=data['work_ratings_count']
            for data in bookData:
                title=data.title
                author=data.author
                year=data.years
                isbn=data.isbn
                session['b_id']=data.id
                session['b_isbn']=data.isbn
            
            
            u_id=session['u_id'];
            b_id=session['b_id'];
            b_isbn=session['b_isbn']
            rvdata=db.execute("SELECT * FROM books JOIN comments ON comments.rbid = books.id;")
            rb_dta=[]
            us_dta=[]
            rid=''
            for x in rvdata:
                if(x.isbn==isbn):
                    usdta=db.execute("SELECT * FROM users WHERE id = :usid;",{'usid':x.ruid})
                    for z in usdta:
                        us_dta.append(z)
                    rb_dta.append(x)
                if(x.ruid==u_id and x.rbid==b_id):
                    rid=x.id
            return render_template('bookDetails.html',bookdtl=bookData,avg_rate=avg_rating,work_rate=work_rating,rbdata=rb_dta,rvid=rid)
        else:
            return render_template('error.html')
    else:
        render_template('error.html')


@app.route('/book/detail/api/<string:isbn>')
def testapi(isbn):
    if('u_id' in session):
        bookData = db.execute('SELECT * FROM books WHERE isbn=:isbn',{'isbn':isbn}).fetchall()
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "V17OhDrftCbEGpN1WmWIA", "isbns": isbn})
        x=res.json()['books']
        if(bookData and res.json()):
            for data in x:
                avg_rating=data['average_rating']
                work_rating=data['work_ratings_count']
            for data in bookData:
                title=data.title
                author=data.author
                year=data.years
                isbn=data.isbn
        bookData={
            "title": title,
            "author": author,
            "year": year,
            "isbn": isbn,
            "review_count": work_rating,
            "average_score": avg_rating,
        }
        return bookData
    else:
        return render_template('error.html')


""" *****************************************************SUBMIT REVIEW********************************************************************* """


@app.route('/submit/review',methods=['POST'])
def submitReview():
    if('u_id' in session):  
        rating=request.form.get('b_rate')
        review=request.form.get('b_review')
        u_id=session['u_id'];
        b_id=session['b_id'];
        b_isbn=session['b_isbn']
    
        reviewConf=db.execute("SELECT * FROM comments WHERE ruid=:u_id AND rbid=:b_id",{'u_id':u_id, 'b_id':b_id}).fetchall()
        if(reviewConf):
            for data in reviewConf:
                f_msg='You cannot submit your review more than one time'
                return redirect(url_for('bdetails',isbn=b_isbn))
        else:
            usdata=db.execute("SELECT * FROM users WHERE id=:u_id",{'u_id':u_id})
            userName=''
            for data in usdata:
                userName=data.name
            db.execute("INSERT INTO comments(ruid, name, rbid, rating, review) VALUES(:ruid, :name, :rbid, :rating, :review)",
                        {'ruid':u_id, 'name':userName, 'rbid':b_id, 'rating':rating, 'review':review})
            db.commit()
            s_msg='you have successfylly submited your review'
            return redirect(url_for('bdetails',isbn=b_isbn))
    else:
        return render_template('error.html')

""" ************************************DELETE REVIEW************************************************************** """


@app.route('/delete/review/<string:rid>')
def deleteReview(rid):
    if('u_id' in session):
        u_id=session['u_id'];
        b_id=session['b_id'];
        b_isbn=session['b_isbn']
        irid=int(rid)
        db.execute("DELETE FROM comments WHERE id = :usid",{'usid':irid})
        db.commit()
        return redirect(url_for('bdetails',isbn=b_isbn))
    else:
        return render_template('error.html')

""" *************************************UPDATE REVIEW*************************************************************** """


@app.route('/update/page')
def updateReview():
    if('u_id' in session):
        u_id=session['u_id']
        b_id=session['b_id']
        b_isbn=session['b_isbn']
        rvdata=db.execute("SELECT * FROM books JOIN comments ON comments.rbid = books.id;")
        rid=''
        for data in rvdata:
            if(data.ruid==u_id and data.rbid==b_id):
                rid=data.id
                return render_template('updateReview.html',review=data.review,rid=data.id)
    else:
        return render_template('error.html')

@app.route('/update/review/<string:urid>',methods=['POST'])
def updateReviewData(urid):
    if('u_id' in session):
        urating=request.form.get('b_rate')
        ureview=request.form.get('b_review')
        b_isbn=session['b_isbn']
        u_rid=int(urid)
        db.execute('UPDATE comments SET review = :ureview, rating = :urating WHERE id = :urid;',{'ureview':ureview, 'urating':urating, 'urid':u_rid})
        db.commit()
        return redirect(url_for('bdetails',isbn=b_isbn))
    else:
        return render_template('error.html')

""" *************************************LOGOUT********************************************************************* """


@app.route('/logout')  
def logout():  
    if 'u_id' in session:  
        session.pop('u_id',None)  
        session.pop('b_id',None)  
        session.pop('b_isbn',None)  
        return redirect(url_for('index'));  
    else:  
        return render_template('error.html')
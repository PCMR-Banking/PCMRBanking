from flask import render_template, flash, redirect, url_for, request, session, jsonify, abort
from flask_login.utils import logout_user
from app import app, db, mail, response
from app.forms import LoginForm, RegistrationForm, EditProfileForm, AccountForm, EditAccountForm, ContactForm
from flask_login import current_user, login_user, login_required
from app.models import User, Accounts
from werkzeug.urls import url_parse
from datetime import datetime
import pyqrcode
from io import BytesIO, StringIO
from flask_mail import Message
from app.email import send_email
import re
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
# import os


@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.username.data.lower()
        user = User.query.filter_by(username=email).first()
        if user is None or not user.check_password(form.password.data) or \
            not user.verify_totp(form.token.data):
            flash('Invaild username, password or token')
            return redirect(url_for('login'))
        if user.deleted:
            abort(404)
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.username.data.lower()
        user = User.query.filter_by(username=email).first()
        if user is not None:
            flash('Username already exists.')
            return redirect(url_for('register'))
            
        email = form.username.data.lower()
        user = User(username=email)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # redirect to the two-factor auth page, passing username in session
        session['username'] = user.username
        return redirect(url_for('two_factor_setup'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    user = User.query.get_or_404(current_user.ID)
    if user.deleted:
        abort(404)

    if request.method == 'POST':
        if request.form.get('deleteCheck'):
            username = request.form['deleteEmail']
            email = username.lower()
            if user.username != email:
                flash("Can't confirm the deletion...")
                return redirect(url_for('user'))
            else:
                accounts = Accounts.query.filter_by(ownerID=user.ID).all()
                for a in accounts:
                    a.deleted = True
                    db.session.add(a)
                user.deleted = True
                db.session.commit()
                return redirect(url_for('logout'))

    return render_template('user.html', user=user)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.cellphone = form.cellphone.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.cellphone.data = current_user.cellphone
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route('/twofactor')
def two_factor_setup():
    if 'username' not in session:
        return redirect(url_for('index'))
    user = User.query.filter_by(username=session['username']).first()
    if user is None:
        return redirect(url_for('index'))

    # since this page contains the sensitive qrcode, make sure the browser
    # does not cache it
    return render_template('two-factor-setup.html'), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@app.route('/qrcode')
def qrcode():
    if 'username' not in session:
        abort(404)
    user = User.query.filter_by(username=session['username']).first()
    if user is None:
        abort(404)

    # for added security, remove username from session
    del session['username']
    
    # render qrcode for FreeTOTP
    url = pyqrcode.create(user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=3)
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/credit')
def credit():
    return render_template('credit.html')

@app.route('/contactus', methods=['GET', 'POST'])
def contactus():
    form = ContactForm()

    if request.method == 'POST':
        if form.validate_on_submit() == False:
            flash('All fields are required.')
            return render_template('contactus.html', form=form)
        else:
            msg = Message('CONTACT US FORM FROM: ' + form.email1.data, sender='pcmrbank@gmail.com', recipients=['banking@vaehaaland.no'])
            msg.body = """
            From: %s 
            Email: %s
            Subject: %s
            Message: %s
            """ % (form.name1.data, form.email1.data, form.subject1.data, form.message1.data)
            mail.send(msg)
            
    
        return render_template('contactus.html', success=True)
    
    elif request.method == 'GET':
        return render_template('contactus.html', form=form)
    
@app.route('/stocks')
def stocks():
    return render_template('stocks.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user = current_user
    if user is None or user.deleted:
        abort(404)
    form = AccountForm()
    if form.validate_on_submit():
        account = Accounts(owner=current_user, AccountName=form.AccountName.data, AccountType=form.AccountType.data, \
            AccountBalance=form.AccountBalance.data)
        db.session.add(account)
        db.session.commit()
        flash('Your new account is activated!')
        accounts = Accounts.query.filter_by(ownerID=user.ID).filter_by(deleted=False).all()
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        if 'accID' in request.form:
            accID = int(request.form.get('accID'))
            accounts = Accounts.query.filter_by(ID=accID).first()
            session['editAccID'] = accID
            return redirect(url_for('edit_acc'))
        elif 'from' in request.form:
            fromAccID = int(request.form.get('from'))
            fromAccInfo = Accounts.query.filter_by(ID=fromAccID).first()
            Amount = int(request.form['money'])
            if Amount is None:
                abort(404)
            if fromAccInfo.AccountBalance < Amount:
                flash("Insufficient funds")
            else:
                toAcc = request.form.get('toAcc')
                toAccformat = re.sub('[^\w]', '', toAcc)
                if toAccformat is None:
                    abort(404)
                toAccInfo = Accounts.query.filter_by(ID=toAccformat).first_or_404()
                fromAccInfo.AccountBalance -= Amount
                toAccInfo.AccountBalance += Amount
                db.session.commit()
                flash('Transfer successful!')

        return redirect(url_for('dashboard'))
    
    accounts = Accounts.query.filter_by(ownerID=user.ID).filter_by(deleted=False).all()
    return render_template('dashboard.html', user=user, accounts=accounts, form=form)



@app.route('/edit_acc', methods=['GET', 'POST'])
@login_required
def edit_acc():
    account = Accounts.query.filter_by(ID=session['editAccID']).first()
    del session['editAccID']
    form = EditAccountForm()
    if form.validate_on_submit():
        account.AccountName = form.AccountName.data
        account.AccountType = form.AccountType.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_acc'))
    elif request.method == 'GET':
        form.AccountName.data = account.AccountName
        form.AccountType.data = account.AccountType
    return render_template('edit_acc.html', title='Edit Account',
                           form=form)

@app.route('/delete_acc', methods=['GET', 'POST'])
@login_required
def delete_acc():
    user = current_user
    if user is None or user.deleted:
        abort(404)
    accounts = Accounts.query.filter_by(ownerID=user.ID).filter_by(deleted=False).all()
    if request.method == 'POST':
        accID = int(request.form['accID'])
        if request.form.get('deleteCheck'):
            account = Accounts.query.filter_by(ID=accID).first()
            account.deleted = True
            db.session.commit()
            return redirect(url_for('dashboard'))
   
    return render_template('delete_acc.html', title='Delete Account', accounts=accounts)


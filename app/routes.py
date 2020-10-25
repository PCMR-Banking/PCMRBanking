from flask import render_template, flash, redirect, url_for, request, session, jsonify
from flask_login.utils import logout_user
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, AccountForm, EditAccountForm
from flask_login import current_user, login_user, login_required
from app.models import User, Accounts
from werkzeug.urls import url_parse
from datetime import datetime
import pyqrcode
from io import BytesIO, StringIO
from os import abort

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
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
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            flash('Username already exists.')
            return redirect(url_for('register'))
            
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # redirect to the two-factor auth page, passing username in session
        session['username'] = user.username
        return redirect(url_for('two_factor_setup'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user')
@login_required
def user():
    user = current_user
    return render_template('user.html', user=user)

@app.route('/user', methods=['DELETE'])
def delete_user(current_user):
    user = User.query.get_or_404(current_user.ID)
    accounts = Accounts.query.filter_by(ownerID=user.ID).all()
    if user.deleted:
        abort(404)
    user.deleted = True
    db.session.commit()
    return '', 204

@app.route('/user', methods=['GET'])
def get_user(current_user):
    user = User.query.get_or_404(current_user.ID)
    if user.deleted:
        abort(404)
    return jsonify(user.to_dict())

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.cellphone = form.cellphone.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
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
    return render_template('Credit.html')

@app.route('/contactus')
def contactus():
    return render_template('/contactus.html')
    
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
        accounts = Accounts.query.filter_by(ownerID=user.ID).all()
        return redirect(url_for('dashboard'))
    # accounts = [
    #     {
    #         'ID': 13376942069,
    #         'owner': {'username': 'alha@tester.no'},
    #         'AccountName': 'Big Brain',
    #         'AccountBalance': 500,
    #         'AccountType': "Standard Account"
    #     },
    #     {
    #         'ID': 13376942070,
    #         'owner': {'username': 'alha@tester.no'},
    #         'AccountName': 'Smol PP',
    #         'AccountBalance': 500,
    #         'AccountType': "Standard Account"
    #     },
    # ]

    if request.method == 'POST':
        if 'accID' in request.form:
            accID = int(request.form.get('accID'))
            print(type(accID))
            accounts = Accounts.query.filter_by(ID=accID).first()
            session['editAccID'] = accID
            return redirect(url_for('edit_acc'))
        elif 'from' in request.form:
            fromAccID = int(request.form.get('from'))
            fromAccInfo = Accounts.query.filter_by(ID=fromAccID).first()
            Amount = int(request.form['money'])
            if fromAccInfo.AccountBalance < Amount:
                flash("U don't have that cash man")
            else:
                toAcc = request.form.get('toAcc')
                toAccInfo = Accounts.query.filter_by(ID=toAcc).first()
                fromAccInfo.AccountBalance -= Amount
                toAccInfo.AccountBalance += Amount
                db.session.commit()
                flash('Transfer successful!')

        return redirect(url_for('dashboard'))
        # AccountName = request.form['AccountName']
        # StartingAmount = request.form['money']
        # AccountType = request.form.get('accounttypes')

    accounts = Accounts.query.filter_by(ownerID=user.ID).all()
    return render_template('dashboard.html', user=user, accounts=accounts, form=form)


# @app.route('/edit_acc', methods=['GET', 'POST'])
# @login_required
# def edit_acc():
#     user = current_user


@app.route('/edit_acc', methods=['GET', 'POST'])
@login_required
def edit_acc():
    account = Accounts.query.filter_by(ID=session['editAccID']).first()
    print(account.ID)
    print(account.AccountName)
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



# @app.route('/dashboard', methods=['GET', 'POST'])
# @login_required
# def index():
#     form = PostForm()
#     if form.validate_on_submit():
#         account = Accounts(body=form.post.data, author=current_user)
#         db.session.add(account)
#         db.session.commit()
#         flash('Your post is now live!')
#         return redirect(url_for('index'))
#     accounts = [
#         {
#             'author': {'username': 'alha@tester.no'},
#             'body': 'Beautiful day in Portland!'
#         },
#         {
#             'author': {'username': 'Susan'},
#             'body': 'The Avengers movie was so cool!'
#         }
#     ]
#     return render_template("dashboard.html", form=form,
#                            accounts=accounts)

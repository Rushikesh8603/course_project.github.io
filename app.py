from flask import Flask , render_template , url_for, redirect , request , session ,  flash , get_flashed_messages
from model import db , Users as user_model , Campaign , InfluencerSignup , SponsorSignup  , request_for_sponsor
from datetime import datetime 

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "ENTERYOURSECRETKEY"

db.init_app(app) 
 
with app.app_context():
    db.create_all() 

#=============== ADMIN =====================#

@app.route('/admin')
def admin_dashboard():
    admin_name = "RUSHIKESH"
    campaigns = Campaign.query.all()
    influencers = InfluencerSignup.query.all()
    accepted_requests = request_for_sponsor.query.filter_by(status='Accepted').all()
    return render_template('admin.html', admin_name=admin_name, campaigns=campaigns, influencers=influencers, accepted_requests=accepted_requests)

#============Update Request Status Route===============================

@app.route('/update_request_status/<int:request_id>/<string:status>', methods=['GET'])
def update_request_status(request_id, status):
    request_to_update = request_for_sponsor.query.get_or_404(request_id)
    request_to_update.status = status
    db.session.commit()
    return redirect(url_for('influencer_requests'))

#============ this is a route of [requested] in a sponsor dashbord  for sponsorrrrr

@app.route('/influencer_requests')
def influencer_requests():
    user_id = session['user_id']
    user = user_model.query.get(user_id)
    accepted_requests = request_for_sponsor.query.filter_by(camp_user_id=user_id, status='Accepted').all()
    rejected_requests = request_for_sponsor.query.filter_by(camp_user_id=user_id, status='Rejected').all()
    pending_requests = request_for_sponsor.query.filter_by(camp_user_id=user_id, status='Pending').all()
    return render_template('sponsor_requests.html', accepted_requests=accepted_requests, rejected_requests=rejected_requests, pending_requests=pending_requests)


# this is a active_campain of influensor for influensorrrr
# in the active_campin we need to send a accepted request and rejected requests so it will be shown 

@app.route('/active_campain')
def active_Campain():
    user_id = session['user_id']
    campaigns = Campaign.query.all()
    Accepted_requests = request_for_sponsor.query.filter_by(user_id=user_id, status = 'Accepted').all()
    Rejected_requests = request_for_sponsor.query.filter_by(user_id=user_id, status = 'Rejected').all()
    return render_template('active_campain.html', Campaigns=campaigns, accepted_requests = Accepted_requests ,   rejected_requests =  Rejected_requests)

# ----------------request for sponsor form influensor dashbord------------

@app.route('/request/<int:campaign_id>', methods=['GET', 'POST'])
def request_for_Sponsor(campaign_id):
    active_Campaign = Campaign.query.get_or_404(campaign_id)
    #this user id will store the user_id of infuensor
    user_id = session['user_id']
    requested = request_for_sponsor(
        title=active_Campaign.title,
        description=active_Campaign.description,
        niche=active_Campaign.niche,
        date=active_Campaign.date,
        user_id=user_id,
        camp_user_id =active_Campaign.user_id,
        status='Pending')

    db.session.add(requested)
    db.session.commit()
    flash('Request sent successfully!', 'success')
    return redirect(url_for('active_Campain'))


#-----------------------search_for_influensor--------------------------

@app.route('/search_influencers', methods=['GET'])
def search_influencers():
    query = request.args.get('query')
    if query:
        Results = InfluencerSignup.query.join(user_model).filter(
            (user_model.username.like(f'%{query}%')) | 
            (InfluencerSignup.category.like(f'%{query}%'))
        ).all()
        return render_template('search_results.html', results=Results, query=query)
    else:
        return redirect(url_for('shome'))


#------------------------search_campaign-------------------------------

@app.route('/search_campaign' , methods = ['GET'])
def search_campaign():
    query = request.args.get('query')
    if query:
        Results = Campaign.query.filter(Campaign.title.ilike(f'%{query}%')).all()
        return render_template('search_campaign_result.html' , Campaigns = Results )

#-------------------------------update-------------------------------------------
@app.route('/editcampaign/<int:campaign_id>', methods=['GET'])
def edit_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template('edit_campaign.html', campaign=campaign)

#================ update_campaign=================

@app.route('/update_campaign/<int:campaign_id>', methods=['POST'])
def update_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)

    campaign.title = request.form['title']
    campaign.description = request.form['description']
    campaign.niche = request.form['niche']
    campaign.date = request.form['date']
    campaign.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    try:
        db.session.commit()
        if session['username'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('shome', campaign_id=campaign.id)) 
    except Exception as e:
        db.session.rollback()
        #undo any changes made to the database within the 
        #current transaction if an error occurs during the commit process.
        return f"Error updating campaign: {str(e)}"

#-----------------------------this is a spnsor home page-------------------------------------------------


@app.route('/shome/')
def shome():
    if 'user_id' not in session or session.get('role') != 'sponsor':
        return redirect(url_for('login'))
    user_id = session['user_id']
    user_name = session['username']
    campaign = Campaign.query.filter_by(user_id=user_id).all()
    return render_template('sponsor.html', Ccampaign=campaign , user_name = user_name)

#============= delete_user========================

@app.route('/delete/<int:id>')
def delete_user(id):
    user_to_delete = Campaign.query.get_or_404(id)
    try:
        print(session['influ_name'])
        db.session.delete(user_to_delete)
        db.session.commit()
        if session['username'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        if session['influ_name'] == 'influ':
            return redirect(url_for('active_Campain'))
        return redirect(url_for('shome'))
    except:
        return "There was a problem deleting that user."        

#================ we are deleting campaign from admin =========================

# @app.route('/delete_user_from_admin/<int:id>')
# def deleteadmin_user(id):
#     user_to_delete = Campaign.query.get_or_404(id)
#     try:
#         db.session.delete(user_to_delete)
#         db.session.commit()
#         return redirect(url_for('admin_dashboard'))
#     except:
#         return "There was a problem deleting that user."    

#=================================================================================

# this is a influenser profile

@app.route('/influ_profile')
def home():
    if 'user_id' not in session or session.get('role') != 'influencer':
        return redirect(url_for('login'))
    user_id = session['user_id']
    user = user_model.query.get(user_id)
    Profile = user.influencer_signups[0]    
    return render_template('influ_profile.html', user=user, Profile=Profile)


#thsi is a sponsor profile

@app.route('/profile')
def profile():
    return redirect(url_for('shome'))

@app.route('/stats')
def stats():
    return 'Stats Page'

@app.route('/logout')
def logout():
    return render_template('login.html')

@app.route('/campaign')
def campain():
    return render_template("campaigns.html")

#============== this is a {campaign} it menas add a campain ===========================

@app.route('/add_campaign', methods=['GET', 'POST'])
def add_campaign():
    if 'user_id' not in session or session.get('role') != 'sponsor':
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        niche = request.form.get('niche')
        date = request.form.get('date')
        user_id = session['user_id'] 
        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
            new_campaign = Campaign(title=title, description=description, niche=niche, date=date, user_id=user_id)
            db.session.add(new_campaign)
            db.session.commit()
            return redirect(url_for('shome'))
        except Exception as e:
            db.session.rollback()
            return f"Error adding campaign: {str(e)}"   

    return render_template('add_campaign.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == '123':
            session['username'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        user = user_model.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            if user.role == 'sponsor':
                session['influ_name'] = 'spon'
                return redirect(url_for('shome'))
            elif user.role == 'influencer':
                session['influ_name'] = 'influ'
                return redirect(url_for('home'))
            else:
                error = "Role not recognized"
        else:
            error = "Invalid username or password"
    return render_template('login.html', error=error)


# this is a influenser signup
@app.route('/signup/', methods  = ['GET' , 'POST'] )
def signup():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        category = request.form.get('category')
        niche = request.form.get('niche')
        reach = request.form.get('reach')
        selected_role = 'influencer'   
        password = request.form.get('password')
        conformpass = request.form.get('conformpass')
        c = user_model.query.filter_by(username= username).first()
        if c or password != conformpass:
            error =' Username already exists. Please choose a different one.'
        else:
            user = user_model(username  = username, password = password, role=selected_role)
            db.session.add(user)    
            db.session.commit()
            c = user_model.query.filter_by(username= username).first()
            new_influencer_signup = InfluencerSignup(
                category=category,
                niche=niche,
                reach=reach,
                role=selected_role,
                user_id=c.id
            )
            db.session.add(new_influencer_signup)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('sign.html', error=error, title ="Influencer_SIGNUP")



@app.route('/Sponsorsignup/', methods  = ['GET' , 'POST'] )
def Sponsor_signup():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conformpass = request.form.get('conformpass')
        selected_role = 'sponsor'

        c = user_model.query.filter_by(username= username).first()
        if c or password != conformpass:
            error =' Username already exists. Please choose a different one.'
        else:
            user = user_model(username  = username, password = password, role=selected_role)
            db.session.add(user)    
            db.session.commit()
            c = user_model.query.filter_by(username= username).first()
            new_sponsor_signup = SponsorSignup(
                username=username,
                password=password,
                role=selected_role,
                user_id=c.id    
            )
            db.session.add(new_sponsor_signup)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('Sponsorsignup.html', error=error, title ="sponsor_SIGNUP")

#--------------------------------------------------------------------------

if __name__ == '__main__': 
    app.run(debug=True)   
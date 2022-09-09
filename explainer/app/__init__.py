from flask import Flask
from flask import render_template, flash, request, session, redirect, url_for

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, EqualTo

import os, sys, requests, json

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = 'correct-horse-battery-staple'

class HCPForm(FlaskForm):
    client_id       = StringField('HCP Client ID', validators=[InputRequired(message='Required')])
    client_secret   = StringField('HCP Client Secret', validators=[InputRequired(message='Required')])
    save_hcp_data   = SubmitField('Save')

class boundaryForm(FlaskForm):
    boundary_url          = StringField('URL', validators=[InputRequired(message='Required')])
    boundary_username     = StringField('User Name', validators=[InputRequired(message='Required')])
    boundary_password     = StringField('User Password', validators=[InputRequired(message='Required')])
    boundary_auth_method  = StringField('Auth Method ID', validators=[InputRequired(message='Required')])
    save_boundary_data    = SubmitField('Save')

@app.route('/')
def hello_world():
  if not session.get('started'):
    session.clear()
    writeToLocalConfigFile()
    session['started'] = "true"
    return render_template('splash.html')

  return render_template('about.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/challenges')
def challenges():
  return render_template('challenges.html')

@app.route('/health')
def health():
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route('/setup_hcp', methods=('GET', 'POST'))
def setup_hcp():

  hcp_form = HCPForm()

  if request.method == 'GET':
    if not session.get('hcp_client_id'):
      session['hcp_client_id'] = ""
    if not session.get('hcp_client_secret'):
      session['hcp_client_secret'] = ""

  if request.method == 'POST':

    if hcp_form.client_id.data:
      session['hcp_client_id'] = hcp_form.client_id.data
    else:
      session['hcp_client_id'] = ""

    if  hcp_form.client_secret.data:
      session['hcp_client_secret'] = hcp_form.client_secret.data
    else:
      session['hcp_client_secret'] = ""

    if hcp_form.validate_on_submit():

      validation = getHCPBearerToken()

      if (validation.status_code == 200):  
          session['hcp_client_token'] = validation.json()["access_token"]
      else:
          session['hcp_client_token'] = "Invalid Credentials."

      writeToLocalConfigFile()

  return render_template('setup_hcp.html', 
      client_id=session.get('hcp_client_id'), 
      client_secret=session.get('hcp_client_secret'),
      hcp_form=hcp_form)

@app.route('/setup_boundary', methods=('GET', 'POST'))
def setup_boundary():
  boundary_form = boundaryForm()

  if request.method == 'GET':
    if not session.get('boundary_url'):
      session['boundary_url'] = ""
    if not session.get('boundary_username'):
      session['boundary_username'] = ""
    if not session.get('boundary_password'):
      session['boundary_password'] = ""
    if not session.get('boundary_auth_method'):
      session['boundary_auth_method'] = ""

  if request.method == 'POST':

    if boundary_form.boundary_url.data:
      session['boundary_url'] = boundary_form.boundary_url.data
    else:
      session['boundary_url'] = ""

    if boundary_form.boundary_username.data:
      session['boundary_username'] = boundary_form.boundary_username.data
    else:
      session['boundary_username'] = ""

    if boundary_form.boundary_password.data:
      session['boundary_password'] = boundary_form.boundary_password.data
    else:
      session['boundary_password'] = ""

    if boundary_form.boundary_auth_method.data:
      session['boundary_auth_method'] = boundary_form.boundary_auth_method.data
    else:
      session['boundary_auth_method'] = ""

    if boundary_form.validate_on_submit():
      writeToLocalConfigFile()

  return render_template('setup_boundary.html',
      boundary_url = session.get('boundary_url'),
      boundary_username    = session.get('boundary_username'), 
      boundary_password    = session.get('boundary_password'), 
      boundary_auth_method = session.get('boundary_auth_method'), 
      boundary_form        = boundary_form)

@app.route('/get_form_status')
def get_form_status():
  
  form_name = request.args.get('form_name')

  if form_name == "hcp_form":
    if not session.get('hcp_client_id') or not session.get('hcp_client_secret'):
      return {"ready": False}

  elif form_name == "boundary_form":
    if not session.get('boundary_url') or not session.get('boundary_username') or not session.get('boundary_password') or not session.get('boundary_auth_method'):
      return {"ready": False}

  return {"ready": True}

@app.route('/track_auth')
def track_auth():
  return render_template('track_auth.html')

def writeToLocalConfigFile():

  HOME = os.getenv('HOME')
  print(HOME)

  fo = open(".deployment_data", "w")
  
  filebuffer = "# HCP Access\nexport HCP_CLIENT_ID=\"{}\"\nexport HCP_CLIENT_SECRET=\"{}\"".format(session.get('hcp_client_id'), session.get('hcp_client_secret'))
  fo.writelines(filebuffer)
  
  filebuffer = "\n\n# Boundary Data\nexport TF_VAR_controller_url=\"{}\"\nexport TF_VAR_bootstrap_user_password=\"{}\"\nexport TF_VAR_bootstrap_user_login_name=\"{}\"\nexport TF_VAR_auth_method_id=\"{}\"\n".format(session.get('boundary_url'), session.get('boundary_password'), session.get('boundary_username'), session.get('boundary_auth_method'))
  fo.writelines(filebuffer)
  
  fo.close()
  return

def getHCPBearerToken():
  auth    = (session.get('hcp_client_id'), session.get('hcp_client_secret'))
  url     = "https://auth.hashicorp.com/oauth/token"
  headers = {"Content-Type": "application/json"}
  data    = { "grant_type": "client_credentials",
              "audience": "https://api.hashicorp.cloud" }
  response = requests.post(url, json = data, auth = auth, headers = headers)

  return response

@app.route('/uc-01-challenge')
def uc_01_challenge():
  return render_template('uc-01-challenge.html')

@app.route('/uc-01-description')
def uc_01_description():
  return render_template('uc-01-description.html')

@app.route('/uc-01-example')
def uc_01_example():
  return render_template('uc-01-example.html')

@app.route('/uc-01-section-01')
def uc_01_section_01():
  return render_template('uc-01-section-01.html')

@app.route('/uc-01-section-02')
def uc_01_section_02():
  return render_template('uc-01-section-02.html')

@app.route('/uc-01-section-03')
def uc_01_section_03():
  return render_template('uc-01-section-03.html')

@app.route('/uc-01-summary')
def uc_01_summary():
  return render_template('uc-01-summary.html')

@app.route('/uc-02-challenge')
def uc_02_challenge():
  return render_template('uc-02-challenge.html')

@app.route('/uc-02-section-01')
def uc_02_section_01():
  return render_template('uc-02-section-01.html')

@app.route('/uc-02-section-02')
def uc_02_section_02():
  return render_template('uc-02-section-02.html')

@app.route('/uc-02-section-03')
def uc_02_section_03():
  return render_template('uc-02-section-03.html')

@app.route('/uc-03-challenge')
def uc_03_challenge():
  return render_template('uc-03-challenge.html')

@app.route('/uc-03-section-01')
def uc_03_section_01():
  return render_template('uc-03-section-01.html')

@app.route('/uc-03-section-02')
def uc_03_section_02():
  return render_template('uc-03-section-02.html')

@app.route('/uc-03-section-03')
def uc_03_section_03():
  return render_template('uc-03-section-03.html')

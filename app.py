from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///athletes.db'
db = SQLAlchemy(app)

# Athlete model
class Athlete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    other_names = db.Column(db.String(50))
    matric_number = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)

# Create the database tables
db.create_all()

# Athlete registration page
@app.route('/athlete/register', methods=['GET', 'POST'])
def athlete_register():
    if request.method == 'POST':
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        other_names = request.form['other-names']
        matric_number = request.form['matric-number']
        department = request.form['department']

        # Create a new athlete
        new_athlete = Athlete(first_name=first_name, last_name=last_name, other_names=other_names, matric_number=matric_number, department=department)
        db.session.add(new_athlete)
        db.session.commit()

        return redirect(url_for('athlete_profile', athlete_id=new_athlete.id))

    return render_template('athlete_registration.html')

# Athlete profile page
@app.route('/athlete/profile/<int:athlete_id>')
def athlete_profile(athlete_id):
    athlete = Athlete.query.get_or_404(athlete_id)
    return render_template('athlete_profile.html', athlete=athlete)

# Event creation page
@app.route('/event/create', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        event_name = request.form['event-name']
        event_date = request.form['event-date']
        event_time = request.form['event-time']
        event_location = request.form['event-location']

        # Create a new event
        new_event = Event(name=event_name, date=event_date, time=event_time, location=event_location)
        db.session.add(new_event)
        db.session.commit()

        return redirect(url_for('event_management'))

    return render_template('event_creation.html')

# Event management page
@app.route('/event/management')
def event_management():
    events = Event.query.all()
    return render_template('event_management.html', events=events)


if __name__ == '__main__':
    app.run(debug=True)

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, session, url_for
from sqlalchemy import PrimaryKeyConstraint
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import psycopg2
import sys
from datetime import datetime
#from models import *
#----------------------------------------------------------------------------#
# App Config
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:faluyi@localhost:5432/postgres'
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
#shows = db.Table('shows',
#  db.Column('Artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
 # db.Column('Venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
 # db.Column('start_time', db.DateTime, default=datetime.utcnow, nullable=False)
#)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    website_link = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.Text, nullable=False)
    #shows = db.relationship('Show', backref='Venue', lazy='joined')
   

    def __repr__(self):
      return f'<Venue {self.id} name: {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(),nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120), nullable=False)
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.Text, nullable=False)
    #shows = db.relationship('Show', backref='Artist', lazy='joined')
    #venues = db.relationship('Venues', secondary=shows, backref=db.backref('Artist', lazy=True))

    def __repr__(self):
      return f'<Venue {self.id} name: {self.name}>'



class Show(db.Model):
  __tablename__="Show"

  id = db.Column(db.Integer, primary_key=True)
  Artist_id =  db.Column(db.Integer,  nullable=False)
  Venue_id =  db.Column(db.Integer, nullable=False)
  start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(str(value), ignoretz=True)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
  areas=Venue.query.with_entities(Venue.city,Venue.state).distinct().all()
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  

  data = []
  for cities in areas:
    city = cities[0]
    state = cities[1]
    venue = Venue.query.filter_by(city=city,state=state).all()
    data.append({
      "city":city,
      "state":state,
      "venues":venue,
      "upcoming shows":len(venue)
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get("search_term")
  query = '%{0}%'.format(search_term)
  response = list(Venue.query.filter(Venue.name.ilike(query)).all())
  result = []
  count = len(response)
  for venue in response:
        result.append({
            "name": venue.name,
            "id": venue.id
        })
        
  app.logger.info(response)
  app.logger.info(search_term)
  return render_template('pages/search_venues.html', results=result, count=count, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.filter_by(id=venue_id).one()
  shows = Show.query.filter_by(Venue_id=venue_id).all()
  upcoming_shows = []
  past_shows = []
  
  for show in shows:
    if (show.start_time).strftime("%j")>datetime.now().strftime("%j"):
      artist = db.session.query(Artist).get(show.Artist_id)
      show_dtls = {
        "artist_image_link": artist.image_link,
        "artist_id": artist.id,
        "artist_name": artist.name,
        "start_time":show.start_time
      }
      upcoming_shows.append(show_dtls)
    else:
      artist = db.session.query(Artist).get(show.Artist_id)
      show_dtls = {
        "artist_image_link": artist.image_link,
        "artist_id": artist.id,
        "artist_name": artist.name,
        "start_time":show.start_time
      }
      past_shows.append(show_dtls)
      
  upcoming_shows_count = len(upcoming_shows)
  past_shows_count = len(past_shows)
  
  return render_template('pages/show_venue.html', venue=venue, shows=shows, upcoming_shows_count=upcoming_shows_count, past_shows_count=past_shows_count, upcoming_shows=upcoming_shows, past_shows=past_shows)
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  form = VenueForm(request.form)

  venue = Venue(
        name = form.name.data, 
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        genres= form.genres.data,
        website_link = form.website_link.data,
        seeking_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data
  )


  # TODO: modify data to be the data object returned from db insertion
  try:
    db.session.add(venue)
    db.session.commit()

  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist= Artist.query.order_by('id').all()
  data = []
  for artists in artist:
    data.append(artists)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get("search_term")
  query = '%{0}%'.format(search_term)
  response = list(Artist.query.filter(Artist.name.ilike(query)).all())
  result = []
  count = len(response)
  for venue in response:
        result.append({
            "name": venue.name,
            "id": venue.id
        })
        
  response={
    "count": count,
    "data": result
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  id = artist_id
  dtl = Artist.query.get(id)
  shows = list(Show.query.filter_by(Artist_id=artist_id).all())
  upcoming_shows = []
  past_shows = []
  
  for show in shows:
    if (show.start_time).strftime("%j")>datetime.now().strftime("%j"):
      upcoming_shows.append(show)
    else:
      past_shows.append(show)
      
  upcoming_shows_count = len(upcoming_shows)
  past_shows_count = len(past_shows)
  
  app.logger.info(upcoming_shows_count)
  app.logger.info(past_shows)
  app.logger.info(shows)
  
      
      
  data = {
    "id": dtl.id,
    "name": dtl.name,
    "genres": dtl.genres,
    "city": dtl.city,
    "state": dtl.state,
    "phone": dtl.phone,
    "website": dtl.website_link,
    "facebook_link": dtl.facebook_link,
    "seeking_venue": dtl.seeking_venue,
    "seeking_description": dtl.seeking_description,
    "image_link": dtl.image_link,
    "upcoming_shows_count": upcoming_shows_count,
    "past_shows_count": past_shows_count
  }
  
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  
  artist.name = form.name.data, 
  artist.city = form.city.data,
  artist.state = form.state.data,
  artist.phone = form.phone.data,
  artist.image_link = form.image_link.data,
  artist.facebook_link = form.facebook_link.data,
  artist.genres = form.genres.data,
  artist.website_link = form.website_link.data,
  artist.seeking_venue = form.seeking_venue.data,
  artist.seeking_description = form.seeking_description.data
  
  db.session.bulk_update_mappings()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  venue = Venue.query.get(venue_id)

  venue.name = form.name.data, 
  venue.city = form.city.data,
  venue.state = form.state.data,
  venue.address = form.address.data,
  venue.phone = form.phone.data,
  venue.image_link = form.image_link.data,
  venue.facebook_link = form.facebook_link.data,
  venue.genres= form.genres.data,
  venue.website_link = form.website_link.data,
  venue.seeking_talent = form.seeking_talent.data,
  venue.seeking_description = form.seeking_description.data
  
  db.session.commit()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = ArtistForm(request.form)

  artist = Artist(
        name = form.name.data, 
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        genres= form.genres.data,
        website_link = form.website_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data
  )

  try:
    db.session.add(artist)
    db.session.commit()


    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()

  finally:
    db.session.close()
  return render_template('pages/home.html')

    # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.


  shows = Show.query.with_entities(Show.Venue_id,Show.Artist_id,Show.start_time).distinct().all()

  data = []
  for show in shows:
    venue_id = show[0]
    artist_id = show[1]
    start_time = show[2]
    venue = Venue.query.filter_by(id=venue_id).one()
    artist = Artist.query.filter_by(id=artist_id).one()
    data.append({
    "venue_id": venue_id,
    "venue_name": venue.name,
    "artist_id": artist_id,
    "artist_name": artist.name, 
    "artist_image_link": artist.image_link,
    "start_time": start_time
  })  
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)

  show = Show(
    Artist_id = form.artist_id.data,
    Venue_id = form.venue_id.data,
    start_time = form.start_time.data       
  )

  try:
    db.session.add(show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')

  except:
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()

  finally:
    db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

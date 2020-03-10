# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import logging
from logging import Formatter, FileHandler
import sys
import babel
import dateutil.parser
from flask import (
    Flask, render_template, request, flash, redirect, url_for, abort
)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from forms import VenueForm, ArtistForm, ShowForm

# ----------------------------------------------------------------------------#
# App Config
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models
# ----------------------------------------------------------------------------#

venue_genres = db.Table(
    'VenueGenres',
    db.Column(
        'venue_id',
        db.Integer,
        db.ForeignKey('Venue.id'),
        primary_key=True
    ),
    db.Column(
        'genre_id',
        db.Integer,
        db.ForeignKey('Genre.id'),
        primary_key=True
    )
)

artist_genres = db.Table(
    'ArtistGenres',
    db.Column(
        'artist_id',
        db.Integer,
        db.ForeignKey('Artist.id'),
        primary_key=True
    ),
    db.Column(
        'genre_id',
        db.Integer,
        db.ForeignKey('Genre.id'),
        primary_key=True
    )
)


class Venue(db.Model):
    """A model representing a venue

    Attributes:
        id: A unique identifer for the venue object
        name: A str representing the venue's name
        genres: A list of Genre objects representing what genres are played at
            the venue
        address: A str representing the address of the venue
        city: A str representing the city in which the venue is located
        state: A str representing the state in which the venue is located
        phone: A str representing the phone number for the venue
        website: A str repersenting the website for the venue
        facebook_link: A str representing a link to the venue's facebook page
        seeking_talent: A bool indicating whether the venue is seeking artists
            or not
        seeking_description: A str describing what type of artist the venue is
            seeking if seeking_talent bool is set to True
        image_link: A str represening a link to an image of the venue
        shows: A list of Show obects representing shows that are assciated
            with the venue
    """

    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.relationship('Genre', secondary=venue_genres, backref='venue')
    address = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue')


class Artist(db.Model):
    """A model representing an artist

    Attributes:
        id: A unique identifer for the artist object
        name: A str representing the artist's name
        genres: A list of Genre objects representing what genres the artist
            plays
        city: A str representing the city in which the artist is from
        state: A str representing the state in which the artist is from
        phone: A str representing the artist's phone number
        website: A str repersenting the artist's website
        facebook_link: A str representing a link to the artist's facebook page
        seeking_venue: A bool indicating whether the artist is seeking a venue
        seeking_description: A str describing what type of venue the artist is
            seeking if seeking_venue bool is set to True
        image_link: A str represening a link to an image of the artist
        shows: A list of Show obects representing shows that are assciated
            with the artist
    """

    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.relationship(
        'Genre',
        secondary=artist_genres,
        backref='artist'
    )
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist')


class Show(db.Model):
    """A model representing an show

    Attributes:
        id: A unique identifer for the show object
        venue_id: The id of the venue that the show was at
        artist_id: The id of the artist that performed at the show
        start_time: A datetime that represents the start time of the show
    """

    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(
        db.Integer,
        db.ForeignKey('Artist.id'),
        nullable=False
    )
    start_time = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now()  # pylint: disable=E1103
    )


class Genre(db.Model):
    """A model representing an genre

    Attributes:
        id: A unique identifer for the genre object
        name: A str representing the name of the genre
    """

    __tablename__ = 'Genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

# ----------------------------------------------------------------------------#
# Filters
# ----------------------------------------------------------------------------#


def format_datetime(value, datetime_format='medium'):
    """Converts a datetime str to a format that is understood by the db

    Args:
        value: A str representing a datetime
        datetime_format: A str representing the desired format of the returned
            datetime, accepted values are ('full', 'medium')

    Returns:
        A date formatted according to the given format
    """
    date = dateutil.parser.parse(value)
    if datetime_format == 'full':
        datetime_format = "EEEE MMMM, d, y 'at' h:mma"
    elif datetime_format == 'medium':
        datetime_format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, datetime_format)


app.jinja_env.filters['datetime'] = format_datetime  # pylint: disable=E1101


# ----------------------------------------------------------------------------#
# Controllers
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    """The route handler for the homepage

    Returns:
        A rendered html template for the homepage
    """
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per
    #   venue.
    data = [{
        "city": "San Francisco",
        "state": "CA",
        "venues": [{
            "id": 1,
            "name": "The Musical Hop",
            "num_upcoming_shows": 0,
        }, {
            "id": 3,
            "name": "Park Square Live Music & Coffee",
            "num_upcoming_shows": 1,
        }]
    }, {
        "city": "New York",
        "state": "NY",
        "venues": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }]
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it
    #       is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live
    #   Music & Coffee"
    response = {
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get('search_term', '')
    )


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data1 = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": (
            "We are on the lookout for a local artist to play every two "
            "weeks. Please call us."
        ),
        "image_link": (
            "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=r"
            "b-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
        ),
        "past_shows": [{
            "artist_id": 4,
            "artist_name": "Guns N Petals",
            "artist_image_link": (
                "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixl"
                "ib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w="
                "300&q=80"
            ),
            "start_time": "2019-05-21T21:30:00.000Z"
        }],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data2 = {
        "id": 2,
        "name": "The Dueling Pianos Bar",
        "genres": ["Classical", "R&B", "Hip-Hop"],
        "address": "335 Delancey Street",
        "city": "New York",
        "state": "NY",
        "phone": "914-003-1132",
        "website": "https://www.theduelingpianos.com",
        "facebook_link": "https://www.facebook.com/theduelingpianos",
        "seeking_talent": False,
        "image_link": (
            "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixli"
            "b=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q"
            "=80"
        ),
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": 0,
        "upcoming_shows_count": 0,
    }
    data3 = {
        "id": 3,
        "name": "Park Square Live Music & Coffee",
        "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
        "address": "34 Whiskey Moore Ave",
        "city": "San Francisco",
        "state": "CA",
        "phone": "415-000-1234",
        "website": "https://www.parksquarelivemusicandcoffee.com",
        "facebook_link": (
            "https://www.facebook.com/ParkSquareLiveMusicAndCoffee"
        ),
        "seeking_talent": False,
        "image_link": (
            "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixli"
            "b=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q"
            "=80"
        ),
        "past_shows": [{
            "artist_id": 5,
            "artist_name": "Matt Quevedo",
            "artist_image_link": (
                "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?"
                "ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop"
                "&w=334&q=80"
            ),
            "start_time": "2019-06-15T23:00:00.000Z"
        }],
        "upcoming_shows": [{
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": (
                "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixl"
                "ib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w="
                "794&q=80"
            ),
            "start_time": "2035-04-01T20:00:00.000Z"
        }, {
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": (
                "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixl"
                "ib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w="
                "794&q=80"
            ),
            "start_time": "2035-04-08T20:00:00.000Z"
        }, {
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": (
                "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixl"
                "ib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w="
                "794&q=80"
            ),
            "start_time": "2035-04-15T20:00:00.000Z"
        }],
        "past_shows_count": 1,
        "upcoming_shows_count": 3,
    }
    data = list(filter(lambda d: d['id'] ==
                       venue_id, [data1, data2, data3]))[0]
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    """Displays the form for creating a venue

    Returns:
        A html template for the venue form
    """

    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    """Creates a new venue in the db from a form submission

    Returns:
        The template for the homepage
    """

    error = False

    try:

        genres = []
        genre_names = request.form.getlist('genres')
        for genre_name in genre_names:
            genre = Genre.query.filter_by(name=genre_name).first()
            if not genre:
                genre = Genre(name=genre_name)
                db.session.add(genre)
            genres.append(genre)

        name = request.form.get('name')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        website = request.form.get('website')
        facebook_link = request.form.get('facebook_link')
        seeking_talent = request.form.get('seeking_talent')
        seeking_description = request.form.get('seeking_description')
        image_link = request.form.get('image_link')
        venue = Venue(
            name=name,
            genres=genres,
            address=address,
            city=city,
            state=state,
            phone=phone,
            website=website,
            facebook_link=facebook_link,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description,
            image_link=image_link
        )
        db.session.add(venue)
        db.session.commit()

    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    if error:
        flash(f'Venue {name} was unable to be listed!', 'error')
        abort(500)

    flash(f'Venue {name} was successfully listed!')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    #       SQLAlchemy ORM to delete a record. Handle cases where the session
    #       commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page,
    # have it so that clicking that button delete it from the db then redirect
    # the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = [{
        "id": 4,
        "name": "Guns N Petals",
    }, {
        "id": 5,
        "name": "Matt Quevedo",
    }, {
        "id": 6,
        "name": "The Wild Sax Band",
    }]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it
    #       is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The
    #   Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {
        "count": 1,
        "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get('search_term', '')
    )


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data1 = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": (
            "Looking for shows to perform at in the San Francisco Bay Area!"
        ),
        "image_link": (
            "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=r"
            "b-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
        ),
        "past_shows": [{
            "venue_id": 1,
            "venue_name": "The Musical Hop",
            "venue_image_link": (
                "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixl"
                "ib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w="
                "400&q=60"
            ),
            "start_time": "2019-05-21T21:30:00.000Z"
        }],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data2 = {
        "id": 5,
        "name": "Matt Quevedo",
        "genres": ["Jazz"],
        "city": "New York",
        "state": "NY",
        "phone": "300-400-5000",
        "facebook_link": "https://www.facebook.com/mattquevedo923251523",
        "seeking_venue": False,
        "image_link": (
            "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixli"
            "b=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q"
            "=80"
        ),
        "past_shows": [{
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": (
                "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?"
                "ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop"
                "&w=747&q=80"
            ),
            "start_time": "2019-06-15T23:00:00.000Z"
        }],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data3 = {
        "id": 6,
        "name": "The Wild Sax Band",
        "genres": ["Jazz", "Classical"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "432-325-5432",
        "seeking_venue": False,
        "image_link": (
            "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=r"
            "b-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80"
        ),
        "past_shows": [],
        "upcoming_shows": [{
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": (
                "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?"
                "ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop"
                "&w=747&q=80"
            ),
            "start_time": "2035-04-01T20:00:00.000Z"
        }, {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": (
                "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?"
                "ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop"
                "&w=747&q=80"
            ),
            "start_time": "2035-04-08T20:00:00.000Z"
        }, {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": (
                "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?"
                "ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop"
                "&w=747&q=80"
            ),
            "start_time": "2035-04-15T20:00:00.000Z"
        }],
        "past_shows_count": 0,
        "upcoming_shows_count": 3,
    }
    data = list(filter(lambda d: d['id'] ==
                       artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": (
            "Looking for shows to perform at in the San Francisco Bay Area!"
        ),
        "image_link": (
            "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=r"
            "b-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
        )
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    #       artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": (
            "We are on the lookout for a local artist to play every two "
            "weeks. Please call us."
        ),
        "image_link": (
            "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=r"
            "b-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
        )
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    #       venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    """Creates a new artist in the db from a form submission

    Returns:
        The template for the homepage
    """

    error = False

    try:

        genres = []
        genre_names = request.form.getlist('genres')
        for genre_name in genre_names:
            genre = Genre.query.filter_by(name=genre_name).first()
            if not genre:
                genre = Genre(name=genre_name)
                db.session.add(genre)
            genres.append(genre)

        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        website = request.form.get('website')
        facebook_link = request.form.get('facebook_link')
        seeking_venue = request.form.get('seeking_venue')
        seeking_description = request.form.get('seeking_description')
        image_link = request.form.get('image_link')
        artist = Artist(
            name=name,
            genres=genres,
            city=city,
            state=state,
            phone=phone,
            website=website,
            facebook_link=facebook_link,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description,
            image_link=image_link
        )
        db.session.add(artist)
        db.session.commit()

    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    if error:
        flash(f'Artist {name} was could not be listed!')
        abort(500)

    flash(f'Artist {name} was successfully listed!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows
    #           per venue.
    data = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": (
            "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=r"
            "b-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
        ),
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": (
            "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixli"
            "b=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q"
            "=80"
        ),
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": (
            "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=r"
            "b-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80"
        ),
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": (
            "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=r"
            "b-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80"
        ),
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": (
            "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=r"
            "b-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80"
        ),
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing
    #   form
    # TODO: insert form data as a new Show record in the db, instead on
    #       successful db insert, flash success
    flash('Show was successfully listed!')
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
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    app.logger.setLevel(logging.INFO)  # pylint: disable=E1103
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)  # pylint: disable=E1103
    app.logger.info('errors')  # pylint: disable=E1103

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

"""A musical venue and artist booking site.

Fyyur is a musical venue and artist booking site that facilitates the discovery
and bookings of shows between local performing artists and venues

    Usage: app.py
"""

# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from datetime import datetime
import logging
from logging import Formatter, FileHandler
import os
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
    'venue_genres',
    db.Column(
        'venue_id',
        db.Integer,
        db.ForeignKey('venues.id'),
        primary_key=True
    ),
    db.Column(
        'genre_id',
        db.Integer,
        db.ForeignKey('genres.id'),
        primary_key=True
    )
)

artist_genres = db.Table(
    'artist_genres',
    db.Column(
        'artist_id',
        db.Integer,
        db.ForeignKey('artists.id'),
        primary_key=True
    ),
    db.Column(
        'genre_id',
        db.Integer,
        db.ForeignKey('genres.id'),
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
        area_id: The id of the area the venue is located in
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

    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.relationship('Genre', secondary=venue_genres, backref='venue')
    address = db.Column(db.String(120), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    shows = db.relationship(
        'Show',
        backref='venue',
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return self.name


class Artist(db.Model):
    """A model representing an artist

    Attributes:
        id: A unique identifer for the artist object
        name: A str representing the artist's name
        genres: A list of Genre objects representing what genres the artist
            plays
        area_id: The id of the area the artist is based out of
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

    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.relationship(
        'Genre',
        secondary=artist_genres,
        backref='artist'
    )
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    shows = db.relationship(
        'Show',
        backref='artist',
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return self.name


class Show(db.Model):
    """A model representing a show

    Attributes:
        id: A unique identifer for the show object
        venue_id: The id of the venue that the show was at
        artist_id: The id of the artist that performed at the show
        start_time: A datetime that represents the start time of the show
    """

    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(
        db.Integer,
        db.ForeignKey('venues.id'),
        nullable=False
    )
    artist_id = db.Column(
        db.Integer,
        db.ForeignKey('artists.id'),
        nullable=False
    )
    start_time = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now()  # pylint: disable=no-member
    )


class Genre(db.Model):
    """A model representing an genre

    Attributes:
        id: A unique identifer for the genre object
        name: A str representing the name of the genre
    """

    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return self.name


class Area(db.Model):
    """A model representing a city, state

    Attributes:
        id: A unique identifier for the area object
        city: A str representing the city in the area object
        state: A str representing the state in the are object
        venues: A list of venues located in the city, state
        artists: A list of artists that are based out of city, state
    """

    __tablename__ = 'areas'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    venues = db.relationship('Venue', backref='area')
    artists = db.relationship('Artist', backref='area')

    def __repr__(self):
        return f'{self.city}, {self.state}'


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
    """Route handler for looking at all venues grouped by city, state

    Returns:
        A template for all venues populated with venues grouped by city, state
    """

    data = []
    areas = Venue.query.with_entities(
        Venue.city,
        Venue.state
    ).group_by(
        Venue.city,
        Venue.state
    ).all()

    for area in areas:
        area_venues = Venue.query.filter_by(
            city=area.city,
            state=area.state
        ).all()
        data.append({
            "city": area.city,
            "state": area.state,
            "venues": area_venues
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    """Route handler for venue search

    Returns:
        A template with the search results
    """
    search_term = request.form.get('search_term', '')
    data = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%')  # pylint: disable=no-member
    ).all()
    results = {
        'count': len(data),
        'data': data
    }

    return render_template(
        'pages/search_venues.html',
        results=results,
        search_term=search_term
    )


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    """Route handler for showing the details for a venue

    Args:
        venue_id: A str representing the id of the venue to show details for

    Returns:
        A template with the detail view for a venue
    """

    venue = Venue.query.get(venue_id)
    venue.past_shows = []
    venue.upcoming_shows = []

    for show in venue.shows:
        show.artist_name = show.artist.name
        show.artist_image_link = show.artist.image_link
        if show.start_time < datetime.now():
            show.start_time = str(show.start_time)
            venue.past_shows.append(show)
        else:
            show.start_time = str(show.start_time)
            venue.upcoming_shows.append(show)

    venue.past_shows_count = len(venue.past_shows)
    venue.upcoming_shows_count = len(venue.upcoming_shows)

    return render_template('pages/show_venue.html', venue=venue)


#  Update Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    """Displays the form for editing a venue

    Args:
        venue_id: A str representing the id of the venue to edit

    Returns:
        A html template for the venue form which has been pre-populated
    """
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    """Updates an existing venue in the db from a form submission

    Args:
        venue_id: A str representing the id of the venue to update

    Returns:
        The template for the venue's detail page
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

        venue = Venue.query.get(venue_id)
        venue.name = request.form.get('name')
        venue.genres = genres
        venue.address = request.form.get('address')
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.phone = request.form.get('phone')
        venue.website = request.form.get('website')
        venue.facebook_link = request.form.get('facebook_link')
        venue.seeking_talent = bool(request.form.get('seeking_talent'))
        venue.seeking_description = request.form.get('seeking_description')
        venue.image_link = request.form.get('image_link')
        db.session.commit()
        venue_name = venue.name

    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    if error:
        flash(f'Venue {venue_name} was unable to be updated!', 'error')
        abort(500)

    flash(f'Venue {venue_name} was successfully updated!')

    return redirect(url_for('show_venue', venue_id=venue_id))


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

        venue = Venue(
            name=request.form.get('name'),
            genres=genres,
            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            phone=request.form.get('phone'),
            website=request.form.get('website'),
            facebook_link=request.form.get('facebook_link'),
            seeking_talent=request.form.get('seeking_talent'),
            seeking_description=bool(request.form.get('seeking_description')),
            image_link=request.form.get('image_link')
        )
        db.session.add(venue)
        db.session.commit()
        venue_id = venue.id
        venue_name = venue.name

    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    if error:
        flash(f'Venue {venue_name} was unable to be listed!', 'error')
        abort(500)

    flash(f'Venue {venue_name} was successfully listed!')

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    """Route handler to delete a venue from the db

    Args:
        venue_id: A str representing the id of the venue to delete

    Returns:
        A redirect to the venues page
    """

    error = False

    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        name = venue.name
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash(f'Venue {name} was unable to be deleted!', 'error')
        abort(500)

    flash(f'Venue {name} was successfully deleted!')

    return redirect(url_for('venues'))


#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
    """Route handler for showing a list of artists

    Returns:
        A template for a list of all artists
    """
    artists_all = Artist.query.all()
    return render_template('pages/artists.html', artists=artists_all)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    """Route handler for artist search

    Returns:
        A template with the search results
    """
    search_term = request.form.get('search_term', '')
    data = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')  # pylint: disable=no-member
    ).all()
    results = {
        'count': len(data),
        'data': data
    }

    return render_template(
        'pages/search_artists.html',
        results=results,
        search_term=search_term
    )


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    """Route handler for showing the details for an artist

    Args:
        artist_id: A str representing the id of the artist to show details for

    Returns:
        A template with the detail view for an artist
    """

    artist = Artist.query.get(artist_id)
    artist.past_shows = []
    artist.upcoming_shows = []

    for show in artist.shows:
        show.venue_name = show.venue.name
        show.venue_image_link = show.venue.image_link
        if show.start_time < datetime.now():
            show.start_time = str(show.start_time)
            artist.past_shows.append(show)
        else:
            show.start_time = str(show.start_time)
            artist.upcoming_shows.append(show)

    artist.past_shows_count = len(artist.past_shows)
    artist.upcoming_shows_count = len(artist.upcoming_shows)

    return render_template('pages/show_artist.html', artist=artist)


#  Update Artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    """Displays the form for editing an artist

    Args:
        artist_id: A str representing the id of the artist to edit

    Returns:
        A html template for the artist form which has been pre-populated
    """
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    """Updates an existing artist in the db from a form submission

    Args:
        artist_id: A str representing the id of the artist to update

    Returns:
        The template for the artist's detail page
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

        artist = Artist.query.get(artist_id)
        artist.name = request.form.get('name')
        artist.genres = genres
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        artist.website = request.form.get('website')
        artist.facebook_link = request.form.get('facebook_link')
        artist.seeking_talent = bool(request.form.get('seeking_talent'))
        artist.seeking_description = request.form.get('seeking_description')
        artist.image_link = request.form.get('image_link')
        db.session.commit()
        artist_name = artist.name

    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    if error:
        flash(f'Artist {artist_name} was unable to be updated!', 'error')
        abort(500)

    flash(f'Artist {artist_name} was successfully updated!')

    return redirect(url_for('show_artist', artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    """Displays the form for creating an artist

    Returns:
        A html template for the artist form
    """
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

        artist = Artist(
            name=request.form.get('name'),
            genres=genres,
            city=request.form.get('city'),
            state=request.form.get('state'),
            phone=request.form.get('phone'),
            website=request.form.get('website'),
            facebook_link=request.form.get('facebook_link'),
            seeking_venue=bool(request.form.get('seeking_venue')),
            seeking_description=request.form.get('seeking_description'),
            image_link=request.form.get('image_link')
        )
        db.session.add(artist)
        db.session.commit()
        artist_id = artist.id
        artist_name = artist.name

    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    if error:
        flash(f'Artist {artist_name} was could not be listed!', 'error')
        abort(500)

    flash(f'Artist {artist_name} was successfully listed!')

    return redirect(url_for('show_artist', artist_id=artist_id))


#  Delete Artist
#  ----------------------------------------------------------------

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    """Route handler to delete a artist from the db

    Args:
        artist_id: A str representing the id of the artist to delete

    Returns:
        A redirect to the artists page
    """

    error = False

    try:
        artist = Artist.query.get(artist_id)
        db.session.delete(artist)
        db.session.commit()
        name = artist.name
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash(f'Artist {name} was unable to be deleted!', 'error')
        abort(500)

    flash(f'Artist {name} was successfully deleted!')

    return redirect(url_for('artists'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    """Route handler for showing a list of shows

    Returns:
        A template for a list of all shows
    """

    shows_all = Show.query.all()

    for show in shows_all:
        show.venue_name = show.venue.name
        show.artist_name = show.artist.name
        show.artist_image_link = show.artist.image_link
        show.start_time = str(show.start_time)

    return render_template('pages/shows.html', shows=shows_all)


#  Create Show
#  ----------------------------------------------------------------

@app.route('/shows/create', methods=['GET'])
def create_show_form():
    """Displays the form for creating a show

    Returns:
        A html template for the show form
    """
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    """Creates a new show in the db from a form submission

    Returns:
        A redirect to the shows page
    """

    error = False

    try:
        show = Show(
            venue_id=request.form.get('venue_id'),
            artist_id=request.form.get('artist_id'),
            start_time=request.form.get('start_time')
        )
        db.session.add(show)
        db.session.commit()
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash(f'Show was unable to be listed!', 'error')
        abort(500)

    flash(f'Show was successfully listed!')

    return redirect(url_for('shows'))


# ----------------------------------------------------------------------------#
# Error Handlers
# ----------------------------------------------------------------------------#

@app.errorhandler(404)
def not_found_error(error):  # pylint: disable=unused-argument
    """Error handler for 404 not found

    Args:
        error: unused

    Returns:
        A custom template for the error message
    """
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):  # pylint: disable=unused-argument
    """Error handler for 500 internal server error

    Args:
        error: unused

    Returns:
        A custom template for the error message
    """
    return render_template('errors/500.html'), 500


# ----------------------------------------------------------------------------#
# Debug
# ----------------------------------------------------------------------------#

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    app.logger.setLevel(logging.INFO)  # pylint: disable=no-member
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)  # pylint: disable=no-member
    app.logger.info('errors')  # pylint: disable=no-member

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    app.run(host=host, port=port)

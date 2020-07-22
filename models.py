"""Model objects used to model data for the db.

Attributes:
    app: A flask Flask object creating the flask app
    moment: A flask_moment Moment object used to format datetimes in Jinja2
        templates bound to app
    db: A flask_sqlalchemy SQLAlchemy object bound to app
    migrate: A flask_migrate Migrate object bound to app and db
    venue_genres: An association table for the many-to-many relationship
        between venues and genres
    artist_genres: An association table for the many-to-many relationship
        between artist and genres

Classes:
    Venue()
    Artist()
    Show()
    Genre()
    Area()
    Music()
    Unavailability()
"""

from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

# ----------------------------------------------------------------------------#
# App Config
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models
# ----------------------------------------------------------------------------#

venue_genres = db.Table(
    "venue_genres",
    db.Column(
        "venue_id", db.Integer, db.ForeignKey("venues.id"), primary_key=True
    ),
    db.Column(
        "genre_id", db.Integer, db.ForeignKey("genres.id"), primary_key=True
    ),
)

artist_genres = db.Table(
    "artist_genres",
    db.Column(
        "artist_id", db.Integer, db.ForeignKey("artists.id"), primary_key=True
    ),
    db.Column(
        "genre_id", db.Integer, db.ForeignKey("genres.id"), primary_key=True
    ),
)


class Venue(db.Model):
    """A model representing a venue.

    Attributes:
        id: A unique identifer for the venue object
        name: A str representing the venue's name
        genres: A list of Genre objects representing what genres are played at
            the venue
        address: A str representing the address of the venue
        area_id: The id of the area the venue is located in
        phone: A str representing the phone number for the venue
        website: A str representing the website for the venue
        facebook_link: A str representing a link to the venue's facebook page
        seeking_talent: A bool indicating whether the venue is seeking artists
            or not
        seeking_description: A str describing what type of artist the venue is
            seeking if seeking_talent bool is set to True
        image_link: A str representing a link to an image of the venue
        shows: A list of Show objects representing shows that are assciated
            with the venue
    """

    __tablename__ = "venues"
    __table_args__ = (db.UniqueConstraint("name", "address", "area_id"),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.relationship("Genre", secondary=venue_genres, backref="venue")
    address = db.Column(db.String(120), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("areas.id"), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now()  # pylint: disable=no-member
    )
    shows = db.relationship(
        "Show", backref="venue", cascade="all, delete-orphan"
    )

    def __repr__(self):
        """A Venue object's str representation."""
        return self.name


class Artist(db.Model):
    """A model representing an artist.

    Attributes:
        id: A unique identifer for the artist object
        name: A str representing the artist's name
        genres: A list of Genre objects representing what genres the artist
            plays
        area_id: The id of the area the artist is based out of
        phone: A str representing the artist's phone number
        website: A str representing the artist's website
        facebook_link: A str representing a link to the artist's facebook page
        seeking_venue: A bool indicating whether the artist is seeking a venue
        seeking_description: A str describing what type of venue the artist is
            seeking if seeking_venue bool is set to True
        image_link: A str representing a link to an image of the artist
        shows: A list of Show objects representing shows that are assciated
            with the artist
        unavailabilities: A list of Unavailability objects representing when
            the artist is unable to be booked
    """

    __tablename__ = "artists"
    __table_args__ = (db.UniqueConstraint("name", "area_id"),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.relationship(
        "Genre", secondary=artist_genres, backref="artist"
    )
    area_id = db.Column(db.Integer, db.ForeignKey("areas.id"), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now()  # pylint: disable=no-member
    )
    shows = db.relationship(
        "Show", backref="artist", cascade="all, delete-orphan"
    )
    unavailabilities = db.relationship(
        "Unavailability", backref="artist", cascade="all, delete-orphan"
    )
    music = db.relationship(
        "Music", backref="artist", cascade="all, delete-orphan"
    )

    def __repr__(self):
        """An Artist object's str representation."""
        return self.name


class Show(db.Model):
    """A model representing a show.

    Attributes:
        id: A unique identifer for the show object
        venue_id: The id of the venue that the show was at
        artist_id: The id of the artist that performed at the show
        start_time: A datetime that represents the start time of the show
    """

    __tablename__ = "shows"
    __table_args__ = (
        db.UniqueConstraint("venue_id", "artist_id", "start_time"),
    )

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(
        db.Integer, db.ForeignKey("venues.id"), nullable=False
    )
    artist_id = db.Column(
        db.Integer, db.ForeignKey("artists.id"), nullable=False
    )
    start_time = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now()  # pylint: disable=no-member
    )


class Genre(db.Model):
    """A model representing an genre.

    Attributes:
        id: A unique identifer for the genre object
        name: A str representing the name of the genre
    """

    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)

    def __repr__(self):
        """A Genre object's str representation."""
        return self.name


class Area(db.Model):
    """A model representing a city, state.

    Attributes:
        id: A unique identifier for the area object
        city: A str representing the city in the area object
        state: A str representing the state in the are object
        venues: A list of venues located in the city, state
        artists: A list of artists that are based out of city, state
    """

    __tablename__ = "areas"
    __table_args__ = (db.UniqueConstraint("city", "state"),)

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    venues = db.relationship("Venue", backref="area")
    artists = db.relationship("Artist", backref="area")

    def __repr__(self):
        """An Area object's str representation."""
        return f"{self.city}, {self.state}"


class Music(db.Model):
    """A model representing a song or album for an artist.

    Attributes:
        id: A unique identifier for the music object
        artist_id: The id of the artist who the made the music
        type_: A str representing the release type of the music
        title: A str representing the title of the music
    """

    __table_args__ = (db.UniqueConstraint("artist_id", "type_", "title"),)

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(
        db.Integer, db.ForeignKey("artists.id"), nullable=False
    )
    type_ = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(120), nullable=False)


class Unavailability(db.Model):
    """A model representing an interval of time that an artist is unavailable.

    Attributes:
        id: A unique identifier for the unavailability object
        artist_id: The id of the artist who is unavailable during this interval
        start_time: A datetime representing the start of the interval
        end_time: A datetime representing the end of the interval
    """

    __tablename__ = "unavailability"
    __table_args__ = (
        db.UniqueConstraint("artist_id", "start_time", "end_time"),
        db.CheckConstraint("start_time < end_time"),
    )

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(
        db.Integer, db.ForeignKey("artists.id"), nullable=False
    )
    start_time = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now()  # pylint: disable=no-member
    )
    end_time = db.Column(
        db.DateTime,
        nullable=False
    )

    def __repr__(self):
        """An Unavailability object's str representation."""
        return (self.start_time, self.end_time)

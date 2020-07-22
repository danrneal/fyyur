"""Form objects used used to collect data for the app.

Attributes:
    genres: A list of strs representing accepted genres
    states: A list of strs representing accepted states

Classes:
    VenueForm()
    ArtistForm()
    ShowForm()
    Unavailability()
    MusicForm()
"""

from datetime import datetime

from flask_wtf import Form
from wtforms import (
    BooleanField,
    DateTimeField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    TextAreaField,
)
from wtforms.compat import text_type
from wtforms.validators import (
    URL,
    AnyOf,
    DataRequired,
    Optional,
    Regexp,
    ValidationError,
)

genres = [
    "Alternative",
    "Blues",
    "Classical",
    "Country",
    "Electronic",
    "Folk",
    "Funk",
    "Hip-Hop",
    "Heavy Metal",
    "Instrumental",
    "Jazz",
    "Musical Theatre",
    "Pop",
    "Punk",
    "R&B",
    "Reggae",
    "Rock n Roll",
    "Soul",
    "Swing",
    "Other",
]
states = [
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
]


class AnyOfMultiple:
    """Compares all the incoming data to a sequence of valid inputs.

    Attributes:
        values: A sequence of valid inputs
        message: Error message to raise in case of a validation error.
            `%(values)s` contains the list of values.
        values_formatter: Function used to format the list of values in the
            error message.
    """

    def __init__(self, values, message=None, values_formatter=None):
        """Set-up for the AnyOfMultiple validator."""
        self.values = values
        self.message = message
        if values_formatter is None:
            values_formatter = self.default_values_formatter
        self.values_formatter = values_formatter

    def __call__(self, form, field):
        """Main caller function for the AnyOfMultiple validator."""
        for value in field.data:
            if value not in self.values:

                message = self.message
                if message is None:
                    message = field.gettext(
                        "Invalid value, must be one of: %(values)s."
                    )

                raise ValidationError(
                    message % dict(values=self.values_formatter(self.values))
                )

    @staticmethod
    def default_values_formatter(values):
        """Function used to format the list of values in the error message.

        Args:
            values: A sequence of valid inputs
        """
        return ", ".join(text_type(x) for x in values)


class VenueForm(Form):
    """A form representing a venue.

    Attributes:
        name: A str representing the venue's name
        genres: A list of Genre objects representing what genres are played at
            the venue
        address: A str representing the address of the venue
        city: A str representing the city in which the venue is located
        state: A str representing the state in which the venue is located
        phone: A str representing the phone number for the venue
        website: A str representing the website for the venue
        facebook_link: A str representing a link to the venue's facebook page
        seeking_talent: A bool indicating whether the venue is seeking artists
            or not
        seeking_description: A str describing what type of artist the venue is
            seeking if seeking_talent bool is set to True
        image_link: A str representing a link to an image of the venue
    """

    name = StringField(
        "name", validators=[DataRequired(message="Please enter a name")]
    )
    genres = SelectMultipleField(
        "genres",
        validators=[
            DataRequired(message="Please select at least one genre"),
            AnyOfMultiple(
                genres,
                message="Please only select genres from the list of choices",
            ),
        ],
        choices=[(genre, genre) for genre in genres],
    )
    address = StringField(
        "address", validators=[DataRequired(message="Please enter an address")]
    )
    city = StringField(
        "city", validators=[DataRequired(message="Please enter a city")]
    )
    state = SelectField(
        "state",
        validators=[
            DataRequired(message="Please select a state"),
            AnyOf(states, message="Please select a valid state"),
        ],
        choices=[(state, state) for state in states],
    )
    phone = StringField(
        "phone",
        validators=[
            Optional(),
            Regexp(
                r"^\d{3}-\d{3}-\d{4}$",
                message="Please enter phone number in the format xxx-xxx-xxxx",
            ),
        ],
    )
    website = StringField(
        "website",
        validators=[
            Optional(),
            URL(message="Please enter a valid url for the website"),
        ],
    )
    facebook_link = StringField(
        "facebook_link",
        validators=[
            Optional(),
            URL(message="Please enter a valid url for the facebook link"),
        ],
    )
    seeking_talent = BooleanField(
        "seeking_talent",
        validators=[Optional()],
        false_values=("", None, False),
    )
    seeking_description = TextAreaField(
        "seeking_description", validators=[Optional()]
    )
    image_link = StringField(
        "image_link",
        validators=[
            Optional(),
            URL(message="Please enter a valid url for the image link"),
        ],
    )


class ArtistForm(Form):
    """A form representing an artist.

    Attributes:
        name: A str representing the artist's name
        genres: A list of Genre objects representing what genres the artist
            plays
        city: A str representing the city in which the artist is from
        state: A str representing the state in which the artist is from
        phone: A str representing the artist's phone number
        website: A str representing the artist's website
        facebook_link: A str representing a link to the artist's facebook page
        seeking_venue: A bool indicating whether the artist is seeking a venue
        seeking_description: A str describing what type of venue the artist is
            seeking if seeking_venue bool is set to True
        image_link: A str representing a link to an image of the artist
    """

    name = StringField(
        "name", validators=[DataRequired(message="Please enter a name")]
    )
    genres = SelectMultipleField(
        "genres",
        validators=[
            DataRequired(message="Please select at least one genre"),
            AnyOfMultiple(
                genres,
                message="Please only select genres from the list of choices",
            ),
        ],
        choices=[(genre, genre) for genre in genres],
    )
    city = StringField(
        "city", validators=[DataRequired(message="Please enter a city")]
    )
    state = SelectField(
        "state",
        validators=[
            DataRequired(message="Please select a state"),
            AnyOf(states, message="Please select a valid state"),
        ],
        choices=[(state, state) for state in states],
    )
    phone = StringField(
        "phone",
        validators=[
            Optional(),
            Regexp(
                r"^\d{3}-\d{3}-\d{4}$",
                message="Please enter phone number in the format xxx-xxx-xxxx",
            ),
        ],
    )
    website = StringField(
        "website",
        validators=[
            Optional(),
            URL(message="Please enter a valid url for the website"),
        ],
    )
    facebook_link = StringField(
        "facebook_link",
        validators=[
            Optional(),
            URL(message="Please enter a valid url for the facebook link"),
        ],
    )
    seeking_venue = BooleanField(
        "seeking_venue",
        validators=[Optional()],
        false_values=("", None, False),
    )
    seeking_description = TextAreaField(
        "seeking_description", validators=[Optional()]
    )
    image_link = StringField(
        "image_link",
        validators=[
            Optional(),
            URL(message="Please enter a valid url for the image link"),
        ],
    )


class ShowForm(Form):
    """A form representing a show.

    Attributes:
        venue_id: The id of the venue that the show was at
        artist_id: The id of the artist that performed at the show
        start_time: A datetime that represents the start time of the show
            defaulting to today
    """

    venue_id = IntegerField(
        "venue_id",
        validators=[DataRequired(message="Please enter a venue id")],
    )
    artist_id = IntegerField(
        "artist_id",
        validators=[DataRequired(message="Please enter an artist id")],
    )
    start_time = DateTimeField(
        "start_time",
        validators=[DataRequired(message="Please enter a start time")],
        default=datetime.today(),
    )


class UnavailabilityForm(Form):
    """A form representing an unavailability for an artist.

    Attributes:
        start_time: A datetime that represents the start time of the interval
            the artist is unavailable defaulting to today
        end_time: A datetime that represents the end time of the interval the
            artist is unavailable
    """

    start_time = DateTimeField(
        "start_time",
        validators=[DataRequired(message="Please enter a start time")],
        default=datetime.today(),
    )
    end_time = DateTimeField(
        "end_time",
        validators=[DataRequired(message="Please enter an end time")],
    )


class MusicForm(Form):
    """A form representing a song or album for an artist.

    Attributes:
        type_: A str representing the release type
        title: A str representing the title of the release
    """

    type_ = SelectField(
        "type_",
        validators=[
            DataRequired(message="Please select a release type"),
            AnyOf(
                ["Album", "Song"], message="Please select a valid release type"
            ),
        ],
        choices=[("Album", "Album"), ("Song", "Song")],
    )
    title = StringField(
        "title", validators=[DataRequired(message="Please enter a title")]
    )

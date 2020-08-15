"""A musical venue and artist booking site.

Fyyur is a musical venue and artist booking site that facilitates the discovery
and bookings of shows between local performing artists and venues

Usage: flask run
"""

# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import logging
import os
import sys
from datetime import datetime
from logging import FileHandler, Formatter

import babel
import dateutil.parser
from flask import (
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from forms import (
    ArtistForm,
    MusicForm,
    ShowForm,
    UnavailabilityForm,
    VenueForm,
)
from models import (
    Area,
    Artist,
    Genre,
    Music,
    Show,
    Unavailability,
    Venue,
    app,
    db,
)

# ----------------------------------------------------------------------------#
# Filters
# ----------------------------------------------------------------------------#


def format_datetime(value, datetime_format="medium"):
    """Converts a datetime str to a format that is understood by the db.

    Args:
        value: A str representing a datetime
        datetime_format: A str representing the desired format of the returned
            datetime, accepted values are ('full', 'medium')

    Returns:
        A date formatted according to the given format
    """
    date = dateutil.parser.parse(value)

    if datetime_format == "full":
        datetime_format = "EEEE MMMM, d, y 'at' h:mma"
    elif datetime_format == "medium":
        datetime_format = "EE MM, dd, y h:mma"

    return babel.dates.format_datetime(date, datetime_format)


app.jinja_env.filters["datetime"] = format_datetime


# ----------------------------------------------------------------------------#
# Helpers
# ----------------------------------------------------------------------------#


def get_genres(genre_names):
    """Gets a list of genre objects from a list of genre names.

    Args:
        genre_names: A list of strs representing the names of genres

    Returns:
        genres: A list of genre objects corresponding the the genre names
            passed in
    """
    genres = []

    for genre_name in genre_names:
        genre = Genre.query.filter_by(name=genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            db.session.add(genre)
        genres.append(genre)

    return genres


def get_area_id(city, state):
    """Gets the area id of an area from a city and state.

    Args:
        city: A str representing the city of an area object
        state: A str representing the state of an area object

    Returns:
        area_id: An int representing the id of the area object cooresponding
            to a city and state
    """
    area = Area.query.filter(Area.city == city, Area.state == state).first()

    if not area:
        area = Area(city=city, state=state)
        db.session.add(area)
        db.session.flush()

    return area.id


# ----------------------------------------------------------------------------#
# Controllers
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    """The route handler for the homepage.

    Returns:
        A rendered html template for the homepage
    """
    recent_venues = (
        Venue.query.order_by(db.desc(Venue.created_at)).limit(9).all()
    )
    recent_artists = (
        Artist.query.order_by(db.desc(Artist.created_at)).limit(9).all()
    )
    recently_listed = []

    while len(recently_listed) < 9 and (
        len(recent_artists) > 0 or len(recent_venues) > 0
    ):
        if (
            len(recent_artists) == 0
            or recent_venues[0].created_at > recent_artists[0].created_at
        ):
            recent_venues[0].type = "Venue"
            recently_listed.append(recent_venues.pop(0))
        else:
            recent_artists[0].type = "Artist"
            recently_listed.append(recent_artists.pop(0))

    print(recently_listed)
    return render_template("pages/home.html", recently_listed=recently_listed)


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    """Route handler for looking at all venues grouped by city, state.

    Returns:
        A template for all venues populated with venues grouped by city, state
    """
    areas = Area.query.filter(
        Area.venues != None  # noqa: E711, pylint: disable=singleton-comparison
    ).all()
    return render_template("pages/venues.html", areas=areas)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    """Route handler for venue search.

    Returns:
        A template with the search results
    """
    search_term = request.form.get("search_term", "")
    areas = Area.query.filter(
        Area.city.ilike(f"%{search_term}%")
        | Area.state.ilike(f"%{search_term}%")
    ).all()
    area_ids = [area.id for area in areas]
    data = Venue.query.filter(
        Venue.name.ilike(f"%{search_term}%") | Venue.area_id.in_(area_ids)
    ).all()
    results = {"count": len(data), "data": data}

    return render_template(
        "pages/search_venues.html", results=results, search_term=search_term
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    """Route handler for showing the details for a venue.

    Args:
        venue_id: A str representing the id of the venue to show details for

    Returns:
        A template with the detail view for a venue
    """
    venue = Venue.query.get(venue_id)
    venue.city = venue.area.city
    venue.state = venue.area.state
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

    return render_template("pages/show_venue.html", venue=venue)


#  Update Venue
#  ----------------------------------------------------------------


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue_form(venue_id):
    """Displays the form for editing a venue.

    Args:
        venue_id: A str representing the id of the venue to edit

    Returns:
        A html template for the venue form which has been pre-populated
    """
    venue = Venue.query.get(venue_id)
    venue.city = venue.area.city
    venue.state = venue.area.state
    form = VenueForm(obj=venue)

    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    """Updates an existing venue in the db from a form submission.

    Args:
        venue_id: A str representing the id of the venue to update

    Returns:
        The template for the venue's detail page
    """
    form = VenueForm()
    if not form.validate():
        flash(
            list(form.errors.values())[0][0], "error",
        )
        return redirect(url_for("edit_venue_form", venue_id=venue_id))

    error = False

    try:
        venue_name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        venue = Venue.query.get(venue_id)
        venue.name = venue_name
        venue.genres = get_genres(request.form.getlist("genres"))
        venue.address = request.form.get("address")
        venue.area_id = get_area_id(city, state)
        venue.phone = request.form.get("phone")
        venue.website = request.form.get("website")
        venue.facebook_link = request.form.get("facebook_link")
        venue.seeking_talent = bool(request.form.get("seeking_talent"))
        venue.seeking_description = request.form.get("seeking_description")
        venue.image_link = request.form.get("image_link")
        db.session.commit()
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash(f"Venue {venue_name} was unable to be updated!", "error")
        abort(500)

    flash(f"Venue {venue_name} was successfully updated!")

    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    """Displays the form for creating a venue.

    Returns:
        A html template for the venue form
    """
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    """Creates a new venue in the db from a form submission.

    Returns:
        The template for a list of all venues
    """
    form = VenueForm()
    if not form.validate():
        flash(
            list(form.errors.values())[0][0], "error",
        )
        return redirect(url_for("create_venue_form"))

    error = False

    try:
        venue_name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        venue = Venue(
            name=venue_name,
            genres=get_genres(request.form.getlist("genres")),
            address=request.form.get("address"),
            area_id=get_area_id(city, state),
            phone=request.form.get("phone"),
            website=request.form.get("website"),
            facebook_link=request.form.get("facebook_link"),
            seeking_talent=bool(request.form.get("seeking_talent")),
            seeking_description=request.form.get("seeking_description"),
            image_link=request.form.get("image_link"),
        )
        db.session.add(venue)
        db.session.commit()
        venue_id = venue.id

    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    if error:
        flash(f"Venue {venue_name} was unable to be listed!", "error")
        abort(500)

    flash(f"Venue {venue_name} was successfully listed!")

    return redirect(url_for("show_venue", venue_id=venue_id))


#  Delete Venue
#  ----------------------------------------------------------------


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    """Route handler to delete a venue from the db.

    Args:
        venue_id: A str representing the id of the venue to delete

    Returns:
        response: A json object signalling the deletion request was successful
    """
    error = False

    try:
        venue = Venue.query.get(venue_id)
        venue_name = venue.name
        db.session.delete(venue)
        db.session.commit()
        response = {"success": True}
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash(f"Venue {venue_name} was unable to be deleted!", "error")
        abort(500)

    flash(f"Venue {venue_name} was successfully deleted!")

    return jsonify(response)


#  Artists
#  ----------------------------------------------------------------


@app.route("/artists")
def artists():
    """Route handler for showing a list of artists.

    Returns:
        A template for a list of all artists
    """
    artists_all = Artist.query.all()
    return render_template("pages/artists.html", artists=artists_all)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    """Route handler for artist search.

    Returns:
        A template with the search results
    """
    search_term = request.form.get("search_term", "")
    areas = Area.query.filter(
        Area.city.ilike(f"%{search_term}%")
        | Area.state.ilike(f"%{search_term}%")
    ).all()
    area_ids = [area.id for area in areas]
    data = Artist.query.filter(
        Artist.name.ilike(f"%{search_term}%") | Artist.area_id.in_(area_ids)
    ).all()
    results = {"count": len(data), "data": data}

    return render_template(
        "pages/search_artists.html", results=results, search_term=search_term
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    """Route handler for showing the details for an artist.

    Args:
        artist_id: A str representing the id of the artist to show details for

    Returns:
        A template with the detail view for an artist
    """
    artist = Artist.query.get(artist_id)
    artist.city = artist.area.city
    artist.state = artist.area.state
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
    music_form = MusicForm()
    unavailability_form = UnavailabilityForm()

    return render_template(
        "pages/show_artist.html",
        artist=artist,
        music_form=music_form,
        unavailability_form=unavailability_form,
    )


#  Create Music


@app.route("/artists/<int:artist_id>/music/create", methods=["POST"])
def create_music(artist_id):
    """Creates a new featured song/album for the artist from form submission.

    Returns:
        The detail view for the artist
    """
    form = MusicForm()
    if not form.validate():
        flash(
            list(form.errors.values())[0][0], "error",
        )
        return redirect(url_for("show_artist", artist_id=artist_id))

    error = False

    try:
        music_type = request.form.get("type_")
        music_title = request.form.get("title")
        music = Music(artist_id=artist_id, type_=music_type, title=music_title)
        db.session.add(music)
        db.session.commit()
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash(f"{music_type} {music_title} could not be added!", "error")
        abort(500)

    flash(f"{music_type} {music_title} was successfully added!")

    return redirect(url_for("show_artist", artist_id=artist_id))


#  Delete Music


@app.route("/artists/<int:artist_id>/music/<int:music_id>", methods=["DELETE"])
def delete_music(artist_id, music_id):  # pylint: disable=unused-argument
    """Route handler to delete an piece of music for an artist from the db.

    Args:
        artist_id: A str representing the id of the artist who's music is being
            deleted
        music_id: A str representing the id of the music to delete

    Returns:
        response: A json object signalling the deletion request was successful
    """
    error = False

    try:
        music = Music.query.get(music_id)
        music_type = music.type_
        music_title = music.title
        db.session.delete(music)
        db.session.commit()
        response = {"success": True}
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash(f"{music_type} {music_title} was unable to be deleted!", "error")
        abort(500)

    flash(f"{music_type} {music_title} was successfully deleted!")

    return jsonify(response)


#  Create Unavailability


@app.route("/artists/<int:artist_id>/unavailability/create", methods=["POST"])
def create_unavailability(artist_id):
    """Creates a new unavailability for the artist from a form submission.

    Returns:
        The detail view for the artist
    """
    form = UnavailabilityForm()
    if not form.validate():
        flash(
            list(form.errors.values())[0][0], "error",
        )
        return redirect(url_for("show_artist", artist_id=artist_id))

    error = False

    try:
        unavailability = Unavailability(
            artist_id=artist_id,
            start_time=request.form.get("start_time"),
            end_time=request.form.get("end_time"),
        )
        db.session.add(unavailability)
        db.session.commit()
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash("Unavailability could not be added!", "error")
        abort(500)

    flash("Unavailability was successfully added!")

    return redirect(url_for("show_artist", artist_id=artist_id))


# Delete Unavailability


@app.route(
    "/artists/<int:artist_id>/unavailability/<int:unavailability_id>",
    methods=["DELETE"],
)
def delete_unavailability(
    artist_id, unavailability_id  # pylint: disable=unused-argument
):
    """Route handler to delete an unavailability for an artist from the db.

    Args:
        artist_id: A str representing the id of the artist who's unavailability
            is being deleted
        unavailability_id: A str representing the id of the unavailability to
            delete

    Returns:
        response: A json object signalling the deletion request was successful
    """
    error = False

    try:
        unavailability = Unavailability.query.get(unavailability_id)
        db.session.delete(unavailability)
        db.session.commit()
        response = {"success": True}
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash("Unavailability was unable to be deleted!", "error")
        abort(500)

    flash("Unavailability was successfully deleted!")

    return jsonify(response)


#  Update Artist
#  ----------------------------------------------------------------


@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist_form(artist_id):
    """Displays the form for editing an artist.

    Args:
        artist_id: A str representing the id of the artist to edit

    Returns:
        A html template for the artist form which has been pre-populated
    """
    artist = Artist.query.get(artist_id)
    artist.city = artist.area.city
    artist.state = artist.area.state
    form = ArtistForm(obj=artist)

    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    """Updates an existing artist in the db from a form submission.

    Args:
        artist_id: A str representing the id of the artist to update

    Returns:
        The template for the artist's detail page
    """
    form = ArtistForm()
    if not form.validate():
        flash(
            list(form.errors.values())[0][0], "error",
        )
        return redirect(url_for("edit_artist_form", artist_id=artist_id))

    error = False

    try:
        artist_name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        artist = Artist.query.get(artist_id)
        artist.name = artist_name
        artist.genres = get_genres(request.form.getlist("genres"))
        artist.area_id = get_area_id(city, state)
        artist.phone = request.form.get("phone")
        artist.website = request.form.get("website")
        artist.facebook_link = request.form.get("facebook_link")
        artist.seeking_venue = bool(request.form.get("seeking_venue"))
        artist.seeking_description = request.form.get("seeking_description")
        artist.image_link = request.form.get("image_link")
        db.session.commit()
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash(f"Artist {artist_name} was unable to be updated!", "error")
        abort(500)

    flash(f"Artist {artist_name} was successfully updated!")

    return redirect(url_for("show_artist", artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    """Displays the form for creating an artist.

    Returns:
        A html template for the artist form
    """
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    """Creates a new artist in the db from a form submission.

    Returns:
        The template for a list of all artists
    """
    form = ArtistForm()
    if not form.validate():
        flash(
            list(form.errors.values())[0][0], "error",
        )
        return redirect(url_for("create_artist_form"))

    error = False

    try:
        artist_name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        artist = Artist(
            name=artist_name,
            genres=get_genres(request.form.getlist("genres")),
            area_id=get_area_id(city, state),
            phone=request.form.get("phone"),
            website=request.form.get("website"),
            facebook_link=request.form.get("facebook_link"),
            seeking_venue=bool(request.form.get("seeking_venue")),
            seeking_description=request.form.get("seeking_description"),
            image_link=request.form.get("image_link"),
        )
        db.session.add(artist)
        db.session.commit()
        artist_id = artist.id
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash(f"Artist {artist_name} was unable to be listed!", "error")
        abort(500)

    flash(f"Artist {artist_name} was successfully listed!")

    return redirect(url_for("show_artist", artist_id=artist_id))


#  Delete Artist
#  ----------------------------------------------------------------


@app.route("/artists/<artist_id>", methods=["DELETE"])
def delete_artist(artist_id):
    """Route handler to delete a artist from the db.

    Args:
        artist_id: A str representing the id of the artist to delete

    Returns:
        response: A json object signalling the deletion request was successful
    """
    error = False

    try:
        artist = Artist.query.get(artist_id)
        artist_name = artist.name
        db.session.delete(artist)
        db.session.commit()
        response = {"success": True}
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash(f"Artist {artist_name} was unable to be deleted!", "error")
        abort(500)

    flash(f"Artist {artist_name} was successfully deleted!")

    return jsonify(response)


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    """Route handler for showing a list of shows.

    Returns:
        A template for a list of all shows
    """
    shows_all = Show.query.all()

    for show in shows_all:
        show.venue_name = show.venue.name
        show.artist_name = show.artist.name
        show.artist_image_link = show.artist.image_link
        show.start_time = str(show.start_time)

    return render_template("pages/shows.html", shows=shows_all)


#  Create Show
#  ----------------------------------------------------------------


@app.route("/shows/create", methods=["GET"])
def create_show_form():
    """Displays the form for creating a show.

    Returns:
        A html template for the show form
    """
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    """Creates a new show in the db from a form submission.

    Returns:
        A redirect to the shows page
    """
    form = ShowForm()
    if not form.validate():
        flash(
            list(form.errors.values())[0][0], "error",
        )
        return redirect(url_for("create_show_form"))

    error = False

    try:

        venue_id = request.form.get("venue_id")
        artist_id = request.form.get("artist_id")
        start_time = request.form.get("start_time")
        unavailabilities = Unavailability.query.filter_by(
            artist_id=artist_id
        ).all()

        for unavailability in unavailabilities:
            if (
                str(unavailability.start_time)
                > start_time
                < str(unavailability.end_time)
            ):
                flash("Artist is unavailable at selected time")
                return redirect(url_for("create_show_form"))

        show = Show(
            venue_id=venue_id, artist_id=artist_id, start_time=start_time
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
        flash("Show was unable to be listed!", "error")
        abort(500)

    flash("Show was successfully listed!")

    return redirect(url_for("shows"))


# ----------------------------------------------------------------------------#
# Error Handlers
# ----------------------------------------------------------------------------#


@app.errorhandler(404)
def not_found_error(error):  # pylint: disable=unused-argument
    """Error handler for 404 not found.

    Args:
        error: unused

    Returns:
        A custom template for the error message
    """
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):  # pylint: disable=unused-argument
    """Error handler for 500 internal server error.

    Args:
        error: unused

    Returns:
        A custom template for the error message
    """
    return render_template("errors/500.html"), 500


# ----------------------------------------------------------------------------#
# Debug
# ----------------------------------------------------------------------------#

if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter(
            "%(asctime)s %(levelname)s: "
            "%(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    app.run(host=host, port=port)

# Fyyur

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.

## Set-up

Set-up a virtual environment and activate it:

```bash
python3 -m venv env
source env/bin/activate
```

You should see (env) before your command prompt now. (You can type `deactivate` to exit the virtual environment any time.)

Install the requirements:

```bash
pip install -U pip
pip install -r requirements.txt
```

Initialize and set up the database:

```bash
dropdb fyyur
createdb fyyur
flask db upgrade
```

## Usage

Make sure you are in the virtual environment (you should see (env) before your command prompt). If not `source /env/bin/activate` to enter it.

```bash
Usage: flask run
```

## Screenshots

![Fyyur Homepage](https://i.imgur.com/6zhIbPP.png)

![Fyyur Venue Detail Page](https://i.imgur.com/h2Dc086.png)

![Fyyur Artist Detail Page](https://i.imgur.com/O94kDcW.png)

## Credit

[Udacity's Full Stack Web Developer Nanodegree Program](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044)

## License

Fyyur is licensed under the [MIT license](https://github.com/danrneal/fyyur/blob/master/LICENSE).

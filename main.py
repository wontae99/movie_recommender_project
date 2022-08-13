from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import ValidationError, DataRequired
import requests

movie_api = "b8aafa6f10f8e0d81f357fd9d52efe94"
access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiOGFhZmE2ZjEwZjhlMGQ4MWYzNTdmZDlkNTJlZmU5NCIsInN1YiI6IjYyZjdiZDE2NzI0ZGUxMDA4MmY1MDA1YyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.iZy0au9XyQl_l_Y0hX-_-NyWPmlWVXdiZ6Yh883ec04"
base_url = "https://api.themoviedb.org/3/search/movie?"
id_search_url = "https://api.themoviedb.org/3/movie/"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, unique=True, nullable=False)
    description = db.Column(db.String(250), unique=True, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, unique=True, nullable=True)
    review = db.Column(db.String(250), unique=True, nullable=True)
    img_url = db.Column(db.String(250), unique=True, nullable=False)

db.create_all()

#Check if rating input is between 0~10
def rating_check(form ,field):
    if float(field.data) > 10 or float(field.data) < 0:
        raise ValidationError("Input must be a number between 0~10")

#Edit Form
class EditForm(FlaskForm):
    new_rating = FloatField("Your Rating(0~10)", validators=[rating_check])
    new_review = StringField("Your Review")
    submit = SubmitField("Done")

#Add Form
class AddForm(FlaskForm):
    movie_title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")

#Adding Data for Test
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
#
# db.session.add(new_movie)
# db.session.commit()


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=['GET','POST'])
def edit():
    form = EditForm()
    movie_id = request.args.get('id')
    movie_selected = Movie.query.get(movie_id)
    if form.validate_on_submit():
        if form.new_review.data != '':
            movie_selected.review = form.new_review.data
        if form.new_rating.data != '':
            movie_selected.rating = form.new_rating.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form, movie=movie_selected)


@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=['GET','POST'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        request_url = f"{base_url}api_key={movie_api}&query={form.movie_title.data}"
        response = requests.get(url=request_url)
        data = response.json()['results']
        return render_template('select.html', data=data)
    return render_template('add.html', form=form)

@app.route('/find', methods=['GET','POST'])
def find():
    movie_id = request.args.get('id')
    if movie_id:
        url = f"{id_search_url}{movie_id}?api_key={movie_api}"
        response = requests.get(url=url)
        data = response.json()
        title = data['title']
        year = data['release_date']
        description = data['overview']
        review=data['tagline']
        img_request_url = f"{id_search_url}{movie_id}/images?api_key={movie_api}"
        response_img = requests.get(url=img_request_url)
        img_url_partial = response_img.json()['posters'][0]['file_path']
        img_url = f"{MOVIE_DB_IMAGE_URL}/{img_url_partial}"
        new_movie = Movie(
            title=title,
            description=description,
            review=review,
            year=year,
            img_url=img_url
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

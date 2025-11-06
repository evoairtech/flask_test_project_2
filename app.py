from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_wtf import CSRFProtect
from forms import GenresForm
from movies_data import movies_list


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'  # required for CSRF protection

# Initialize CSRF protection
csrf = CSRFProtect(app)


GENRES = [
    {"id": 1, "name": "Action"},
    {"id": 2, "name": "Adventure"},
    {"id": 3, "name": "Animation"},
    {"id": 4, "name": "Biography"},
    {"id": 5, "name": "Comedy"},
    {"id": 6, "name": "Crime"},
    {"id": 7, "name": "Documentary"},
    {"id": 8, "name": "Drama"},
    {"id": 9, "name": "Fantasy"},
    {"id": 10, "name": "Historical"},
    {"id": 11, "name": "Horror"},
    {"id": 12, "name": "Musical"},
    {"id": 13, "name": "Mystery"},
    {"id": 14, "name": "Romance"},
    {"id": 15, "name": "Sci-Fi"},
    {"id": 16, "name": "Sports"},
    {"id": 17, "name": "Thriller"},
    {"id": 18, "name": "War"},
    {"id": 19, "name": "Western"}
]



@app.route('/', methods=['GET', 'POST'])
def index():
    form = GenresForm()
    choices_list = []
    for item in GENRES:
        genre_id = str(item['id'])
        genre_name = item['name']
        genre_tuple = (genre_id, genre_name)
        choices_list.append(genre_tuple)
    form.chosen_genres.choices = choices_list

    if request.method == 'POST':
        selected_ids = request.form.getlist('chosen_genres')
        selected_genres = []
        for genre in GENRES:
            if str(genre['id']) in selected_ids:
                selected_genres.append(genre['name'])
        
        # Store in session for the redirect
        session['selected_genres'] = selected_ids
        
        # If client requests JSON, return JSON response. Use a "contains" check
        # because Accept headers can include multiple types (e.g. "application/json, */*").
        accept = request.headers.get('Accept', '')
        if 'application/json' in accept or request.is_json:
            return jsonify({
                "selected_ids": selected_ids,
                "selected_genres": selected_genres,
                "redirect_url": url_for('result')  # Include redirect URL in JSON
            })
        
        # Otherwise redirect to results page
        return redirect(url_for('result'))

    return render_template('index.html', MGform=form)


@app.route('/result', methods=['GET'])
def result():
    selected_ids = session.get('selected_genres', [])
    selected_genres = []
    for genre in GENRES:
        if str(genre['id']) in selected_ids:
            selected_genres.append(genre['name'])
            
    print("Selected genres:", selected_genres)

    movie_results = []
    for movie in movies_list:
        # Normalize movie genres to a list to avoid accidental substring matches
        movie_genres = movie.get('genre', [])
        if isinstance(movie_genres, str):
            movie_genres = [movie_genres]

        if any(genre in movie_genres for genre in selected_genres):
            movie_results.append(movie)
            
    print("Movie results:", movie_results)

    session.pop('selected_genres', None)
    return render_template('results.html', selected_genres=selected_genres, movie_results=movie_results)



if __name__ == '__main__':
    app.run(debug=True)

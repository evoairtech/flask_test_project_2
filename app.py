"""
Annotated Flask application for genre selection and movie filtering.

This file is intentionally commented to explain each section. The runtime
behavior is unchanged: it renders a form on `/`, accepts form submissions,
optionally returns JSON for API clients, and shows results on `/result`.
"""

# --- imports -----------------------------------------------------------------
# Flask core objects used for routing, rendering templates, request data,
# redirects, JSON responses and session storage.
from flask import Flask, render_template, request, redirect, url_for, jsonify, session

# CSRF protection from Flask-WTF (protects POST forms and AJAX POSTs when
# configured properly).
from flask_wtf import CSRFProtect

# Local form class (WTForms) used to build the checkbox list.
from forms import GenresForm

# Local movies data (list of dicts). Each movie dict is expected to have
# keys like 'id', 'name', 'genre', etc.
from movies_data import movies_list


# Create the Flask application instance. Configuration (like SECRET_KEY)
# follows immediately below.
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'  # required for CSRF protection

# Initialize CSRF protection for forms. Flask-WTF will validate CSRF tokens
# on incoming POST requests when the form includes the hidden CSRF field.
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
    """Render the selection form (GET) and handle form submissions (POST).

    The form uses a SelectMultipleField rendered as checkboxes. On POST we
    collect the selected ids, optionally return JSON for API clients, or
    store the selection in the session and redirect to the results page.
    """

    # Create the form instance and populate its choices from GENRES.
    # Each choice is a (value, label) tuple; the value must be a string.
    form = GenresForm()
    choices_list = []
    for item in GENRES:
        genre_id = str(item['id'])
        genre_name = item['name']
        genre_tuple = (genre_id, genre_name)
        choices_list.append(genre_tuple)
    form.chosen_genres.choices = choices_list   # Inject choices for the form (which are taken from the GENRES list) at runtime 

    # Handle form submission. On POST, read selected values from
    # `request.form.getlist` since multiple values are sent under the same field name.
    if request.method == 'POST':
        selected_ids = request.form.getlist('chosen_genres')
        selected_genres = []
        for genre in GENRES:
            if str(genre['id']) in selected_ids:
                selected_genres.append(genre['name'])
        
        # Store in session for the redirect to results page.
        session['selected_genres'] = selected_ids
        
        # If client requests JSON, return JSON response. Use a "contains" check
        # because Accept headers can include multiple types (e.g. "application/json, */*").
        accept = request.headers.get('Accept', '')
        if 'application/json' in accept or request.is_json:
            return jsonify({
                "selected_ids": selected_ids,
                "selected_genres": selected_genres,
                "redirect_url": url_for('result')  # Include redirect URL in JSON response
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


@app.route('/submit', methods=['POST'])
def submit():
    """
    Handle AJAX/JSON form submissions from the frontend.

    Flow:
    1. Frontend sends POST request with JSON containing selected genre IDs.
    2. Server parses JSON, filters `movies_list` for movies with matching IDs.
    3. Stores filtered movies in session for access by /api route.
    4. Returns JSON response with success status, redirect URL, and movie count.

    This ensures:
    - No HTML is accidentally returned (avoids "Unexpected token '<'" in fetch).
    - The session always contains the latest submitted movies for /api.
    """

    # 1️⃣ Ensure the request is JSON
    if request.is_json:
        # Parse JSON payload into Python dictionary
        data = request.get_json() #request. pareses the JSON payload into a Python dictionary

        # 2️⃣ Extract selected genre/movie IDs from JSON
        # Frontend sends: { "chosen_genres": ["1", "3", "5"] }
        selected_ids = data.get('chosen_genres', [])

        # 3️⃣ Filter movies_list for movies matching selected IDs
        # Convert movie['id'] to str to match string IDs from JSON
        submitted_movies = [
            movie for movie in movies_list
            if str(movie['id']) in selected_ids
        ]

        # 4️⃣ Store filtered movies in session
        # This allows /api route to access them later
        session['submitted_movies'] = submitted_movies

        # 5️⃣ Return JSON response to frontend
        # Frontend can redirect to /api using redirect_url
        return jsonify({
            "status": "success",                     # Indicates submission worked
            "redirect_url": url_for('api'),          # Frontend can navigate here
            "submitted_count": len(submitted_movies) # Optional: number of movies found
        })

    # 6️⃣ Handle bad requests (not JSON)
    # Returns HTTP 400 with descriptive error
    return jsonify({"error": "Expected JSON"}), 400




@app.route('/api', methods=['GET'])
def api():
    """
    Display the list of movies submitted via the /submit route.

    Flow:
    1. Retrieves the last submitted movies from the session.
    2. Prints them to the console for debugging purposes.
    3. Renders 'api.html', passing the movie data for display.

    Notes:
    - `session.get('submitted_movies', [])` ensures that if the session
      has no submitted movies, we get an empty list instead of None.
    - This route is intended for viewing results after a JSON-based
      form submission.
    - The frontend can redirect here after receiving the JSON response
      from /submit.
    """
    
    # 1️⃣ Get the submitted movies from the session
    # If no movies were submitted yet, default to an empty list
    submitted_movies = session.get('submitted_movies', [])

    # 2️⃣ Optional: print to console for debugging
    print("Submitted movies:", submitted_movies)

    # 3️⃣ Render template and pass movie_data for frontend
    # In 'api.html', movie_data is converted to JSON for display
    return render_template('api.html', movie_data=submitted_movies)


if __name__ == '__main__':
    app.run(debug=True)

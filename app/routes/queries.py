from flask import Blueprint, render_template, request
from app.database import Database

queries_bp = Blueprint("query", __name__)


@queries_bp.route("/list_tables")
def list_tables():

    query = """ show tables; """

    with Database() as db:
        tables = db.execute(query)
    return render_template("list_tables.html", tables=tables)


@queries_bp.route("/search_movie", methods=["POST"])
def search_movie():
    movie_name = request.form["movie_name"]

    # >>>> TODO 2: Search Motion Picture by Motion picture name (parameterized). <<<<
    #              List the motion picture name along with its rating, production, and budget.

    query = """ select name, rating, production, budget from MotionPicture where name like %s; """

    with Database() as db:
        movies = db.execute(query, (f"%{movie_name}%",))
    return render_template("search_results.html", movies=movies)


@queries_bp.route("/search_liked_movies", methods=["POST"])
def search_liked_movies():
    user_email = request.form["user_email"]

    # >>>> TODO 3: Find the movies that have been liked by a specific user. A user is uniquely identified by their email (parameterized). <<<<
    #              List the movie `name`, `rating`, `production` and `budget`.

    query = """ SELECT mp.name, mp.rating, mp.production, mp.budget 
FROM MotionPicture as mp, Likes as l, Movie as m 
WHERE mp.id = m.mpid AND l.uemail = %s AND l.mpid=mp.id;  """

    with Database() as db:
        movies = db.execute(query, (user_email,))
    return render_template("search_results.html", movies=movies)


@queries_bp.route("/search_by_country", methods=["POST"])
def search_by_country():
    country = request.form["country"]

    # >>>> TODO 4: Search motion pictures by their shooting location country. <<<<
    #              List only the motion picture names without any duplicates.

    query = """ SELECT DISTINCT mp.name FROM MotionPicture as mp, Location as l WHERE mp.id = l.mpid AND l.country = %s;  """

    with Database() as db:
        movies = db.execute(query, (country,))
    return render_template("search_results_by_country.html", movies=movies)


@queries_bp.route("/search_directors_by_zip", methods=["POST"])
def search_directors_by_zip():
    zip_code = request.form["zip_code"]

    # >>>> TODO 5: List all directors who have directed a TV series shot in a specific zip code (parameterized). <<<<
    #              List the director’s name and TV series name only, without duplicates.

    query = """ SELECT DISTINCT p.name, mp.name 
FROM People as p, Series as s, Role as r, Location as l, MotionPicture as mp 
WHERE r.mpid = s.mpid AND l.mpid = s.mpid AND l.zip = %s AND s.mpid=mp.id AND r.role_name = 'Director' AND r.pid = p.id; """

    with Database() as db:
        results = db.execute(query, (zip_code,))
    return render_template("search_directors_results.html", results=results)


@queries_bp.route("/search_awards", methods=["POST"])
def search_awards():
    k = int(request.form["k"])

    # >>>> TODO 6: Identify the individuals who have received more than “k” (parameterized) awards for a single motion picture in the same year. <<<<
    #              Return the individual’s name, the motion picture’s name, the award year, and the award count.

    query = """ SELECT p.name, mp.name, a.award_year, COUNT(*)
FROM People as p, MotionPicture as mp, Award as a
WHERE a.mpid = mp.id AND a.pid = p.id
GROUP BY p.id, a.award_year, a.award_year
HAVING COUNT(*) > %s; """

    with Database() as db:
        results = db.execute(query, (k,))
    return render_template("search_awards_results.html", results=results)


@queries_bp.route("/find_youngest_oldest_actors", methods=["GET"])
def find_youngest_oldest_actors():

    # >>>> TODO 7: Find the youngest and oldest actors who have won at least one award. <<<<
    #              List the actor names and their age at the time they received the award. 
    #              Age must be computed using the actor’s date of birth and the award-year only. 
    #              In case of a tie, list all tied actors.

    query = """
WITH Age AS (SELECT p.name,
TIMESTAMPDIFF(YEAR, STR_TO_DATE(p.dob, '%%Y-%%m-%%d'), STR_TO_DATE(CONCAT(a.award_year, '-01-01'), '%%Y-%%m-%%d')) AS age
FROM People p
JOIN Award a ON p.id = a.pid
JOIN Role r ON p.id = r.pid AND r.mpid = a.mpid
WHERE r.role_name = 'Actor')
SELECT age, name FROM Age
WHERE age = (SELECT MIN(age) FROM Age) OR age = (SELECT MAX(age) FROM Age);
"""

    with Database() as db:
        actors = db.execute(query)

    # Filter out actors with null ages (if any)
    actors = [actor for actor in actors if actor[1] is not None]
    if actors:
        min_age = min(actors, key=lambda x: x[1])[1]
        max_age = max(actors, key=lambda x: x[1])[1]
        youngest_actors = [actor for actor in actors if actor[1] == min_age]
        oldest_actors = [actor for actor in actors if actor[1] == max_age]
        return render_template(
            "actors_by_age.html",
            youngest_actors=youngest_actors,
            oldest_actors=oldest_actors,
        )
    else:
        return render_template(
            "actors_by_age.html", youngest_actors=[], oldest_actors=[]
        )


@queries_bp.route("/search_producers", methods=["POST"])
def search_producers():
    box_office_min = float(request.form["box_office_min"])
    budget_max = float(request.form["budget_max"])

    # >>>> TODO 8: List the American producers whose movies achieved a box office collection greater than or equal to “X” (parameterized) with a budget less than or equal to “Y” (parameterized). <<<<
    #              List the producer’s name and movie name along with its box office collection and budget.

    query = """ SELECT p.name, mp.name, mp.budget, m.boxoffice_collection
FROM People as p, MotionPicture as mp, Movie as m, Role as r
WHERE p.id = r.pid AND r.role_name = "Producer" AND p.nationality = "USA"
AND mp.id = m.mpid AND r.mpid = m.mpid
AND boxoffice_collection >= %s AND budget <= %s; """

    with Database() as db:
        results = db.execute(query, (box_office_min, budget_max))
    return render_template("search_producers_results.html", results=results)


@queries_bp.route("/search_multiple_roles", methods=["POST"])
def search_multiple_roles():
    rating_threshold = float(request.form["rating_threshold"])

    # >>>> TODO 9: List the individuals who played multiple roles in a motion picture with a rating greater than “X” (parameterized). <<<<
    #              List the individual’s name, the motion picture name, and the number of roles the individual played in that motion picture.

    query = """ SELECT p.name, mp.name, COUNT(*)
FROM People as p, MotionPicture as mp, Role as r
WHERE p.id = r.pid AND r.mpid = mp.id AND mp.rating > %s
GROUP BY p.id, mp.id
HAVING COUNT(*) > 1;
"""

    with Database() as db:
        results = db.execute(query, (rating_threshold,))
    return render_template("search_multiple_roles_results.html", results=results)


@queries_bp.route("/top_thriller_movies_boston", methods=["GET"])
def top_thriller_movies_boston():

    # >>>> TODO 10: Find the top 2 highest-rated thriller movies (genre: thriller) that were shot exclusively in Boston. <<<<
    #               “Exclusively” means that the movie may not have any other shooting location. 
    #               List the movie names and their rating.

    query = """ SELECT mp.name, mp.rating
FROM MotionPicture mp
JOIN Genre g ON mp.id = g.mpid
WHERE g.genre_name = 'Thriller'
AND mp.id NOT IN (SELECT mpid FROM Location WHERE city <> 'Boston')
ORDER BY mp.rating DESC
LIMIT 2; """

    with Database() as db:
        results = db.execute(query)
    return render_template("top_thriller_movies_boston.html", results=results)


@queries_bp.route("/search_movies_by_likes", methods=["POST"])
def search_movies_by_likes():
    min_likes = int(request.form["min_likes"])
    max_age = int(request.form["max_age"])

    # >>>> TODO 11: Find all the movies with more than “X” (parameterized) likes by users of age less than “Y” (parameterized). <<<<
    #               Return the movie names and the number of likes from that age group.

    query = """ SELECT mp.name, COUNT(*)
FROM MotionPicture as mp
JOIN Likes l on l.mpid = mp.id
JOIN User u on l.uemail = u.email
WHERE u.age < %s
GROUP BY mp.id
HAVING COUNT(*) > %s; """

    with Database() as db:
        results = db.execute(query, (max_age, min_likes))
    return render_template("search_movies_by_likes_results.html", results=results)


@queries_bp.route("/actors_marvel_warner", methods=["GET"])
def actors_marvel_warner():

    # >>>> TODO 12: Identify the actors who played a role in both “Marvel” and “Warner Bros” productions. <<<<
    #               List the actor names and the corresponding motion picture names.

    query = """ SELECT p.name, mp.name
FROM People as p
JOIN Role as r ON r.pid = p.id
Join MotionPicture mp on mp.id = r.mpid
WHERE p.id IN (SELECT p.id
FROM MotionPicture as mp
JOIN Role r on mp.id = r.mpid
Join People p on r.pid = p.id
WHERE r.role_name = "Actor"
AND mp.production = "Warner Bros"
INTERSECT
SELECT p.id
FROM MotionPicture as mp
JOIN Role r on mp.id = r.mpid
Join People p on r.pid = p.id
WHERE r.role_name = "Actor"
AND mp.production = "Marvel"); """

    with Database() as db:
        results = db.execute(query)
    return render_template("actors_marvel_warner.html", results=results)


@queries_bp.route("/movies_higher_than_comedy_avg", methods=["GET"])
def movies_higher_than_comedy_avg():

    # >>>> TODO 13: Find the motion pictures with a higher rating than the average rating of all comedy (genre) motion pictures.  <<<<
    #               List the names and ratings, sorted in descending order of ratings.

    query = """ SELECT mp.name, mp.rating
FROM MotionPicture mp
WHERE mp.rating > (SELECT AVG(rating) 
FROM MotionPicture as mp
JOIN Genre g on g.mpid = mp.id
WHERE g.genre_name = "Comedy")
ORDER BY mp.rating DESC; """

    with Database() as db:
        results = db.execute(query)
    return render_template("movies_higher_than_comedy_avg.html", results=results)


# @queries_bp.route("/top_5_movies_people_roles", methods=["GET"])
# def top_5_movies_people_roles():
#     """
#     Display the top 5 movies that involve the most people and roles.
#     """

#     # >>>> TODO 14: Find the top 5 movies with the highest number of people playing a role in that movie. <<<<
#     #               Show the `movie name`, `people count` and `role count` for the movies.

#     query = """ """

#     with Database() as db:
#         results = db.execute(query)
#     return render_template("top_5_movies_people_roles.html", results=results)


@queries_bp.route("/actors_with_common_birthday", methods=["GET"])
def actors_with_common_birthday():

    # >>>> TODO 14: Find actors who share the same birthday. <<<<
    #               List the actor names (actor 1, actor 2) and their common birthday.

    query = """ SELECT p1.name, p2.name, p1.dob
FROM People as p1
JOIN People as p2 ON p1.dob = p2.dob
WHERE p1.id < p2.id AND p1.name <> p2.name;"""

    with Database() as db:
        results = db.execute(query)
    return render_template("actors_with_common_birthday.html", results=results)


@queries_bp.route("/top_production_by_genre", methods=["GET"])
def top_production_by_genre():

    # >>>> TODO 15: List the productions that have produced more than two movies in a given genre, where each movie has a rating higher than the average rating of that genre. <<<<
    #               List the `production company name`, `genre name` and the `count of movies` that meet the criteria, ordered by the count of movies in descending order.

    query = """ SELECT DISTINCT mp.production
FROM MotionPicture as mp
JOIN Movie as m ON mp.id = m.mpid
JOIN Genre as g ON mp.id = g.mpid
GROUP BY g.genre_name, mp.production
HAVING COUNT(*) > 2
AND MIN(mp.rating) > (SELECT
AVG(mp.rating)
FROM MotionPicture as mp
JOIN Genre as g2 ON g2.mpid = mp.id
WHERE g2.genre_name = g.genre_name);
 """

    with Database() as db:
        results = db.execute(query)
    return render_template(
        "generic_results.html", results=results, title="Consistent Genre Leaders"
    )


@queries_bp.route("/versatile_talent", methods=["GET"])
def versatile_talent():

    # >>>> TODO 16: Find individuals who have acted, directed, and produced motion pictures, and have won at least one award against one of those roles. <<<<
    #               List the person’s `name` and `nationality`.

    query = """ SELECT p.name
FROM People as p
WHERE p.id IN (SELECT p.id FROM People as p JOIN Role r ON p.id = r.pid WHERE r.role_name = "Actor")
AND p.id IN (SELECT p.id FROM People as p JOIN Role r ON p.id = r.pid WHERE r.role_name = "Producer")
AND p.id IN (SELECT p.id FROM People as p JOIN Role r ON p.id = r.pid WHERE r.role_name = "Director")
AND p.id IN (SELECT p.id FROM Award); """

    with Database() as db:
        results = db.execute(query)
    return render_template(
        "generic_results.html",
        results=results,
        title="Versatile Talent (Triple Threats)",
    )


@queries_bp.route("/high_roi_movies", methods=["GET"])
def high_roi_movies():

    # >>>> TODO 17: Find the top 5 movies produced(shooted) in the USA with a “Return on Investment” (Box Office/Budget) higher than the average return on investment of all Marvel movies. <<<<
    #               Only include movies that have an ROI greater than the average ROI of all Marvel movies
    #               First column should be the movie name, second column should be country, and third column should be the ROI.

    query = """ SELECT mp.name, (m.boxoffice_collection / mp.budget) AS ROI
FROM MotionPicture as mp
JOIN Movie as m ON mp.id = m.mpid
WHERE mp.production = "USA"
AND (m.boxoffice_collection / mp.budget) > (SELECT AVG(m.boxoffice_collection / mp.budget)
FROM MotionPicture as mp
JOIN Movie as m ON mp.id = m.mpid
WHERE mp.production = "Marvel")
ORDER BY ROI DESC
LIMIT 5;
"""

    with Database() as db:
        results = db.execute(query)
    return render_template(
        "generic_results.html", results=results, title="Highest ROI (vs Marvel Average)"
    )


# @queries_bp.route("/super_fans", methods=["POST"])
# def super_fans():
#     """
#     Find users who have liked all movies from a specific production company.
#     """
#     # >>>> TODO 19: Find the users who have liked all the movies produced by a specific production company. <<<<
#     #               List the user `name` and `email`.

#     production = request.form["production"]
#     query = """ """

#     with Database() as db:
#         results = db.execute(query, (production,))
#     return render_template(
#         "generic_results.html", results=results, title=f"Super-fans of {production}"
#     )


@queries_bp.route("/awarded_series_growth", methods=["GET"])
def awarded_series_growth():

    # >>>> TODO 18: Find all TV series that have more seasons than the average season count of all series, and have at least one award-winning person after the year 2010. <<<<
    #               List the TV series `name`, `season count` and the `number of awards won`, ordered by season count in descending order.

    query = """ SELECT mp.name, s.season_count
FROM Series as s
JOIN MotionPicture as mp ON s.mpid = mp.id
WHERE s.season_count > (SELECT AVG(season_count) FROM Series)
AND s.mpid IN (SELECT r.mpid FROM Role as r JOIN Award as a ON r.pid = a.pid WHERE a.award_year > 2010); """

    with Database() as db:
        results = db.execute(query)
    return render_template(
        "generic_results.html",
        results=results,
        title="Award-Winning Long-Running Series",
    )

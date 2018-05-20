
import csv

from typing import List, Dict, Tuple, Set
from pprint import pprint

import pandas
import numpy
from sklearn.metrics.pairwise import cosine_similarity


class Movie:
    def __init__(self, MID, title, genres):
        super().__init__()
        self.id = MID
        self.title = title
        self.genres = genres
        self.genres_vector = None

    def setGenres(self, genres_str_to_int: Dict[str, int]):
        self.genres_vector = numpy.zeros(len(genres_str_to_int))
        for genre in self.genres:
            self.genres_vector[genres_str_to_int[genre]] = 1

        self.genres_vector = self.genres_vector.reshape(1, -1)

    def __repr__(self, *args, **kwargs):
        return "{} ({},{})".format(self.title, self.id, self.genres)



class User:
    def __init__(self, UID, genres_count):
        super().__init__()
        self.id = UID
        self.genre_ratings = numpy.zeros(genres_count, dtype=int)  # Ratings of genres by the user, normalized to (0,1)
        self.ratings: Dict[int, float] = {}  # Star-rating of given movies
        self.movies_rated = set()

    def __repr__(self, *args, **kwargs):
        return "User[{}]: {}".format(self.id, self.genre_ratings)

    def pGenreR(self, genreGetString, sort_by_name=False):
        print(f"User {self.id} genre ratings:")

        if not sort_by_name:
            genre_ratings: List[Tuple[str, float]] = [(genreGetString[i], self.genre_ratings[i]) for i in
                                                      range(0, self.genre_ratings.size)]

            genre_ratings = sorted(genre_ratings, key=lambda rating: rating[1], reverse=True)
            for genre_rating in genre_ratings:
                if genre_rating[1] > 0:
                    print("  {}: {}".format(genre_rating[0], genre_rating[1]))
        else:
            for i in range(0, self.genre_ratings.size):
                if self.genre_ratings[i] > 0:
                    print("  {}: {}".format(genreGetString[i], self.genre_ratings[i]))

class Recc:
    def __init__(self, movies_csv, ratings_csv):
        super().__init__()

        self.csvM = movies_csv
        self.csvR = ratings_csv

        self.movies = self.loadMovies()
        self.genresAll = ['Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary', 'Drama',
                            'Fantasy',
                            'Film-Noir', 'Horror', 'IMAX', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War',
                            'Western']

        self.genreGetID = {genre: i for i, genre in enumerate(self.genresAll)}
        self.genreGetString = {i: genre for i, genre in enumerate(self.genresAll)}
        for movie in self.movies.values():
            movie.setGenres(self.genreGetID)

        self.users: Dict[int, User] = self.loadUsers(self.csvR)

    def pUsrRatings(self, UID):
        self.users[UID].pGenreR(self.genreGetString)

    def pRecomended(self, recommended_movies):
        print("-----------  Recommended   --------------")
        for i, (MID, score) in enumerate(recommended_movies):
            print(f"{i:}. score: {score} , {self.movies[MID].title}")

    def getHybrid(self, UID, limit, content_based_weight, collab_based_weight, collab_use_top_n_similar_users):
        content_recommendations = self.getContentBased(UID, -1)
        collab_recommendations = self.getCollaborativeBased(UID, -1,
                                                            use_top_n_similar_users=collab_use_top_n_similar_users)

        final_recommendations: Dict[int, float] = {MID: (score * content_based_weight) for MID, score in
                                                   content_recommendations}

        for MID, score in collab_recommendations:
            if MID not in final_recommendations:
                final_recommendations[MID] = 0
            final_recommendations[MID] += score

        sorted_final = sorted(final_recommendations.items(), key=lambda item: item[1], reverse=True)
        if limit > 0:
            return sorted_final[:limit]
        else:
            return sorted_final

    def getContentBased(self, UID, limit):

        similarities: Dict[int, float] = {}
        non_rated_movies = [movie for movie in self.movies.values() if movie.id not in self.users[UID].movies_rated]
        for movie in non_rated_movies:
            similarity = cosine_similarity(self.users[UID].genre_ratings.reshape(1, -1), movie.genres_vector)[0][0]
            similarities[movie.id] = similarity

        sorted_similarities: List[Tuple[int, float]] = sorted(similarities.items(),
                                                              key=lambda item: item[1],
                                                              reverse=True)
        if limit > 0:
            return sorted_similarities[:limit]
        else:
            return sorted_similarities

    def getCollaborativeBased(self, UID, limit, use_top_n_similar_users):

        this_user = self.users[UID]

        similarities: Dict[int, float] = {}
        for user in self.users.values():
            if UID == user.id:
                continue  # skip this user

            similarity = \
                cosine_similarity(this_user.genre_ratings.reshape(1, -1), user.genre_ratings.reshape(1, -1))[0][0]
            similarities[user.id] = similarity

        sorted_similar_users: List[Tuple[int, float]] = sorted(similarities.items(),
                                                               key=lambda item: item[1],
                                                               reverse=True)[:use_top_n_similar_users]

        temp_ratings: Dict[int, List[float, int]] = {}
        for user, user_similarity in [(self.users[UID], _user_similarity)
                                      for UID, _user_similarity in
                                      sorted_similar_users]:
            for MID, movie_rating in user.ratings.items():
                if MID in this_user.movies_rated:
                    continue

                if MID not in temp_ratings:
                    temp_ratings[MID] = [0, 0]

                temp_ratings[MID][0] += movie_rating * user_similarity
                temp_ratings[MID][1] += 1

        new_ratings: Dict[int, float] = {MID: temp_rating[0] / temp_rating[1]
                                         for MID, temp_rating in temp_ratings.items()}
        sorted_new_ratings: Dict[int, float] = sorted(new_ratings.items(), key=lambda rating: rating[1], reverse=True)

        # Normalize
        max_val = sorted_new_ratings[0][1]
        normalized_sorted_new_ratings = [(rating[0], (rating[1] / max_val)) for rating in sorted_new_ratings]

        if limit > 0:
            return normalized_sorted_new_ratings[:limit]
        else:
            return normalized_sorted_new_ratings

    def loadMovies(self):

        movies = {}
        f = open(self.csvM, encoding="utf-8")
        f.readline()
        f.readline()
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            MID = int(row[0])
            genres = [genre.strip() for genre in row[2].split('|') if genre.strip() not in ['(no genres listed)']]
            movies[MID] = Movie(MID, row[1], genres)

        return movies

    def loadUsers(self, csvR):
        users: Dict[int, User] = {}

        with open(csvR, encoding="utf-8") as f:
            f.readline()
            f.readline()
            reader = csv.reader(f, delimiter=',', )
            for i, row in enumerate(reader):
                UID = int(row[0])
                MID = int(row[1])
                rating = float(row[2])
                if UID not in users:
                    users[UID] = User(UID, len(self.genreGetID))

                users[UID].movies_rated.add(MID)
                users[UID].ratings[MID] = rating
                for movie_genre in self.movies[MID].genres:
                    if rating >= 2.5:
                        users[UID].genre_ratings[self.genreGetID[movie_genre]] += 1

        for user in users.values():
            user.genre_ratings = user.genre_ratings / numpy.amax(user.genre_ratings)

        return users


Recc = Recc('./data/movies.csv', './data/ratings.csv')
UID = 19

Recc.pUsrRatings(UID)
Hybrid_recommended = Recc.getHybrid(UID, 50, 0.5, 20, 10)

Collaborative_recommended = Recc.getCollaborativeBased(UID, 50, 10)
Content_recommended = Recc.getContentBased(UID, 50)

Recc.pRecomended(Hybrid_recommended)
Recc.pRecomended(Collaborative_recommended)
Recc.pRecomended(Content_recommended)



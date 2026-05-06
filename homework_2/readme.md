# Homework 2 — BERT on AWS


A content-based movie recommender for MovieLens 1M, built on
[`bert-base-uncased`](https://huggingface.co/bert-base-uncased) embeddings.
The dataset, intermediate embeddings, and final recommendation outputs all
live on S3.

## Environment

- AWS credentials configured for an account with write access to the
  S3 bucket named at the top of the notebook (`barnett-evan-lab3`).
- A Python environment with `datarec-lib`, `boto3`, `pandas`, `numpy`,
  `torch`, and `transformers` installed (the first cell has the `pip`
  command, commented out).
- A network connection on first run (downloads MovieLens 1M from the
  GroupLens mirror via `datarec-lib` and pulls the BERT weights from
  the Hugging Face Hub).

## How to run

1. Open `eb_hw2.ipynb` in Jupyter on the EC2 instance.
2. Edit the `BUCKET` constant in the imports cell if you
   want to point at a different S3 bucket.
3. Run the cells from top to bottom. Each "run" cell either uploads
   fresh artifacts or prints `… already exists at s3://…` and exits
   early — re-running the notebook is cheap.

## Sequence of functions

The notebook is organized so each step is a function and the "run"
cells call them in order. The end-to-end pipeline is:

1. **`upload_movielens_1m_to_s3()`** — downloads MovieLens 1M with
   `datarec-lib` and uploads `movies.dat`, `ratings.dat`, `users.dat`
   to `s3://<bucket>/datasets/movielens-1m/`. Skips the download if
   all three files are already in S3.
2. **`create_movie_pool_bert_embeddings(max_year=1980)`** — reads the
   MovieLens movie list from S3, filters to movies released in or
   before 1980, builds a short `Title / Year / Genres` text per movie,
   runs `bert-base-uncased` over those texts (mean-pooled over
   non-padding tokens), and uploads `embeddings.npy`, `movie_ids.npy`,
   `filtered_movies.csv`, `embedding_config.json` to
   `s3://<bucket>/intermediate/movielens-1m-bert-pre1980/`. Skips work
   if `embeddings.npy` already exists.
3. **`create_recommendation_outputs()`** — for both the pre-1980 pool
   and the full pool (calling `create_movie_pool_bert_embeddings` again
   with `max_year=None`), generates 5 recommendations for a cold user
   and for a randomly chosen top-5%-by-interaction user (resampled
   until they have a ≥4-star rating in the candidate pool), then saves
   the combined output to
   `s3://<bucket>/outputs/movielens-1m-recommendations/recommendations.{json,csv}`.
4. **`create_personal_profile_recommendations()`** — matches the
   hand-rated 10-movie list (`MY_MOVIE_RATINGS`) to MovieLens, averages
   the embeddings of my liked (≥4-star) movies into a profile vector,
   recommends the 5 unrated movies with the highest cosine similarity,
   and saves both the profile and the recommendations to
   `s3://<bucket>/outputs/movielens-1m-personal-profile/`.

### Recommendation strategies

- **Cold user (popularity):** keep movies with at least 50 ratings,
  rank by mean rating, take the top 5.
- **Top user / personal profile (content-based):** average the BERT
  embeddings of the user's liked (≥4-star) movies into a single
  profile vector, score every candidate movie by cosine similarity to
  that vector, drop anything the user has already rated, take the top
  5.

### Supporting helpers

- `s3_key_exists`, `list_s3_keys`, `find_s3_key_by_filename`,
  `s3_get_bytes` — thin wrappers around `boto3` used everywhere else.
- `load_movielens_from_s3` — reads the three `.dat` files back into
  pandas DataFrames and parses `timestamp` into `interaction_time`.
- `load_embedding_artifacts` — loads a previously-saved embedding pool
  (`embeddings`, `movie_ids`, `filtered_movies`) from S3.
- `cosine_similarity_to_profile` — vectorized cosine similarity between
  a single profile vector and every row of an embedding matrix.
- `recommend_popular_movies` — popularity ranking used for the cold
  user case.
- `recommend_by_profile` — mean-of-liked-embeddings + cosine
  similarity, shared by the top-user and personal-profile cases.
- `pick_top_user_with_liked_in_pool` — samples a user from the top 5%
  by interaction count, retrying until they have at least one ≥4-star
  rating inside the current candidate pool.
- `summarize_user` — demographics, total interactions, average rating,
  and (optionally) overlap with the candidate pool.
- `match_profile_ratings_to_movielens` — fuzzy title matching for the
  personal profile.
- `movies_to_records` — convert a recommendation DataFrame slice to
  a JSON-friendly list of dicts.

## Expected S3 outputs

After a clean run the bucket contains:

```
s3://<bucket>/datasets/movielens-1m/
    movies.dat
    ratings.dat
    users.dat

s3://<bucket>/intermediate/movielens-1m-bert-pre1980/
    embeddings.npy             # (num_movies, 768) float32
    movie_ids.npy              # int64 movie IDs aligned with embeddings
    filtered_movies.csv        # the MovieLens rows used as input
    embedding_config.json      # model name, filter, pooling, shape

s3://<bucket>/intermediate/movielens-1m-bert-full/
    embeddings.npy
    movie_ids.npy
    filtered_movies.csv
    embedding_config.json

s3://<bucket>/outputs/movielens-1m-recommendations/
    recommendations.json       # cold + top user, both scopes
    recommendations.csv

s3://<bucket>/outputs/movielens-1m-personal-profile/
    user_profile.json          # the 10 hand-rated movies + summary
    user_profile.csv
    personal_recommendations.json   # 5 recs from the full pool
    personal_recommendations.csv
```

The notebook also prints these `s3://` paths as it runs and renders the
final recommendation lists inline as Python objects.

## Output schema

`recommendations.json` is a list with four entries (cold + top user, for
each of the two scopes). Each entry contains:

- `Dataset_Scope` — `"Pre-1980 movies"` or `"Full MovieLens 1M movies"`
- `User_Type` — `"Cold user"` or `"Top user"`
- `Last_Interaction_Time` — ISO-8601 timestamp (or `null` for the cold
  user)
- `User_Summary` — demographic + rating-history fields from
  `summarize_user`
- `Recommended_Movies` — list of 5 `{movie_id, title, year, genres,
  score}` dicts

`personal_recommendations.json` follows the same schema with
`User_Type = "Personal profile"`. `user_profile.json` mirrors the
shape but lists `Rated_Movies` instead of `Recommended_Movies`.


## AI Usage
Tools used:
- ChatGPT 5.5
- Claude Sonnent 4.6 VSCode extension

Usage:
- Used to help created S3 Helpers section as I was getting S3 errors that I didn't know how to handle:
  - `s3_key_exists`, `list_s3_keys`, `find_s3_key_by_filename`, `s3_get_bytes`
- Used to make JSON and CSV format more consistent for save files
- Used to add `FORCE_OVERWRITE` functionality so you can see cell output for homework submission
- Used to ensure all path directories are correct and consistent
- Used to help create Readme file

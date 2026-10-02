import pandas as pd

posts = pd.read_csv("data/posts.csv")
creators = pd.read_csv("data/creators.csv")

print("DATA LOADED SUCCESSFULLY")
print("Posts:", len(posts))
print("Creators:", len(creators))
def predict_views(creator_id):

    creator = creators[creators["creator_id"] == creator_id]

    if creator.empty:
        return 0

    creator_posts = posts[posts["creator_id"] == creator_id]

    if len(creator_posts) >= 3:
        return int(creator_posts["views_final"].mean())

    return int(creator.iloc[0]["historical_avg_views_per_post"])

print("Predicted Views:", predict_views("CR0001"))
def historical_average(creator_id):

    creator_posts = posts[posts["creator_id"] == creator_id]
    print("Historical Posts:", len(creator_posts))

    if creator_posts.empty:
        return 0

    return int(creator_posts["views_final"].mean())


print("Actual Average Views:", historical_average("CR0001"))
creator_counts = posts["creator_id"].value_counts()

eligible = creator_counts[creator_counts >= 3]

print("\nCREATORS WITH 3+ POSTS:")
print(eligible.head())
print("\nPREDICTION TEST")

print("Available Creator IDs:")
print(eligible.index.tolist())

test_creator = eligible.index[0]

print("\nTesting Creator:", test_creator)

print("Predicted Views:", predict_views(test_creator))

print("Actual Average Views:", historical_average(test_creator))
evaluation = []

for creator_id in creators["creator_id"]:

    creator_posts = posts[posts["creator_id"] == creator_id]

    if creator_posts.empty:
        continue

    predicted = predict_views(creator_id)

    actual = int(creator_posts["views_final"].mean())

    evaluation.append({
        "creator_id": creator_id,
        "predicted_views": predicted,
        "actual_views": actual,
        "error": abs(predicted - actual)
    })

evaluation_df = pd.DataFrame(evaluation)

print("\nPREDICTION EVALUATION")
print(evaluation_df.head(10))

print("\nCreators Evaluated:", len(evaluation_df))

print("Mean Absolute Error:",
      round(evaluation_df["error"].mean(), 2))
global_average = posts["views_final"].mean()

evaluation_df["baseline_error"] = abs(
    evaluation_df["actual_views"] - global_average
)

baseline_mae = evaluation_df["baseline_error"].mean()

print("\nBASELINE COMPARISON")

print("Creator Prediction MAE:",
      round(evaluation_df["error"].mean(), 2))

print("Global Average MAE:",
      round(baseline_mae, 2))
print("\nDATA STRUCTURE")

print("\nPOST COLUMNS:")
print(posts.columns.tolist())

print("\nCREATOR COLUMNS:")
print(creators.columns.tolist())

print("\nCONTENT FORMATS:")
print(posts["format"].value_counts())

print("\nPLATFORMS:")
print(posts["platform"].value_counts())

print("\nCREATOR TIERS:")
print(creators["tier"].value_counts())
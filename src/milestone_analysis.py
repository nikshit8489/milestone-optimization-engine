import pandas as pd

posts = pd.read_csv("data/posts.csv")
thresholds = [10000, 50000, 100000, 500000]

for t in thresholds:
    achieved = (posts["views_final"] >= t).sum()
    rate = achieved / len(posts) * 100

    print(f"Milestone {t}: {achieved} posts ({rate:.2f}%)")
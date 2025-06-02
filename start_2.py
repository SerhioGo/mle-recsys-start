from Recommendations import Recommendations

rec_store = Recommendations()

rec_store.load(
    "personal",
    '/home/mle-user/mle_projects/mle-recsys-start/final_recommendations_feat.parquet',
    columns=["user_id", "item_id", "rank"],
)
rec_store.load(
    "default",
    '/home/mle-user/mle_projects/mle-recsys-start/top_recs.parquet',
    columns=["item_id", "rank"],
)

aaa = rec_store.get(user_id=1049126, k=5)
print(aaa)


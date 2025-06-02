import logging

from fastapi import FastAPI
from contextlib import asynccontextmanager
import pandas as pd
import requests

recom_store_url = "http://127.0.0.1:8000"
features_store_url = "http://127.0.0.1:8010"
events_store_url = "http://127.0.0.1:8020"

class Recommendations:
    def __init__(self):

        self._recs = {"personal": None, "default": None}
        self._stats = {
            "request_personal_count": 0,
            "request_default_count": 0,
        }

    def load(self, type, path, **kwargs):
        """
        Загружает рекомендации из файла
        """

        logger.info(f"Loading recommendations, type: {type}")
        self._recs[type] = pd.read_parquet(path, **kwargs)
        if type == "personal":
            self._recs[type] = self._recs[type].set_index("user_id")
        logger.info(f"Loaded")

    def get(self, user_id: int, k: int=100):
        """
        Возвращает список рекомендаций для пользователя
        """
        try:
            recs = self._recs["personal"].loc[user_id] 
            recs = recs["item_id"].to_list()[:k]
            self._stats["request_personal_count"] += 1
        except KeyError:
            recs = self._recs["default"]
            recs = recs["item_id"].to_list()[:k]
            self._stats["request_default_count"] += 1
        except:
             logger.error("No recommendations found")
             recs = []

        return recs

    def stats(self):

        logger.info("Stats for recommendations")
        for name, value in self._stats.items():
            logger.info(f"{name:<30} {value} ")

logger = logging.getLogger("uvicorn.error")

## Поднимаем класс
rec_store = Recommendations()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
    # код ниже (до yield) выполнится только один раз при запуске сервиса
        logger.info("Starting")
        rec_store.load(
                "personal",
                "/home/mle-user/mle_projects/mle-recsys-start/final_recommendations_feat.parquet",
                columns=["user_id", "item_id", "rank"]
                )
        rec_store.load(
                "default",
                "/home/mle-user/mle_projects/mle-recsys-start/top_recs.parquet",
                columns=["item_id", "rank"]
                )
        yield
    finally:
    # этот код выполнится только один раз при остановке сервиса
        rec_store.stats()
        logger.info("Stopping")
    
# создаём приложение FastAPI
app = FastAPI(title="recommendations", lifespan=lifespan)

@app.post("/recommendations_offline")
async def recommendations_offline(user_id: int, k: int = 100):
    """
    Возвращает список офлайн-рекомендаций длиной k для пользователя user_id
    """

    recs = rec_store.get(user_id, k)

    return {"recs": recs} 

def dedup_ids(ids):
    """
    Дедублицирует список идентификаторов, оставляя только первое вхождение
    """
    seen = set()
    ids = [id for id in ids if not (id in seen or seen.add(id))]
    return ids

@app.post("/recommendations_online")
async def recommendations_online(user_id: int, k: int = 100):
    """
    Возвращает список онлайн-рекомендаций длиной k для пользователя user_id
    """
    
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    
    # получаем список последних событий пользователя, возьмём три последних
    params = {"user_id": user_id, "k": 3}
    try:
        resp = requests.post(events_store_url + "/get", headers=headers, params=params)
        resp.raise_for_status()
        events_data = resp.json()
        events = events_data.get("events", [])
    except requests.RequestException as e:
        return {"error": "Не удалось получить последние события"}
    
    # получаем список айтемов, похожих на последние три, с которыми взаимодействовал пользователь
    items = []
    scores = []
    for item_id in events:
        try:
            # получаем список похожих объектов
            resp = requests.post(f"{features_store_url}/similar_items", params={'item_id': item_id, 'k': k})
            resp.raise_for_status()
            item_similar_items = resp.json()
        
        # добавляем найденные похожие объекты
            items += item_similar_items.get("item_id_2", [])
            scores += item_similar_items.get("score", [])
        except requests.RequestException as e:
            return {"error": f"Не удалось получить похожие объекты для item_id {item_id}"}
    
    # сортируем похожие объекты по scores в убывающем порядке
    combined = list(zip(items, scores))
    combined = sorted(combined, key=lambda x: x[1], reverse=True)
    combined = [item for item, _ in combined]
    
    # удаляем дубликаты, чтобы не выдавать одинаковые рекомендации
    recs = dedup_ids(combined)
    
    # берем только первые k рекомендаций
    recs = recs[:k]
    
    return {"recs": recs}

@app.post("/recommendations")
async def recommendations(user_id: int, k: int = 100):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """

    recs_offline = await recommendations_offline(user_id, k)
    recs_online = await recommendations_online(user_id, k)

    recs_offline = recs_offline["recs"]
    recs_online = recs_online["recs"]

    recs_blended = []

    min_length = min(len(recs_offline), len(recs_online))
    # чередуем элементы из списков, пока позволяет минимальная длина
    for i in range(min_length):
        recs_blended.append(recs_online[i])
        recs_blended.append(recs_offline[i])

    # добавляем оставшиеся элементы в конец
    recs_blended.extend(recs_offline[min_length:])
    recs_blended.extend(recs_online[min_length:])

    # удаляем дубликаты
    recs_blended = dedup_ids(recs_blended)
    
    # оставляем только первые k рекомендаций
    recs_blended = recs_blended[:k]

    return {"recs": recs_blended}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        workers=1
    )
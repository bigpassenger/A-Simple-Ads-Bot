import pymongo


class AdsMongoClient:
    def __init__(
        self,
        host: str,
        port: int,
        db_name: str = "telegram_bot",
        ads_collection_name: str = "ads",
        categories_collection_name: str = "categories",
    ):
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client.get_database(db_name)
        self.ads_collection = self.db.get_collection(ads_collection_name)
        self.categories_collection = self.db.get_collection(categories_collection_name)

    def add_category(self, category: str):
        # write your code here
        obj = {
            "category"  :category
        } 
        self.categories_collection.insert_one(obj)

    def get_categories(self) -> list:
        # write your code here
        results = self.categories_collection.find()
        return list(set([result["category"] for result in results]))

    def add_advertising(
        self, user_id: int, photo_url: str, category: str, description: str
    ):
        # write your code here
        ad = {
            "user_id": user_id,
            "description": description,
            "category": category,
            "photo_url": photo_url,
        }
        self.ads_collection.insert_one(ad)

    def delete_advertising(self, user_id: int, doc_id: str):
        # write your code here
        ad = {
            "_id":doc_id,
            "user_id": user_id,
        }
        self.ads_collection.delete_one(ad)
    def get_ads_by_user_id(self, user_id: int):
        # write your code here
        
        results = self.ads_collection.find({"user_id":user_id})
        empty_list = []

        for result in results:
            ad = {
            "id": str(result["_id"]),
            "photo_url": result["photo_url"],
            "category": result["category"],
            "description": result["description"],
            }
            empty_list.append(ad)
        return empty_list

    def get_ads_by_category(self, category: str):
        # write your code here
        results = self.ads_collection.find({"category":category})
        empty_list = []

        for result in results:
            ad = {
                "id": str(result["_id"]),
                "photo_url": result["photo_url"],
                "category": result["category"],
                "description": result["description"],
            }
            empty_list.append(ad)

        return empty_list


if __name__ == "__main__":
    ads_mongo_client = AdsMongoClient("localhost", 27017)
    ads_mongo_client.add_category("کالای دیجیتال")
    ads_mongo_client.add_category("خودرو")
    ads_mongo_client.add_category("موبایل")
    ads_mongo_client.add_advertising(123, "url1", "کالای دیجیتال", "لپ تاپ")
    ads_mongo_client.add_advertising(123, "url2", "خودرو", "پراید")
    ads_mongo_client.add_advertising(123, "url3", "موبایل", "آیفون")
    ads_mongo_client.add_advertising(321, "url4", "کالای دیجیتال", "موس")
    ads_mongo_client.add_advertising(321, "url5", "خودرو", "پژو")
    ads_mongo_client.add_advertising(321, "url6", "موبایل", "سامسونگ")

    print("Categories")
    print(ads_mongo_client.get_categories())

    print("User 123 ads")
    print(ads_mongo_client.get_ads_by_user_id(123))

    print("Ads of category کالای دیجیتال")
    print(ads_mongo_client.get_ads_by_category("کالای دیجیتال"))

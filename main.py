import sqlite3

import requests


class VK:
    def __init__(self, user) -> None:
        self.token = "TOKEN"
        self.version = "5.131"
        self.session = requests.Session()
        self.main_user_id = self.get_main_user_id(user)
        self.creating_database()

        self.accounts = 0

    def creating_database(self) -> None:
        with sqlite3.connect(f"database.db") as db:
            db.execute(f"""CREATE TABLE IF NOT EXISTS db_{self.main_user_id}(
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        user_id BIGINT NOT NULL,
                        first_name TEXT,
                        last_name TEXT,
                        sex TEXT,
                        birthday TEXT,
                        country TEXT,
                        city TEXT,
                        mobile_phone TEXT,
                        home_phone TEXT, 
                        crop_photo TEXT,
                        university_name TEXT)""")
            db.commit()

    def get_main_user_id(self, user) -> str:
        if "vk.com" in user:
            username = user.split("/")[-1]
            if username.isnumeric():
                return username
            else:
                response = self.session.post("https://api.vk.com/method/users.get", data={
                    "access_token": self.token,
                    "user_id": username,
                    "fields": "id",
                    "v": self.version
                }).json()
                return response["response"][0]["id"]

    def save_info(self, friend, db):
        user_id = friend["id"]
        if friend.get("first_name") is not None and friend.get("first_name") != "":
            first_name = friend["first_name"]
        else:
            first_name = None

        if friend.get("last_name") is not None and friend.get("last_name") != "":
            last_name = friend["last_name"]
        else:
            last_name = None

        if friend.get("sex") == 1 and friend.get("sex") != "":
            sex = "Woman"
        elif friend.get("sex") == 2 and friend.get("sex") != "":
            sex = "Men"
        else:
            sex = None

        if friend.get("bdate") and friend.get("bdate") != "":
            birthday = friend["bdate"]
        else:
            birthday = None

        if friend.get("country"):
            country = friend["country"]["title"]
        else:
            country = None

        if friend.get("city"):
            city = friend["city"]["title"]
        else:
            city = None

        if friend.get("mobile_phone") is not None and friend.get("mobile_phone") != "" and friend.get(
                "mobile_phone").replace("+", "").isnumeric():
            mobile_phone = friend["mobile_phone"]
        else:
            mobile_phone = None

        if friend.get("home_phone") is not None and friend.get("home_phone") != "" and friend.get("home_phone").replace(
                "+", "").isnumeric():
            home_phone = friend["home_phone"]
        else:
            home_phone = None

        if friend.get("crop_photo") is not None:
            if friend["crop_photo"]["photo"].get("sizes"):
                crop_photo = friend["crop_photo"]["photo"]["sizes"][-1]["url"]
            else:
                crop_photo = friend["crop_photo"]["photo"]["album_id"][-1]["url"]
        else:
            crop_photo = None

        if friend.get("university_name") is not None and friend.get("university_name") != "":
            university_name = friend.get("university_name")
        else:
            university_name = None

        db.execute(f"""INSERT INTO db_{self.main_user_id}
                   (user_id, first_name, last_name, sex, birthday, country, city, 
                   mobile_phone, home_phone, crop_photo, university_name) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                   (user_id, first_name, last_name, sex, birthday, country, city,
                    mobile_phone, home_phone, crop_photo, university_name))

    def get_friends_info(self) -> None:
        response = self.session.post("https://api.vk.com/method/friends.get", data={
            "user_id": self.main_user_id,
            "access_token": self.token,
            "fields": "id, bdate, city, country, contacts, crop_photo, education, sex",
            "v": self.version
        }).json()
        count_friends = response["response"]["count"]
        friends_0_5000 = response["response"]["items"]
        with sqlite3.connect(f"database.db") as db:
            for friend_0_5000 in friends_0_5000:
                self.save_info(friend_0_5000, db)
                self.accounts += 1
                print(self.accounts)

            if count_friends == 5000:
                response = self.session.post("https://api.vk.com/method/friends.get", data={
                    "access_token": self.token,
                    "user_id": self.main_user_id,
                    "count": 10000,
                    "v": self.version
                }).json()
                friends_5000_10000 = response["response"]["items"][5000:10000]
                for friend_5000_10000 in friends_5000_10000:
                    response = self.session.post("https://api.vk.com/method/users.get", data={
                        "access_token": self.token,
                        "user_ids": friend_5000_10000,
                        "fields": "id, bdate, city, country, contacts, crop_photo, education, sex",
                        "v": self.version
                    }).json()
                    self.save_info(response["response"][0], db)
                    self.accounts += 1
                    print(self.accounts)
            db.commit()


if __name__ == "__main__":
    while True:
        url = input("Enter the link: ")
        vk = VK(url)

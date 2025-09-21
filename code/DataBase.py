import json, os, redis
import numpy as np
from Debug import print_debug

class DataBase:
    def __init__(self, _debug: bool = True):
        """
        
        Запуск класса, инициализация redis, загрузка конфига, конвертация данных в redis.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        """
        if _debug:
            print_debug("DataBase", "[main]Initialized.[/main]")

        self.load_redis_config()
        try:
            self.redis = redis.Redis(
                    host = self.redis_host, 
                    port = self.redis_port, 
                    db = 0, 
                    decode_responses = True
                )
        
        except Exception as e:
            if _debug:
                print_debug("DataBase", "[red]Redis[/red] not connected.")
                print_debug("DataBase", "[red]Error: " + str(e) + "[/red]")
        
            return
        
        del self.redis_host, self.redis_port

        if not self.redis.exists("redis_write_all_configs"):
            if _debug:
                print_debug("DataBase", "[main]Redis connected.[/main]")
        
            self.converter_data_in_redis()
        
        else:
            if _debug:
                print_debug("DataBase", "[main]Redis reconnected.[/main]")
    
    def load_redis_config(self, _debug: bool = True) -> None:
        """
        
        Загрузка конфига(host, port) redis.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        """
        if _debug:
            print_debug("DataBase", "Load [main]redis[/main] config...")
        main_config = json.loads(open(os.path.join(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0], "data/Config.json"), "r", encoding="utf-8").read())
        self.redis_host = main_config["redis_config"]["host"]
        self.redis_port = main_config["redis_config"]["port"]
        del main_config

    def pre_loads(self, _debug: bool = True) -> None:
        """
        
        Загрузка данных из файлов в переменные.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        """
        path_project = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
        if _debug:
            print_debug("DataBase", "[main]Load data...[/main]")
            print_debug("DataBase", "Path project: [main]" + path_project + ".[/main]")
        
        self.main_config = json.loads(open(os.path.join(path_project, "data/Config.json"), "r", encoding = "utf-8").read())
        self.schedule = json.loads(open(os.path.join(path_project, "data/Schedule.json"), "r", encoding = "utf-8").read())
        self.lessons = json.loads(open(os.path.join(path_project, "data/lessons.json"), "r", encoding = "utf-8").read())
        self.ping = json.loads(open(os.path.join(path_project, "data/Ping.json"), "r", encoding = "utf-8").read())
        self.url = json.loads(open(os.path.join(path_project, "data/Url.json"), "r", encoding = "utf-8").read())

        del path_project
        if _debug:
            print_debug("DataBase", "[main]Data loaded.[/main]")

    def converter_data_in_redis(self, _debug: bool = True) -> None:
        """
        
        Конвертация данных в redis. А после удаление переменных.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        """
        self.pre_loads(_debug = _debug)

        #---------SCHEDULE---------
        if _debug:
            print_debug("DataBase", "[main]Converter data in redis.[/main]")
     
        for day in self.schedule:
            if day == "times": continue    
            for number_lesson, lessons in self.schedule[day].items():
                lessons_data = []
                for i in lessons:
                    if type(i) == int:
                        lessons_data.append(lessons[i])

                    elif type(i) == str:
                        lessons_data.append(i)

                    elif type(i) == None:
                        lessons_data.append("None")

                if lessons_data:
                    self.redis.rpush(f"schedule_{day}_{number_lesson}", *lessons_data)
                    if _debug:
                        print_debug("DataBase", f"redis add schedule: [main]{day}[/main], number_lesson: [main]{number_lesson}[/main], lessons: [main]{lessons_data}[/main].")

        for number_lessons, value in self.schedule["times"].items():
            self.redis.hset("times_lessons", number_lessons, json.dumps(value))

        if _debug:
            print_debug("DataBase", "Converter [main]schedule[/main] in redis [main]complete.[/main]")
        
        #---------LESSONS---------
        for id, lessons in self.lessons.items():
            self.redis.set(f"lessons_{id}", lessons)
            self.redis.set(f"lessons_{lessons}", id)
            if _debug:
                print_debug("DataBase", f"redis add lesson: [main]{lessons}[/main], id: [main]{id}[/main].")

        if _debug:
            print_debug("DataBase", "Converter [main]lessons[/main] in redis [main]complete.[/main]")
        
        #---------PING---------
        pings_username_data = [i for i in self.ping]
        
        self.redis.rpush("pings_username", *pings_username_data)
        if _debug:
            print_debug("DataBase", f"redis add [main]pings_username[/main]: [main]{pings_username_data}[/main].")
        
        if _debug:
            print_debug("DataBase", "Converter [main]pings_username[/main] in redis [main]complete.[/main]")

        for username, user_id in self.ping.items():
            self.redis.set(f"pings_{username}", user_id)

        if _debug:
            print_debug("DataBase", "Converter [main]pings[/main] in redis [main]complete.[/main]")

        #---------URL---------
        for id, url in self.url.items():
            self.redis.set(f"url_{id}", url)
            if _debug:
                print_debug("DataBase", f"redis add url: [main]{url}[/main], id: [main]{id}[/main].")

        if _debug:
            print_debug("DataBase", "Converter [main]url[/main] in redis [main]complete.[/main]")

        #---------CONFIG---------
        self.redis.set("config_token", self.main_config["token"])
        self.redis.set("config_chat_log_id", self.main_config["chat_log_id"])
        self.redis.set("config_chats_id", "|".join(self.main_config["chats_id"]))
        self.redis.set("config_number_of_weeks_types", np.uint8(self.main_config["number_of_weeks_types"]).tobytes())
        self.redis.hset("config_data_week_type", mapping = self.main_config["data_week_type"])
        self.redis.set("time_zone", self.main_config["time_zone"])

        max_days = int([i for i in self.schedule["times"]][-1])
        self.redis.set("config_max_lesson_in_days", np.uint8(max_days).tobytes())
        if _debug:
            print_debug("DataBase", "Converter [main]config[/main] in redis [main]complete.[/main]")

        del self.main_config, self.schedule, self.lessons, self.ping, self.url
        if _debug:
            print_debug("DataBase", "Converter [main]all[/main] in redis [main]complete.[/main]")

        self.redis.set("redis_write_all_configs", "True")
    def reload_redis(self, _debug: bool = True) -> None:
        """
        
        Перезагрузка redis.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        """
        if _debug:
            print_debug("DataBase", "[main]Reload[/main] redis.")

        self.pre_loads()
        self.redis.flushall()
        self.converter_data_in_redis()
        if _debug:
            print_debug("DataBase", "[main]Redis[/main] reloaded.")

    def get_max_lesson_in_days(self, _debug: bool = True) -> np.uint8:
        """
        
        Получение максимального количества уроков в день.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            np.uint8: Максимальное количество уроков в день.
        """
        max_days =  np.frombuffer(self.redis.get("config_max_lesson_in_days").encode("utf-8"), dtype = np.uint8)[0]

        if _debug:
            print_debug("DataBase", f"Get [main]max lesson in days[/main]: [main]{max_days}[/main].")

        return max_days

    def get_lesson_for_id(self, id: str = None, _debug: bool = True) -> str:
        """
        
        Получение урока по id.

        Args:
            id (str): Id урока.
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            str: Урок.
        """

        if id is None: return
        
        lesson = self.redis.get(f"lessons_{id}")

        if _debug:
            print_debug("DataBase", f"Get lesson for id: [main]{id}[/main], lesson: [main]{lesson}[/main].")

        return lesson

    def get_url_for_id(self, id: str = None, _debug: bool = True) -> str:
        """
        
        Получение url по id.

        Args:
            id (str): Id урока.
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            str: url урока.
        """

        if id is None: return

        url = self.redis.get(f"url_{id}")

        if _debug:
            print_debug("DataBase", f"Get url for id: [main]{id}[/main], url: [main]{url}[/main].")

        return url

    def get_id_lesson_for_date(self, 
                               day: int = None, 
                               number_lesson: int = None, 
                               _debug: bool = True
                               ) -> list[str]:
        
        """
        
        Получение id урока по дате.

        Args:
            day (int): День недели.
            number_lesson (int): Номер урока.
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            list[str]: Список id уроков.
        """

        if day is None or number_lesson is None: return

        lessons = self.redis.lrange(f"schedule_{day}_{number_lesson}", 0, -1)
        
        if _debug:
            print_debug("DataBase", f"Get id lesson for date: day: [main]{day}[/main], number lesson: [main]{number_lesson}[/main], lessons: [main]{lessons}[/main].")

        return lessons

    def get_lesson_for_date(self, day: int = None, 
                            number_lesson: int = None, 
                            _id_lessons = None, 
                            _debug: bool = True
                            ) -> list[str]:
        
        """
        
        Получение урока по дате.

        Args:
            day (int): День недели.
            number_lesson (int): Номер урока.
            _id_lessons (list[str]): Id уроков.
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            list[str]: Список id уроков.
            list[str]: Список уроков.
        """
        if day is None or number_lesson is None or self.get_max_lesson_in_days(_debug = False) < number_lesson: return None, None

        id_lessons = self.get_id_lesson_for_date(day, number_lesson, _debug = False) if _id_lessons is None else _id_lessons
        lessons = [self.get_lesson_for_id(id, _debug = False) for id in id_lessons]

        if _debug:
            print_debug("DataBase", f"Get lesson for date: day: [main]{day}[/main], number lesson: [main]{number_lesson}[/main], lessons: [main]{lessons}[/main].")

        return id_lessons, lessons
    
    def get_all_usernames(self, _debug: bool = True) -> list[str]:
        if _debug:
            print_debug("DataBase", "Get [main]all usernames[/main].")

        return self.redis.lrange("pings_username", 0, -1)
    
    def get_user_id_for_username(self, username: str = None, _debug: bool = True) -> str:
        """
        
        Получение id пользователя по username.

        Args:
            username (str): Username пользователя.
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            str: user_id пользователя
        """

        if username is None: return
        if _debug:
            print_debug("DataBase", f"Get user id for username: [main]{username}[/main]")

        return self.redis.get(f"pings_{username}")

    def get_chats_id(self, _debug: bool = True) -> list[str]:
        """
        
        Получение id чатов для разсылки.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            list[str]: Список id чатов.
        """

        chats = self.redis.get("config_chats_id").split("|")

        if _debug:
            print_debug("DataBase", "Get [main]chats id[/main]: [main]" + ", ".join(chats) + "[/main].")

        return chats
    
    def get_chat_log_id(self, _debug: bool = True) -> str:
        """
        
        Получение id чата для логирования.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            int: id чата.
        """

        chat_log = str(self.redis.get("config_chat_log_id"))

        if _debug:
            print_debug("DataBase", "Get [main]chat log id[/main]: [main]" + chat_log + "[/main].")

        return chat_log
    
    def get_token(self, _debug: bool = True) -> str:
        """
        
        Получение токена телеграм бота.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            str: Токен.
        """

        if _debug:
            print_debug("DataBase", "Get [main]token[/main].")

        return str(self.redis.get("config_token"))
    
    def get_number_of_weeks_types(self, _debug: bool = True) -> np.uint8:
        """
        
        Получение количества типов недели.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            np.uint8: Количество типов недели.
        """

        number_of_weeks_types = np.frombuffer(self.redis.get("config_number_of_weeks_types").encode("utf-8"), dtype = np.uint8)[0]

        if _debug:
            print_debug("DataBase", "Get [main]number of weeks types[/main], number of weeks types: [main]" + str(number_of_weeks_types) + "[/main].")

        return number_of_weeks_types

    def get_data_week_type(self, _debug: bool = True) -> dict:
        """
        
        Получение данных о типе недели от которой будем считать.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            dict: Данные о типе недели.
        """
        if _debug:
            print_debug("DataBase", "Get [main]data week type[/main].")

        data = self.redis.hgetall("config_data_week_type")
        result = {
            "type": np.int16(int(data["type"])),
            "day": np.uint8(int(data["day"])),
            "month": np.uint8(int(data["month"])),
            "year": np.uint16(int(data["year"]))
        }

        return result

    def add_user_in_pings(self, 
                          username: str = None, 
                          user_id: str = None, 
                          _debug: bool = True
                          ) -> bool:

        """
        
        Добавление/удаление пользователя в спосок пингов.

        Args:
            username (str): Username пользователя.
            user_id (str): Id пользователя.
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            bool: True - если пользователь добавлен, False - если пользователь удален.
        """

        if username is None or user_id is None: return
        if _debug:
            print_debug("DataBase", f"Add user in pings: username: [main]{username}[/main], user id: [main]{user_id}[/main]")
        path_project = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
        ping = json.loads(open(os.path.join(path_project, "data/Ping.json"), "r", encoding = "utf-8").read())

        for username_value, id_value in ping.items():
            if id_value == user_id:
                ping.remove(username_value)
                return False
            
        if ping.get(username):
            ping.remove(username)
            open(os.path.join(path_project, "data/Ping.json"), "w", encoding = "utf-8").write(json.dumps(ping))
            return False
        
        ping[username] = user_id
        open(os.path.join(path_project, "data/Ping.json"), "w", encoding = "utf-8").write(json.dumps(ping))

        self.redis.rpush("pings_username", username)
        self.redis.set(f"pings_{username}", user_id)
        return True
    
    def get_times(self, _debug: bool = True) -> dict:
        """
        
        Получение данных о времени.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            dict: Данные о времени.
        """
        if _debug:
            print_debug("DataBase", "Get [main]times[/main].")

        data = self.redis.hgetall("times_lessons")
        result = {}

        for number_lesson, value in data.items():
            result[number_lesson] = json.loads(value)

        return result
    
    def get_start_recession(self, number_lesson: int = None, _debug: bool = True) -> str:
        """
        
        Получение начала перемены.

        Args:
            number_lesson (int): Номер урока.
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            str: Начало перерыва.
        """

        if number_lesson is None: return
        
        start_recession = json.loads(self.redis.hget("times_lessons", str(number_lesson)))["start_recession"]

        if _debug:
            print_debug("DataBase", "Get [main]start recession[/main]: [main]" + start_recession + "[/main].")

        return start_recession
    
    def get_start_lesson(self, number_lesson: int = None, _debug: bool = True) -> str:
        """
        
        Получение начала пары.

        Args:
            number_lesson (int): Номер пары.
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            str: Начало пары.
        """

        if number_lesson is None: return

        start_lesson = json.loads(self.redis.hget("times_lessons", str(number_lesson)))["start_lesson"]

        if _debug:
            print_debug("DataBase", "Get [main]start lesson[/main]: [main]" + start_lesson + "[/main].")

        return start_lesson
    
    def get_end_lesson(self, number_lesson: int = None, _debug: bool = True) -> str:
        """
        
        Получение конца пары.

        Args:
            number_lesson (int): Номер пары.
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            str: Конец пары.
        """

        if number_lesson is None: return

        end_lesson = json.loads(self.redis.hget("times_lessons", str(number_lesson)))["end_lesson"]

        if _debug:
            print_debug("DataBase", "Get [main]end lesson[/main]: [main]" + end_lesson + "[/main].")

        return end_lesson
    
    def get_send_spam(self, number_lesson: int = None, _debug: bool = True) -> str:
        """
        
        Получение время отправки рассылки.

        Args:
            number_lesson (int): Номер пары.
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            str: Время отправки рассылки.
        """

        if number_lesson is None: return

        send_spam = json.loads(self.redis.hget("times_lessons", str(number_lesson)))["send_spam"]

        if _debug:
            print_debug("DataBase", "Get [main]send spam[/main]: [main]" + send_spam + "[/main], number lesson: [main]" + str(number_lesson) + "[/main].")

        return send_spam

    def get_time_zone(self, _debug: bool = True):
        """
        
        Получение временной зоны.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            str: Временная зона.
        """

        if _debug:
            print_debug("DataBase", "Get [main]time zone[/main].")
    
        return self.redis.get("time_zone")
    
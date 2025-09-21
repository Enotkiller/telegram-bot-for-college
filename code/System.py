import datetime
import calendar
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import DataBase

from Debug import print_debug

class System:
    def __init__(self, _database: DataBase.DataBase = None, _debug: bool = True):
        """

        Инициализация системы.

        Args:
            _database (DataBase.DataBase): База данных.
            _debug (bool): Если True, то выводится в консоль сообщение.
        """

        if _debug:
            print_debug("System", "[main]Initialized.[/main]")

        self.database = DataBase.DataBase(_debug = _debug) if _database is None else _database
        self.cancellation = []

    def get_lesson(self, 
                   day_week: int = None, 
                   number_lesson: int = None, 
                   type = None, 
                   _debug: bool = True
                   ) -> tuple[str, str] | tuple[None, None]:
        
        """

        Получение пары.
        
        Args:
            day_week (int): День недели.
            number_lesson (int): Номер урока.
            type (int): Тип урока.
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            tuple[str, str] : id и пара или ничего.
        """
        
        if day_week is None or number_lesson is None: return
        if _debug:
            print_debug("System", f"Get lesson: day: [main]{day_week}[/main], number lesson: [main]{int(number_lesson)}[/main], type: [main]{type}[/main]")
        if int(number_lesson) > 0 and int(number_lesson) <= int(self.database.get_max_lesson_in_days(_debug = False)):    
            ids, lessons = self.database.get_lesson_for_date(day_week, int(number_lesson), _debug = False)
           
            if lessons and ids:           
                lessons.reverse()
                ids.reverse()
                
                return ids[type], lessons[type]
        
        return None, None
    
    def get_lesson_for_date(self, 
                            day: int = None, 
                            mounth: int = None, 
                            year: int = None, 
                            number_lesson: int = None, 
                            _debug: bool = True
                            ) -> tuple[str, str] | set[None, None]:
        
        """

        Получение пары за определенную дату.

        Args:
            day (int): День.
            mounth (int): Месяц.
            year (int): Год.
            number_lesson (int): Номер пары.
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            tuple[str, str] : id и пара или ничего.
        """

        if day is None or number_lesson is None: return
        if _debug:
            print_debug("System", f"Get lesson for date: day: [main]{day}[/main], number lesson: [main]{number_lesson}[/main]")
        date = self.get_day_isoweekly(year = year, mounth = mounth, day = day)
        ids = self.database.get_id_lesson_for_date(day = date, number_lesson = number_lesson, _debug = False)
        _, lessons = self.database.get_lesson_for_date(day = date, number_lesson = number_lesson, _id_lessons = ids, _debug = False)
        type = self.get_week_type(_day = day, _mounth = mounth, _year = year, _debug = False)

  

        if lessons and ids:
            lessons.reverse()
            ids.reverse()
            
            return ids[type], lessons[type]
        
        return None, None
    
    def get_lesson_now(self, 
                       _day = None, 
                       _number_lesson = None, 
                       _type = None, 
                       _debug: bool = True
                       ) -> tuple[str, str] | tuple[None, None]:

        """

        Получение пары сейчас.

        Args:
            _day (int): День.
            _number_lesson (int): Номер пары.
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            tuple[str] : id и пара или ничего.
        """

        

        day = self.get_day_isoweekday_now(_debug = False) if _day is None else _day
        number_lesson = self.get_lesson_number_now_without_type() if _number_lesson is None else _number_lesson
        ids = self.database.get_id_lesson_for_date(day = day, number_lesson = number_lesson, _debug = False)
        _, lessons = self.database.get_lesson_for_date(day = day, number_lesson = number_lesson, _id_lessons = ids, _debug = False)
        type = self.get_week_type(_debug = False) if _type is None else _type

        if _debug:
            print_debug("System", f"Get [main]lesson now[/main]. day: [main]{day}[/main], number lesson: [main]{number_lesson}[/main], type: [main]{type}[/main]")
        
        if lessons and ids:                    
            lessons.reverse()
            ids.reverse()

            return ids[type], lessons[type]
        
        return None, None
    
    def get_url(self, 
                _day = None, 
                _number_lesson = None, 
                _type = None, 
                _id = None, 
                _debug: bool = True
                ) -> str | None:

        """

        Получение ссылки.

        Args:
            _day (int): День.
            _number_lesson (int): Номер пары.
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            str : ссылка или ничего.
        """

        if _id:
            return self.database.get_url_for_id(id = _id, _debug = False)
        
        day = self.get_day_isoweekday_now(_debug = False) if _day is None else _day
        number_lesson = self.get_lesson_number_now_without_type(_debug = False) if _number_lesson is None else _number_lesson
        type = self.get_week_type(_debug = False) if _type is None else _type
        id, lesson = self.get_lesson(day_week = day, number_lesson = number_lesson, type = type, _debug = False)
        
        if _debug:
            print_debug("System", f"Get [main]url[/main], day: [main]{day}[/main], number lesson: [main]{number_lesson}[/main], type: [main]{type}[/main], lessons: [main]{lesson}[/main].")
        
        if lesson:
            return self.database.get_url_for_id(id = id, _debug = False)
        return None
    
    def recess_now(self, _debug: bool = True) -> bool:
        """

        Проверка на перемену.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            bool : True - перемена, False - нет.
        """

        if _debug:
            print_debug("System", "Get [main]recess now[/main].")

        return False if self.get_number_lesson_now() > 0 else True

    def get_url_now(self, _debug: bool = True) -> str:
        """

        Получение ссылки за текущию пару.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            str : ссылка.
        """
        
        if _debug:
            print_debug("System", "Get [main]url now[/main].")

        return self.get_url()


    def get_day_isoweekday_now(self, _debug: bool = True) -> np.uint8:
        """

        Получение дня недели сейчас.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            np.uint8 : день недели.
        """

        if _debug:
            print_debug("System", "Get [main]day weekly now[/main].")

        return np.uint8(datetime.datetime.now().isoweekday())

    def get_day_isoweekly(self, 
                          year: int = None, 
                          mounth: int = None, 
                          day: int = None
                          ) -> int:
        
        """

        Получение дня недели.

        Args:
            year (int): Год.
            mounth (int): Месяц.
            day (int): День.
        Returns:
            int : день недели.
        """
        max_days_in_mounth = calendar.monthrange(year, mounth)[1]
        if mounth > 0 and mounth < 13 and day > 0 and day < max_days_in_mounth:
            date = datetime.date(year if year else 2025, mounth if mounth else datetime.datetime.now().month, day if day else datetime.datetime.now().day)
            return int(date.isoweekday())

    def get_week_type(self, 
                      type: int = None, 
                      day: int = None, 
                      mounth: int = None, 
                      year: int = None, 
                      _day: int = None, 
                      _mounth: int = None, 
                      _year: int = None, 
                      _debug: bool = True
                      ) -> np.uint8:
        
        """

        Получение типа недели.

        Args:
            type (int): Тип недели изначально.
            day (int): День изначально.
            mounth (int): Месяц изначально.
            year (int): Год изначально.
            _day (int): День сейчас.
            _mounth (int): Месяц сейчас.
            _year (int): Год сейчас.
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            np.uint8 : тип недели.
        """

        if _debug:
            print_debug("System", "Get [main]week type[/main].")
        
        when_mounth, when_day, when_year = mounth if mounth else self.database.get_data_week_type(_debug = False)["month"], day if day else self.database.get_data_week_type(_debug = False)["day"], year if year else self.database.get_data_week_type(_debug = False)["year"]
        when_mounth, when_day, when_year = np.uint(when_mounth), np.uint(when_day), np.uint(when_year)
        mounth = int(datetime.datetime.now().strftime("%m")) if not _mounth else _mounth
        day = int(datetime.datetime.now().strftime("%d")) if not _day else _day
        year = int(datetime.datetime.now().strftime("20%y")) if not _year else _year
        
        max_type = self.database.get_number_of_weeks_types(_debug = False) - 1
        type = type if type is not None else self.database.get_data_week_type(_debug = False)["type"]
        days = np.uint16(0)
        
        mounth, day, year, max_type = np.uint(mounth), np.uint(day), np.uint(year), np.uint(max_type)

        if self.get_day_isoweekly(year = when_year, mounth = when_mounth, day = when_day) == 1:
            type += 1
            if type > max_type:
                type = 0
        
        for i in range(mounth - when_mounth + 1):
            for j in range(1, calendar.monthrange(year, i + when_mounth)[1] + 1):
                if i == 0 and j <= when_day - 1:
                    pass
        
                else:
                    if self.get_day_isoweekly(year = year, mounth = when_mounth + i, day = j) == 1:
                        days += 1
        
                    if i + when_mounth == mounth and j >= day:
                        break
        
        for i in range(days):
            type += 1
            if type > max_type:
                type = 0
            

        return int(type)

    def get_lesson_type(self, lesson : int = 0, _debug: bool = True) -> bool:
        """

        Получение типа пары (перемена или уже идёт).

        Args:
            lesson (int): Урок.
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            bool : тип пары(true - перемена, false - уже идёт).
        """
        
        if _debug:
            print_debug("System", "Get [main]pair lesson type[/main].")
        
        if lesson != 0:
            if lesson < 0:
                return True
        
            else:
                return False

    def get_number_lesson_now(self) -> np.int8:
        """

        Получение номера пары сейчас.

        Returns:
            np.int8 : номер пары.
        """
        
        time_now = self.get_time_float(_debug = False)
        times = self.database.get_times(_debug = False)
        for number_lesson in times:
            if self.get_time_float(_time = times[number_lesson]["start_recess"], _debug = False) <= time_now <= self.get_time_float(_time = times[number_lesson]["start_lessons"], _debug = False):
                return np.int8(-int(number_lesson))
            
            if self.get_time_float(_time = times[number_lesson]["start_lessons"], _debug = False) <= time_now <= self.get_time_float(_time = times[number_lesson]["end_lessons"], _debug = False):
                return np.int8(int(number_lesson))

        return np.int8(0)

    def get_time_now(self, _debug: bool = True) -> datetime.datetime:
        """

        Получение времени сейчас.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            datetime.datetime : время.
        """

        if _debug:
            print_debug("System", "Get [main]time now[/main].")
    
        time_zone = ZoneInfo(self.database.get_time_zone(_debug = False))
        time_now = datetime.datetime.now(time_zone)
        return time_now

    def get_time_str(self, _time = None, _debug: bool = True) -> str:
        """

        Получение времени сейчас в str.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            str : время.
        """
        
        if _debug:
            print_debug("System", "Get [main]time[/main] in [main]time str[/main].")
    
        time = self.get_time_now(_debug = False) if _time is None else _time
        return f"{(str('0') + str(time.hour)) if int(time.hour) < 10 else str(time.hour)}:{(str('0') + str(time.minute)) if int(time.minute) < 10 else str(time.minute)}"

    def get_time_float(self, _time = None, _debug: bool = True) -> float:
        """

        Получение времени сейчас в float.
        Пример: 12.30, 12.50.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            float : время.
        """
        
        if _debug:
            print_debug("System", "Get [main]time[/main] in [main]time float[/main].")
    
        if _time is None:
            time = self.get_time_now(_debug = False) 
            return float(float(time.hour) + (float(time.minute) / 100))
        else:
            if type(_time) == str and _time != "" and ":" in _time:
                return float(_time.split(":")[0] + "." + _time.split(":")[1])
    
    def get_lesson_number_now_without_type(self, _debug: bool = True) -> np.uint8:
        """

        Получение номера пары сейчас без типа.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            np.uint8 : номер пары.
        """

 
        number_lesson = self.get_number_lesson_now()
        
        if _debug:
            print_debug("System", f"Get [main]lesson number now without type[/main], number lesson: [main]{number_lesson}[/main].")
        
        
        return np.int8(number_lesson if number_lesson > 0 else int(number_lesson) * -1)

    def set_cancellation_on_lesson(self, mass : Any = None, _debug: bool = True) -> None:
        """

        Установка отмены на пару.

        Args:
            mass (Any): Масса.
            _debug (bool): Если True, то выводится в консоль сообщение.
        """
        
        if mass is None:
            self.cancellation.append([self.get_lesson_number_now_without_type(_debug = False), self.get_day_isoweekday_now(_debug = False)])
        
        else:
            if type(mass) == int:
                mass = [mass]
            
            if type(mass) == str:
                mass = [int(mass)]
            
            if type(mass) == float:
                mass = [int(mass)]
            
            if type(mass) == list or type(mass) == tuple:
                for i in mass:
                    self.cancellation.append([i, self.get_day_isoweekday_now(_debug = False)])
                if _debug:
                    print_debug("System", "Set [main]cancellation[/main] on [main]lesson[/main].")

    def get_cancellation(self, _debug: bool = True) -> bool:
        """

        Проверка на то что отменена сейчас пара.

        Args:
            _debug (bool): Если True, то выводится в консоль сообщение.
        Returns:
            bool : True - отменена, False - нет.
        """

        if _debug:
            print_debug("System", "Get [main]cancellation[/main].")
    
        delete = []
        for i in range(len(self.cancellation)):
            cancel = self.cancellation[i]
            if cancel[1] is self.get_day_isoweekday_now(_debug = False):
                if cancel[0] < self.get_day_isoweekday_now(_debug = False):
                    delete.append(self.cancellation[i])

            elif cancel[1] < self.get_day_isoweekday_now(_debug = False):
                delete.append(self.cancellation[i])

        for i in delete:
            self.cancellation.pop(self.cancellation.index(i))

        for i in range(len(self.cancellation)):
            if self.cancellation[i][0] == self.get_lesson_number_now_without_type(_debug = False) and self.cancellation[i][1] == self.get_day_isoweekday_now(_debug = False):
                return True

        return False

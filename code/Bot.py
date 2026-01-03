from datetime import timedelta, datetime
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, CommandObject
from zoneinfo import ZoneInfo
import asyncio

from Debug import print_debug
from System import System
from DataBase import DataBase


class BotСollege:
    def __init__(self, _token = None, _debug = True):
        """

        Инициализация бота, базы данных и системы.

        Args:
            _token (str): Токен бота.
            _debug (bool): Если True, то выводится в консоль сообщение.
        """

        if _debug:
            print_debug("Bot", "[main]Initialized.[/main]")
        self.database: DataBase = DataBase(_debug=_debug)
        self.system: System = System(_database=self.database, _debug=_debug)

        self.days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
        TOKEN = _token if _token else self.database.get_token()
        self.bot = Bot(token=TOKEN)
        self.dp = Dispatcher(bot=self.bot)

        self.dp.message.register(self.start_command, CommandStart())
        self.dp.message.register(self.send_lesson, Command("para"))
        self.dp.message.register(self.cancel_lesson, Command("cancel"))
        self.dp.message.register(self.pingme, Command("pingme"))
        self.dp.message.register(self.pingwho, Command("pingwho"))

    async def start_command(self, message: Message):
        """

        Команда - /start\n
        Выводит приветствие.

        Args:
            message (Message): Сообщение.
        """

        await message.reply(text="Привет, я <b>бот</b> для уведомлений о парах.\n<b>/para [None | all | next | number]</b> - выводит текущую пару.\n<b>/cancel [None | number | list[number]]</b> - отменяет пары.\n<b>/pingme</b> - добавляет в список пингов.\n<b>/pingwho</b> - выводит список пингов.\n", parse_mode=ParseMode.HTML)

    async def send_lesson(self, message: Message, command: CommandObject):
        """

        Команда - /para агрументы\n
        Если аргументы не указаны, то выводится текущая пара.\n
        Если аргумент all, то выводятся все пары на сегодня.\n
        Если аргумент next, то выводятся все пары на завтра.\n
        Если вести число то выведет пары на этот день под этим номером.\n

        Args:
            message (Message): Сообщение.
            command (CommandObject): Аргументы.
        """

        args = command.args.split() if command.args is not None else None

        print_debug(
            "Bot",
            f"Send [main]lesson[/main], parameters: [main]{args if args is None else ", ".join(args)}[/main].",
        )

        if args is None:
            _, lesson = self.system.get_lesson_now()
            text_lesson = f"{str("Текущая") if not self.system.recess_now() else str("Будет")} пара: <b>{lesson}</b>."
            text_status = f"Статус: <b>{str("Отпустили") if self.system.get_cancellation() else 'Перемена' if self.system.recess_now() else str("Идёт")}</b>."
            text_url = f"Ссылка: {self.system.get_url_now()}"
            if lesson is None:
                await message.answer(text="На сегодня пар нет.")
                return

            else:
                await message.answer(
                    text=f"{self.days[self.system.get_day_isoweekday_now() - 1]}\n{text_lesson}\n{text_status}\n{text_url}",
                    parse_mode=ParseMode.HTML,
                )
                return

        elif args[0].lower() == "all":
            if self.system.get_day_isoweekday_now() <= 5:
                text = ""
                lesson_number = self.system.get_number_lesson_now()
                for i in range(1, self.database.get_max_lesson_in_days() + 1):
                    _, lesson = self.system.get_lesson_now(_number_lesson=int(i))
                    if lesson:
                        if i == lesson_number:
                            text = f"{text}\t{i} - <b>{lesson}</b> (Текущая)\n"

                        else:
                            text = f"{text}\t{i} - {lesson}\n"

                await message.answer(
                    text=f"{self.days[self.system.get_day_isoweekday_now() - 1]}\n{text}",
                    parse_mode=ParseMode.HTML,
                )
                del text, lesson
                return

            else:
                await message.answer(text="Сегодня пар нет.")
                return

        elif args[0].lower() == "next":
            if (
                self.system.get_day_isoweekday_now() < 5
                or self.system.get_day_isoweekday_now() == 7
            ):
                text = ""
                day = (
                    self.system.get_day_isoweekday_now() + 1
                    if self.system.get_day_isoweekday_now() < 7
                    else 1
                )
                date = datetime.now(
                    ZoneInfo(self.database.get_time_zone())
                ) + timedelta(days=1)

                for i in range(1, self.database.get_max_lesson_in_days() + 1):
                    _, lesson = self.system.get_lesson_now(
                        _day=day,
                        _number_lesson=int(i),
                        _type=self.system.get_week_type(
                            _day=date.day,
                            _mounth=date.month,
                            _year=date.year,
                            _debug=False,
                        ),
                    )
                    if lesson:
                        text = f"{text}\t{i} - {lesson}\n"

                await message.answer(
                    text=f"{self.days[self.system.get_day_isoweekday_now() if day != 1 else 0]}\n{text}"
                )
                del text, lesson
                return

            else:
                await message.reply(text="Завтра пар нет.")
                return

        elif str(args[0]).isdigit():
            if 0 < int(args[0]) <= self.database.get_max_lesson_in_days():
                _, lesson = self.system.get_lesson_now(_number_lesson=int(args[0]))
                if lesson:
                    await message.answer(
                        text=f"{self.days[self.system.get_day_isoweekday_now() - 1]}\n\t{args[0]} - {lesson}\nСсылка: {self.system.get_url(_number_lesson = int(args[0]))}"
                    )

                else:
                    await message.reply(
                        text=f"{str(args[0])} пары в {self.days[self.system.get_day_isoweekday_now() - 1]} нет."
                    )

            else:
                await message.reply(text="Такой пары нет.")
            return
        
    async def cancel_lesson(self, message: Message, command: CommandObject):
        """
        Команда /cancel аргументы\n
        Если вести число то отменится пара под этим номером на сегодня.\n
        Если ничего не вести то отменится сейчсас пара.\n

        Args:
            message (Message): Сообщение.
            command (CommandObject): Аргументы.
        """

        print_debug(
            "Bot",
            f"Send [main]cancel[/main], parameters: [main]{command.args if command.args is not None else None}[/main].",
        )

        args = str(command.args).replace(" ", "").replace(",", "") if command.args is not None else None
        mass = []
        if args:
            for i in args:
                if str(i).isdigit():
                    if 0 < int(i) <= self.database.get_max_lesson_in_days(_debug = False):
                        mass.append(int(i))

        self.system.set_cancellation_on_lesson(mass = mass or None)

        text = f"Пары отменены: <b>{', '.join([f"номер: {i[0]}, день: {self.days[i[1] - 1]}" for i in self.system.cancellation])}</b>." if self.system.cancellation else "Нет отмен."
        await message.answer(text, parse_mode=ParseMode.HTML)

    async def pingme(self, message: Message):
        """

        Команда /pingme\n
        Добавляет в список пингов или удаляет.

        Args:
            message (Message): Сообщение.
        """
        print_debug("Bot", "Send [main]pingme[/main].")

        result = self.database.add_user_in_pings(
            username=message.from_user.username, user_id=message.from_user.id
        )
        if result:
            await message.reply(
                text="Вы были <b>добавлены</b> в список пингов.",
                parse_mode=ParseMode.HTML,
            )

        else:
            await message.reply(
                text="Вы были <b>удалены</b> в списке пингов.",
                parse_mode=ParseMode.HTML,
            )

    async def pingwho(self, message: Message):
        """

        Команда /pingwho\n
        Выводит список пингов.

        Args:
            message (Message): Сообщение.
        """
        await message.reply(
            text=f"Вот всё кого будет пинговать: <b>{", ".join(self.database.get_all_usernames())}</b>.",
            parse_mode=ParseMode.HTML,
        )

    async def send_message(self):
        """

        Рассылка сообщения(какая пара будет) во все чаты, а после пингует список пингов.

        """
        print_debug("Bot", "Send message.")
        if int(self.system.get_day_isoweekday_now()) <= 5:
            if not self.system.get_cancellation():
                _, lesson = self.system.get_lesson_now()
                if lesson:
                    for chat_id in self.database.get_chats_id():
                        print_debug("Bot", f"Send message to [main]{chat_id}[/main].")
                        try:
                            await self.bot.send_message(
                                chat_id=chat_id,
                                text=f"Следующая пара: <b>{lesson}</b>\nСсылка: {self.system.get_url_now()}.",
                                parse_mode=ParseMode.HTML,
                            )
                            await self.bot.send_message(
                                chat_id=chat_id,
                                text=f"Пинг: @{" @".join(self.database.get_all_usernames())}",
                            )

                        except Exception as e:
                            print_debug("Bot", "Error: [red]" + str(e) + "[/red]")

    async def scheduler(self, target_times: list):
        """

        Ожидание и отправляет рассылку в указанное время.

        Args:
            target_times (list): Время отправки сообщения.
        """
        utc_plus_2 = ZoneInfo(self.database.get_time_zone(_debug=False))
        while True:
            now = datetime.now(utc_plus_2)
            future_targets = []
            for time_str in target_times:
                target_hour, target_minute = map(int, time_str.split(":"))
                target = now.replace(
                    hour=target_hour, minute=target_minute, second=0, microsecond=0
                )
                if now > target:
                    target += timedelta(days=1)

                future_targets.append(target)

            next_target = min(future_targets)
            wait_seconds = (next_target - now).total_seconds()
            print_debug(
                "Bot",
                f"Ожидание до [main]{next_target.strftime('%H:%M')}[/main] UTC+2 [main]({wait_seconds:.0f}[/main] секунд).",
            )
            await asyncio.sleep(wait_seconds)
            await asyncio.sleep(1)
            await self.send_message()

    async def on_startup(self):
        """

        Запуск ``scheduler`` в отдельном потоке и передает время отправки рассылок.

        """
        times_spam = []
        for i in range(1, self.database.get_max_lesson_in_days() + 1):
            times_spam.append(self.database.get_send_spam(number_lesson=i))

        print_debug(
            "Bot", "Start scheduler. Times: [main]" + str(times_spam) + "[/main]."
        )
        asyncio.create_task(self.scheduler(times_spam))

    async def start(self):
        """

        Запуск ``on_startup`` и запуск бота.

        """
        await self.on_startup()
        await self.dp.start_polling(self.bot)


if __name__ == "__main__":
    asyncio.run(BotСollege().start())

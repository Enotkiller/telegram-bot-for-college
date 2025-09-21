from rich.console import Console

class debug():
    _instance = None  # Правильное имя переменной

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init()
        return cls._instance
    
    def init(self):
        self.console = Console()
        self.config = {
            "main": "#00BCD9",
            "grey": "#939393",
            "red": "#920000"
        }


debug_varible = debug()

def print_debug(left = None, right = None, add_to_rjust = 0):
    debug_varible.console.print(f"[bold][{debug_varible.config['grey']}]{str(left).rjust(30 + add_to_rjust)} | {convert(str(right))}[/{debug_varible.config['grey']}][/bold]")

def convert(text):
    return str(text).replace("[main]", f"[{debug_varible.config['main']}]").replace("[/main]", f"[/{debug_varible.config['main']}]").replace("[/red]", f"[/{debug_varible.config['red']}]").replace("[red]", f"[{debug_varible.config['red']}]").replace("[/grey]", f"[/{debug_varible.config['grey']}]").replace("[grey]", f"[{debug_varible.config['grey']}]")
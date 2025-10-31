import datetime
import platform
def banner() -> str:
    return (
        "Bonjour Docker !\n"
        f"Date et heure : {datetime.datetime.utcnow().isoformat()}Z\n"
        f"Système : {platform.system()} {platform.release()}"
    )
if __name__ == "__main__":
    print(banner())
from argh import aliases
from taskcli import task, tt, run
import requests


with tt.Group("Weather"):
    @task(aliases="w")
    def weather():
        """auto-determine the current city, and check weather there."""
        city = requests.get("https://ipinfo.io").json()
        city = city["city"]
        weather_in(city) # call the other task

    @task
    def weather_in(city):
        """Curl wttr.in to check the weather in the given city."""
        run(f"curl wttr.in/{city}")

@task(aliases="du")
def display_disk_usage(host:str="localhost", *, remote_user:str="root"):
    """Display disk usage. If host other than localhost, ssh to host first."""
    if host == "localhost":
        run("df -h")
    else:
        run(f"ssh {remote_user}@{host} df -h")

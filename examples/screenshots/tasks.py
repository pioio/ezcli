from argh import aliases
from taskcli import task, tt, run
import requests

tt.config.merge_with_parent = True


with tt.Group("Weather"):
    @task(aliases="here")
    def weather_here():
        """auto-determine the current city, and check weather there."""
        city = requests.get("https://ipinfo.io").json()["city"]
        weather_in(city) # call the other task
        run("pwd")

    @task
    def weather_in(city):
        """Curl wttr.in to check the weather in the given city. Mandatory argument."""
        run(f"curl wttr.in/{city}")

    @task
    def test():
        """Conflicting name""" # TODO: remove me
        run("Hello, tst")

    for city in ["Boston", "Sydney", "London", "Yokohama"]:
        @task(hidden=True, name=f"weather-{city.lower()}", desc=f"Check weather in {city}.")
        def weather_in_a_city(city=city): # we need the arg to bind the loop variable
            weather_in(city)

    @task(aliases="w")
    def weather(cities:list[str]=[]):
        """Check weather here (no arg), or specify seceral Cities."""
        if cities:
            for city in cities:
                weather_in(city)
        else:
            weather_here()

@task(aliases="du")
def display_disk_usage(host:str="localhost", *, remote_user:str="root"):
    """Display disk usage. If host other than localhost, ssh to host first."""
    if host == "localhost":
        run("df -h")
    else:
        run(f"ssh {remote_user}@{host} df -h")

@task
def say_hello(message="Hello, world!", *, repeat:int=1):
    """Say hello."""
    for _ in range(repeat):
        print(message)

@task(aliases=["ls", "list"]) # multiple aliases
def list_files(files:list[str]=["."]):
    """List files. Optionally append '-- <args>' to add any number of custom arguments."""
    args = tt.get_extra_args()
    run(f"ls --color=always {' '.join(files)} {args} ")
# Building the app image

The app can be build as a Docker image:

```bash
~/Projects/Scraping-Reference$ docker build -f docker/Dockerfile -t coffeescraper:latest .
```

And example [Docker compose file](../docker/docker-compose.yml) is provided as well.

You would typically:

- build the image
- push it to your registry
- [on the machine where you run your docker container] pull the image
- run the app

The app can be run once with:

```bash
cd CoffeeScraper/docker
docker-compose run -d app
```

This will automatically run the database too, and stop the app container once it is done.

Since this app typically needs to run only once a day, there is no need to have these
containers up and running 24/7, so to conserve energy I have eveything configured as
cronjobs:

```crontab
5 6 * * * docker-compose -f /home/michel/docker/coffeescraper/docker-compose.yml run -d app
10 6 * * * docker-compose -f /home/michel/docker/coffeescraper/docker-compose.yml down
15 6 * * * docker container prune --filter until=3d -f
```

This will run the app at 5 past 6 in the morning (the app, and therefore the container,
exits after scraping the configured sites once), bring down the database 5 minutes later
(the data is persisted on a volume), and again 5 minutes later all stopped containers are
removed that are older than three days (so we don't keep on storing stopped containers
endlessly,\ but could still inspect the logging for a few days if something went wrong)

# Jukebox Radio

Part jukebox. Part radio.

## Installation

### Docker

In this section, we assume that you are installing Jukebox Radio locally. If you are installing Jukebox Radio on a remote server, change `local` to `production` where appropriate.

First, create your environment files. Then, fill them in.

    cp -r .envs/.template .envs/.local

Build the Docker image.

    docker-compose -f local.yml build

Create a superuser. Before you do that, you will have to run migrations.

    docker-compose -f local.yml run --rm django python manage.py migrate
    docker-compose -f local.yml run --rm django python manage.py createsuperuser

Some manual adjustments to the application must be made.

    docker-compose -f local.yml run --rm django python manage.py shell_plus

    # Update the Site object
    In [1]: Site.objects.update(domain="localhost:3000")
    Out[1]: 1

    # Create cron schedule
    In [2]: tz = timezone.get_current_timezone()
    In [3]: crontab = CrontabSchedule.objects.create(minute='26', hour='*', day_of_week='*', day_of_month='*', month_of_year='*', timezone=tz)

    # Register cron task
    In [4]: task_name = 'jukebox_radio.users.tasks.refresh_spotify_access_tokens'
    In [5]: PeriodicTask.objects.create(name=task_name, task=task_name, crontab=crontab)
    Out[5]: <PeriodicTask: jukebox_radio.users.tasks.refresh_spotify_access_tokens: 27 * * * * (m/h/d/dM/MY) UTC>

Run the following to start the Django server.

    docker-compose -f local.yml up

Or to run in a detached (background) mode, just run.

    docker-compose -f local.yml up -d

### DigitalOcean

1: Create a new project in Digital Ocean.
2: Register a domain to the project with 3 NS records and 2 A records.
3: Create a new "Docker 19.03.12 on Ubuntu 20.04" droplet from the marketplace.
4: SSH into droplet.
5: `ssh-keygen`
6: `pbcopy < ~/.ssh/id_rsa.pub`
7: Upload SSH key to GitHub settings.
8: `git clone git@github.com:0x213F/jukebox-radio-web.git`
9: Follow "Docker" instructions.

## FAQ

To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

This project was created from [Cookiecutter Django](https://github.com/pydanny/cookiecutter-django).

* [Settings](https://cookiecutter-django.readthedocs.io/en/latest/settings.html)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)

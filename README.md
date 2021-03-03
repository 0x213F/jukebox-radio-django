# Jukebox Radio
Part jukebox. Part radio.

## Installation
We assume you are installing Jukebox Radio locally. If you are installing Jukebox Radio on a server, just modify the commands from `local` to `production` where necessary.

### Docker
First, create your environment files.

    cp -r .envs/.template .envs/.local

Next, fill them in.

    vim .envs/.local/.django
    vim .envs/.local/.postgres

Build the Docker image.

    docker-compose -f local.yml build

Now is a good time to create a superuser. However, before you do that you will have to run migrations.

    docker-compose -f local.yml run --rm django python manage.py migrate
    docker-compose -f local.yml run --rm django python manage.py createsuperuser

In order for things to run smoothly, some manual adjustments must be made to the application.

    docker-compose -f local.yml run --rm django python manage.py shell_plus

<!-- br -->

    # Update the Site object
    Site.objects.update(domain="localhost:3000")

    # Create cron schedule
    tz = timezone.get_current_timezone()
    crontab = CrontabSchedule.objects.create(
        minute='26',
        hour='*',
        day_of_week='*',
        day_of_month='*',
        month_of_year='*',
        timezone=tz,
    )

    # Register cron tasks
    task_name = 'jukebox_radio.users.tasks.refresh_spotify_access_tokens'
    PeriodicTask.objects.create(name=task_name, task=task_name, crontab=crontab)

Finally, run the following to start the Django server.

    docker-compose -f local.yml up

Or run in a detached (background) mode.

    docker-compose -f local.yml up -d

Navigate to `localhost:8000` to verify that the server is working.

### AWS
https://medium.com/@chandupriya93/deploying-docker-containers-with-aws-ec2-instance-265038bba674

Launch a standard Linux micro (free tier) instance.

Select or create a security group. It is a good idea to consider SSH and HTTP access limitations.

Select or create a private key file. Download the file on your system. Then move the file to the following location:

    /Users/josh/.ssh/<SECURITY-GROUP>.pem

From here, create a micro (free tier) Postgres database in RDS. Create via the "Standard create" interface so you can setup an initial database under the "Additional configuration" sub-section. Inspect security settings to make sure the RDS instance can be accessed via the EC2 instance.

By now, you may SSH into your EC2 instance to get the Django server up and running.

    ssh -i <SECURITY-GROUP>.pem ec2-user@<EC2-INSTANCE-PUBLIC-IP-ADDRESS>

Run the following commands to get Docker working.

    sudo yum install -y docker
    sudo service docker start
    sudo groupadd docker
    sudo usermod -aG docker $USER
    newgrp docker

You can verify that Docker is working by running:

    docker run hello-world

Make sure Docker reboots when the machine restarts by running:

    sudo systemctl enable docker

Now that the underlying setup is complete, start installing all the required software.
Generate a SSH key:

    ssh-keygen -t rsa -b 4096 -C <SYSADMIN@DOMAIN.EXT>
    cat ~/.ssh/id_rsa.pub

Add the SSH key to your GitHub account. Then, pull the latest code.

    sudo yum install git
    git clone git@github.com:0x213F/jukebox-radio-django.git

The moment you have been waiting for!

    cd jukebox-radio-django/

Fix some files:

    grep -rnw . -e 'jukebox\.radio'
    vim jukebox_radio/contrib/sites/migrations/0003_set_site_domain_and_name.py

Setup the local environment variables:

    mkdir .envs/.production
    touch .envs/.production/.django
    vim .envs/.production/.django
    touch .envs/.production/.postgres
    vim .envs/.production/.postgres

Try setting Docker up once more:

    sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    docker-compose --version

    docker-compose -f production.yml build
    docker-compose -f production.yml run --rm django python manage.py migrate
    docker-compose -f production.yml run --rm django python manage.py createsuperuser

In order for things to run smoothly, some manual adjustments must be made to the application.

    docker-compose -f production.yml run --rm django python manage.py shell

<!-- br -->

    # Create cron schedule
    from django.utils import timezone
    tz = timezone.get_current_timezone()

    from django_celery_beat.models import CrontabSchedule
    crontab = CrontabSchedule.objects.create(
        minute='26',
        hour='*',
        day_of_week='*',
        day_of_month='*',
        month_of_year='*',
        timezone=tz,
    )

    # Register cron tasks
    task_name = 'jukebox_radio.users.tasks.refresh_spotify_access_tokens'
    from django_celery_beat.models import PeriodicTask
    PeriodicTask.objects.create(name=task_name, task=task_name, crontab=crontab)

Finally, run the following to start the Django server.

    docker-compose -f production.yml up


### Digital Ocean
First, you need to [create a Digital Ocean account](https://m.do.co/c/137a789f8b35).

Once that is setup, create a new project. Inside that project, register your domain by creating 3 NS records and 2 A records (`@`, `www`).

Inside that project, create a `Docker 19.03.12 on Ubuntu 20.04` droplet from the marketplace.

Now that you have a machine running Docker, you can follow the "Docker" instructions in the above section.

## Getting started
Now that you have your very own instance of Jukebox Radio, commence the kicking tires!

Below are the domains that you may access.

- Main website at `localhost:3000`
- Admin website at `localhost:3000/admin`
- Celery admin website at `localhost:5555`

To create a normal user account, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

## Developing
Now that you have a working local setup, let us dive into the code setup. This project was created from [Cookiecutter Django](https://github.com/pydanny/cookiecutter-django).

The main components of the application are a Django server, Postgres database, and Celery for asynchronous task processing.

### Testing
`pytest` is used for testing.

    docker-compose -f local.yml run --rm django pytest

To check your test coverage and generate an HTML coverage report, run the following.

    docker-compose -f local.yml run --rm django coverage run -m pytest
    docker-compose -f local.yml run --rm django coverage html
    open htmlcov/index.html

### Type checks

Run type checks with `mypy`.

    docker-compose -f local.yml run --rm django mypy jukebox_radio

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Sponsoring
Please consider financially sponsoring this project with a monetary donation.

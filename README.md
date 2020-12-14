# Jukebox Radio

Foobar is a Python library for dealing with word pluralization.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install foobar
```

## Usage

```python
import foobar

foobar.pluralize('word') # returns 'words'
foobar.pluralize('goose') # returns 'geese'
foobar.singularize('phenomena') # returns 'phenomenon'
```

## Deploy

1: Create a new project in Digital Ocean.
2: Register a domain to the project with 3 NS records and 2 A records.
3: Create a new "Docker 19.03.12 on Ubuntu 20.04" droplet from the marketplace.
4: SSH into droplet.
5: `ssh-keygen`
6: `pbcopy < ~/.ssh/id_rsa.pub`
7: Upload SSH key to GitHub settings.
8: `git clone git@github.com:0x213F/jukebox-radio-web.git`


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)

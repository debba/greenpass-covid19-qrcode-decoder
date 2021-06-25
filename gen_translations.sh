#!/bin/bash

pybabel extract -F babel.cfg -k _l -o messages.pot .
pybabel update -i messages.pot -d translations -l it
pybabel compile -d translations
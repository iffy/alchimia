#!/bin/bash
CONTAINER=$(sudo docker run -d -p 5432:5432 tiokksar/postgres)
DATABASE_URI="postgres://docker:docker@127.0.0.1/docker" tox -e txpostgres
rc=$?
sudo docker kill $CONTAINER
exit $rc
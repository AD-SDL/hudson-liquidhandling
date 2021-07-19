import sys
import mysql.connector
from pathlib import Path

# this is needed to find config.py outside of the repo
home = str(Path.home())
sys.path.append(home)
import config


def connect():
    print("using database {} as iser {}".format(config.DBNAME, config.DBUSER))

    # set up
    try:
        cnx = mysql.connector.connect(
            user=config.DBUSER,
            password=config.DBPASSWD,
            host=config.DBHOST,
            database=config.DBNAME,
        )
    except mysql.connector.Error as err:
        print("unable to commect")
        print(err)

    return cnx


def close(cnx):
    cnx.close()


def main(args):
    cnx = connect()
    close(cnx)


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)

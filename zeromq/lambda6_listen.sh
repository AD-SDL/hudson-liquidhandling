
source /home/brettin/anaconda3/bin/activate /home/brettin/anaconda3/envs/hudson


PY=$(which python)
DB=$(grep DBNAME ${HOME}/config.py)
DBUSER=$(grep DBUSER ${HOME}/config.py)

echo "starting up using python $PY"
echo "starting up using database $DB"
echo "starting up using database user $DBUSER"

nohup python ./lambda6_listen.py > lambda6_listen.log 2>&1 &

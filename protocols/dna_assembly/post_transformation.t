#!/bin/bash

TEST_DIR=${1:-test}

if [ -d "$TEST_DIR/hudson-liquidhandling" ]; then
  # Take action if $DIR exists. #
  echo "$TEST_DIR/hudson-liquidhandling exists"
  pushd $TEST_DIR/hudson-liquidhandling/zeromq/
else
  mkdir -p $TEST_DIR
  pushd $TEST_DIR
  git clone https://github.com/AD-SDL/hudson-liquidhandling
  pushd $TEST_DIR/hudson-liquidhandling/zeromq/
fi


python test/send_shutdown.py --host localhost --port 5555
python test/send_shutdown.py --host localhost --port 5556
python test/send_shutdown.py --host localhost --port 5557
python test/send_shutdown.py --host localhost --port 5558
python test/send_shutdown.py --host localhost --port 5559
ps -ef | grep python | grep listen


cd ../..
mv hudson-liquidhandling hudson-liquidhandling-$(date +'%Y%m%d')
git clone https://github.com/AD-SDL/hudson-liquidhandling
cd hudson-liquidhandling
conda activate hudson
pip uninstall -y liquidhandling
pip install liquidhandling


cd zeromq/
./lambda6_listen.sh
./lambda6_listen_5556.sh
./lambda6_listen_5557.sh
./lambda6_listen_5558.sh
./lambda6_listen_5559.sh



cd ~/test/hudson-liquidhandling/protocols/dna_assembly/
python ./post_transformation.py


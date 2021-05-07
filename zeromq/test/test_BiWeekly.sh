cd test/liquidhandling/
git pull
git status
conda activate hudson
pip uninstall -y liquidhandling
pip install --upgrade liquidhandling
conda install -y path
conda install -y pandas
conda install -y openpyxl
pip install mysql-connector-python
cd example/campaign1
jupyter notebook --no-browser --port 8889 steps_1_2_3_notebook.ipynb

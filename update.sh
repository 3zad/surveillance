mv /surveillance/token.txt /
mv /surveillance/main.db /
rm -r /surveillance
git clone https://github.com/3zad/surveillance.git
mv /token.txt /surveillance/
mv /main.db /surveillance/
cd /surveillance
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install setuptools
python3 -m pip install -r requirements.txt
python3 main.py
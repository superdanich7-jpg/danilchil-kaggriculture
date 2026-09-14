import subprocess, sys

def run(cmd, label):
    print('=== ' + label + ' ===', flush=True)
    subprocess.run(cmd, shell=True)

# Replay identical game seeds for champion v83 (currently opp_champ.py) vs v82
run('python kaggle_environments.py --game halite --agents "bots/opp_champ.py" "bots/opp_champ82.py" --episodes 12',
    'champ v83 vs champ v82, 12 eps')

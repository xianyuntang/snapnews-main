import os
import json
import subprocess

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from model import Channel


def load_system_config():
    with open('config.json', 'r') as f:
        return json.load(f)


def main():
    system_config = load_system_config()
    print(system_config)
    engine = create_engine(
        f"mysql://{system_config['username']}:{system_config['password']}@{system_config['host']}/{system_config['database']}?charset=utf8",
        encoding="utf-8",
        echo=False)
    base = declarative_base()
    base.metadata.create_all(engine)
    _session_ = sessionmaker(engine)
    session = _session_()
    channel_collections = session.query(Channel).all()
    for channel in channel_collections:
        if channel.enable:
            cmd = "python ./TextRecognition.py -dh {} -cu {} -cn {} -u {} -p {} -dn {} -r {} -l {}".format(
                system_config['host'], channel.url, channel.name, system_config['username'],
                system_config['password'], system_config['database'], system_config['text_recognition_api_url'],
                system_config['text_localization_api_url'])
            print(f'run {cmd}')
            subprocess.Popen(cmd, shell=True)


if __name__ == '__main__':
    main()
    input('snapnews is running ...')

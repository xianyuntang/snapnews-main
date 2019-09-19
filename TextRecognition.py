import cv2
import requests
import json
import time
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from model import Record, UserProfile, Keyword
from argparse import ArgumentParser
import os


class TextRecognition:

    def __init__(self, args):
        self.args = args
        self.engine = create_engine(
            f"mysql://{self.args.dbusername}:{self.args.dbpassword}@{self.args.dbhost}/{self.args.dbname}?charset=utf8",
            encoding="utf-8",
            echo=False)
        self.base = declarative_base()
        self.base.metadata.create_all(self.engine)
        _session_ = sessionmaker(self.engine)
        self.session = _session_()
        self.keyword_dict = self.init_keyword_dict()
        self.detected_keyword_dict = dict()

        self.run()

    def init_keyword_dict(self):
        keyword_dict = {}
        keyword = self.session.query(Keyword).all()
        for k in keyword:
            if k.user_id not in keyword_dict:
                keyword_dict[k.user_id] = [k.keyword]
            else:
                keyword_dict[k.user_id] +=[k.keyword]

        return keyword_dict

    def text_recognition(self, image):
        files = {
            'file': image.tobytes(),
            'height': image.shape[0],
            'width': image.shape[1],
            'depth': image.shape[2]
        }

        # get boxes
        boxes = requests.post(self.args.textloccurl, files=files)
        boxes = json.loads(boxes.content)
        # get the longest edge
        for box in boxes:
            clipped_image = image[box[1]:box[5], box[0]:box[4]]
            if clipped_image.shape[0] == 0 or clipped_image.shape[1] == 0:
                continue
            height, width, depth = clipped_image.shape

            files = {
                'file': clipped_image.tobytes(),
                'height': height,
                'width': width,
                'depth': depth,
            }
            text = requests.post(self.args.textrecurl, files=files).text
            text = json.loads(text)
            text = text.replace(' ','')
            self.check_keyword(text)
        for user_id, detected_keyword in self.detected_keyword_dict.items():
            self.save_image(image, user_id, detected_keyword)
            self.send_message(user_id, image)
        self.detected_keyword_dict.clear()

    def check_keyword(self, text):
        for u, k_list in self.keyword_dict.items():
            for k in k_list:

                if k in text:
                    if u not in self.detected_keyword_dict:
                        self.detected_keyword_dict[u] = [k]
                    else:
                        if k not in self.detected_keyword_dict[u]:
                            self.detected_keyword_dict[u] += [k]


    def save_image(self, image, user_id, detected_keyword):

        for k in detected_keyword:
            image_name = f'{time.time()}.jpg'
            cv2.imwrite(f'/media/storage/images/{image_name}', image, [cv2.IMWRITE_JPEG_QUALITY, 20])
            record = Record(channel=self.args.channelname, time=datetime.datetime.now(), keyword=k,
                            image=image_name, user_id=user_id)
            self.session.add(record)
        self.session.flush()
        self.session.commit()

    def send_message(self, user, image):
        url = 'https://notify-api.line.me/api/notify'
        user_profile = self.session.query(UserProfile).filter(UserProfile.user_id == user).first()
        api_key = user_profile.line_api_key
        message = f'於 {self.args.channelname} 有 {" ".join(self.detected_keyword_dict[user])} 相關報導'
        _, image_file = cv2.imencode('.jpg', image)
        headers = {
            'Authorization': 'Bearer {}'.format(api_key)
        }

        payload = {'message': message}
        file = {'imageFile': image_file.tobytes()}
        requests.post(url, params=payload, headers=headers, files=file)

    def run(self):

        while True:
            try:
                cap = cv2.VideoCapture(self.args.channeluri)
                if cap.isOpened():
                    _, image = cap.read()
                    self.text_recognition(image)
            except Exception as e:
                with open(os.path.join('.', 'log', f'{(datetime.datetime.now()+datetime.timedelta(hours=8)).date()}.txt'), 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now() + datetime.timedelta(hours=8)} : {e}\n")


def main():
    parser = ArgumentParser()
    parser.add_argument('-dh', '--dbhost', help='IP Address', required=True, type=str)
    parser.add_argument('-cu', '--channeluri', help='Channel URI', required=True, type=str)
    parser.add_argument('-cn', '--channelname', help='Channel URI', required=True, type=str)
    parser.add_argument('-u', '--dbusername', help='Username', required=True, type=str)
    parser.add_argument('-p', '--dbpassword', help='Password', required=True, type=str)
    parser.add_argument('-dp', '--dbport', help='port', default=3306, type=int)
    parser.add_argument('-dn', '--dbname', help='database name', required=True, type=str)
    parser.add_argument('-r', '--textrecurl', help='text recognition API URL', required=True, type=str)
    parser.add_argument('-l', '--textloccurl', help='text localization API URL', required=True, type=str)


    args = parser.parse_args()

    TextRecognition(args)


if __name__ == '__main__':
    main()

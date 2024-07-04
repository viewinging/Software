from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import string

app = Flask(__name__)
CORS(app) #모든 원본(cors)에서의 요청을 허용

#데이터 베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/viewinging'
db = SQLAlchemy(app)

#데이터베이스 모델
class Nickname(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), unique = True)

    def __repr__(self):
        return f'<Nickname {self.name}>'

@app.route("/")
def get_nickname():
    nicknames = Nickname.query.all() #DB에서 모든 닉네임을 조회
    nicknames_list = [{'id': nickname.id, 'name': nickname.name} 
                    for nickname in nicknames]
    return jsonify(nicknames_list)



if __name__ == '__main__':
    with app.app_context():
        db.create_all() #DB 테이블 생성
    app.run(host='0.0.0.0', port=5000)  # host='0.0.0.0'으로 설정.
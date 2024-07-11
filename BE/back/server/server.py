from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy #mariaDB
from flask_cors import CORS, cross_origin   
import random
import string

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) 

#DB설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/viewinging' #DB URI
db = SQLAlchemy(app)    

#DB모델
class Nickname(db.Model):
    id = db.Column(db.Integer, primary_key = True) #ID coulmn(primary key)
    name = db.Column(db.String(50), unique = True)  #NAME coulmn.

    def __repr__(self):
        return f'<Nickname {self.name}>'

@app.route("/") #기본경로
def get_nickname(): #DB->nickname 함수
    nicknames = Nickname.query.all() #DB에서 모든 닉네임을 조회
    nicknames_list = [{'id': nickname.id, 'name': nickname.name}
                    for nickname in nicknames]
    return jsonify(nicknames_list)  #json형식-응답 변환


if __name__ == '__main__':
    with app.app_context():
        db.create_all() #DB 테이블 생성
    app.run(host='0.0.0.0', port=5000)
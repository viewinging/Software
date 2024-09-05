from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin   
import pymysql

app = Flask(__name__)
#cors연결
CORS(app, resources={
        r"/submit-phone": {"origins": "*"},
        r"/trash-kind": {"origins": "*"}
     }) 

# DB설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/viewinging' #DB URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#DB모델
class PhoneNumber(db.Model): #폰번호
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(13), unique=True)

    def __repr__(self):
        return f'<PhoneNumber {self.phone_number}>'

class TrashKind(db.Model): #쓰레기종류
    id = db.Column(db.Integer, primary_key=True)
    trash_name = db.Column(db.String(30), unique=True)

    def __repr__(self):
        return f'<TrashKind {self.trash_name}>'

#랜덤_닉네임 함수
###

@app.route('/submit-phone', methods=['POST'])
def submit_phone():
    data = request.get_json()
    phone_number = data.get('phoneNumber')

    if phone_number:
        #등록 여부확인
        ex_phone_number = PhoneNumber.query.filter_by(phone_number=phone_number).first()

        if ex_phone_number:
            return jsonify({'message': 'login successful'}), 200
        else:
            new_phone_number = PhoneNumber(phone_number=phone_number)
            db.session.add(new_phone_number)
            db.session.commit()
            return jsonify({'message': 'get new phone_number'}), 200
    else:
        return jsonify({'message': 'Phone number is missing'}), 400
        

#(2)쓰레기의 종류 파악 | 라즈베리에 전달 
@app.route('/trash-kind', methods=['POST'])
def submit_trash():
    data2 = request.get_json()
    trash = data2.get('trash')
    if trash == 'plastic':
        return jsonify({'message': 'plastic'}), 200
    else:
        return jsonify({'message': 'Trash is missing'}), 400
        



if __name__ == '__main__':
    with app.app_context():
        db.create_all() #DB 테이블 생성
    app.run(host='0.0.0.0', port=5000)
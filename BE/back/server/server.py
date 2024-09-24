from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin   

app = Flask(__name__)
#cors연결
CORS(app, resources={
        r"/submit-phone": {"origins": "*"},
        r"/trash-kind": {"origins": "*"},
        r"/label": {"origins": "*"}
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
    trash_name = db.Column(db.String(30))

    def __repr__(self):
        return f'<TrashKind {self.trash_name}>'


#폰 번호
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




#쓰레기의 종류
@app.route('/trash-kind', methods=['POST'])
def submit_trash():
    data = request.get_json()
    trash = data.get('trash')
    if trash:
        # 기존 데이터 삭제
        db.session.query(TrashKind).delete()  # 모든 기존 데이터 삭제
        db.session.commit()

        new_trash = TrashKind(trash_name=trash)
        db.session.add(new_trash)
        db.session.commit()

        if trash == '플라스틱':
            print(f"Received label: {trash}")
            return jsonify({'message': 'plastic'}), 200
        elif trash == '비닐':
            print(f"Received label: {trash}")
            return jsonify({'message': 'vinyl'}), 200
        elif trash == '캔':
            print(f"Received label: {trash}")
            return jsonify({'message': 'can'}), 200
        elif trash == '일반쓰레기':
            print(f"Received label: {trash}")
            return jsonify({'message': 'general'}), 200
        else:
            return jsonify({'message': 'Trash is missing'}), 400
    

# POST 요청을 받아서 label을 처리하는 엔드포인트
@app.route('/label', methods=['POST'])
def receive_label():
    data = request.get_json()
    label = data.get('label')
    if label:
        print(f"Received label: {label}")
        return jsonify({'message': 'Label received successfully', 'label': label}), 200
    else:
        return jsonify({'error': 'No label provided'}), 400



if __name__ == '__main__':
    with app.app_context():
        db.create_all() #DB 테이블 생성
    app.run(host='0.0.0.0', port=5000)
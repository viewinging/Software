from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

plus = 200
minus = -200

app = Flask(__name__)

# CORS 설정
CORS(app, resources={
        r"/submit-phone": {"origins": "*"},
        r"/get-nickname": {"origins": "*"},
        r"/auto_manu": {"origins": "*"},
        r"/label": {"origins": "*"},
        r"/compare_result": {"origins": "*"}  # 비교 결과 조회 허용
     })

# DB 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/viewinging'  # DB URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# DB 모델 정의
class PhoneNumber(db.Model):  # 폰번호
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(13), unique=True)
    nickname = db.Column(db.String(4), unique=True)
    scores = db.relationship('CompareResult', backref='phone_number', lazy=True)  # 점수와의 관계 추가

    def __repr__(self):
        return f'<PhoneNumber {self.phone_number}>'

class TrashKind(db.Model):  # 쓰레기 종류
    id = db.Column(db.Integer, primary_key=True)
    trash_name = db.Column(db.String(30))

    def __repr__(self):
        return f'<TrashKind {self.trash_name}>'

class Label(db.Model):  # 라벨
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(30))

    def __repr__(self):
        return f'<Label {self.label}>'

class CompareResult(db.Model):  # 비교 결과 저장
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.String(10))
    score = db.Column(db.Integer)
    phone_number_id = db.Column(db.Integer, db.ForeignKey('phone_number.id'), nullable=False)  # 전화번호와 연결

    def __repr__(self):
        return f'<CompareResult {self.result} - {self.score}>'

# 전화번호 제출
@app.route('/submit-phone', methods=['POST'])
def submit_phone():
    data = request.get_json()
    phone_number = data.get('phoneNumber')

    if phone_number:
        ex_phone_number = PhoneNumber.query.filter_by(phone_number=phone_number).first()

        if ex_phone_number:
            last_four = ex_phone_number.phone_number[-4:]
            return jsonify({'nickname': last_four}), 200
        else:
            nickname = phone_number[-4:]  # 새로운 전화번호의 마지막 4자리로 닉네임 설정
            new_phone_number = PhoneNumber(phone_number=phone_number, nickname=nickname)
            try:
                db.session.add(new_phone_number)
                db.session.commit()
                return jsonify({'nickname': nickname}), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({'message': 'Error saving phone number', 'error': str(e)}), 500
    else:
        return jsonify({'message': 'Phone number is missing'}), 400
    
# 닉네임 반환
@app.route('/get-nickname', methods=['GET'])
def get_nickname():
    phone_number = request.args.get('phoneNumber')

    if phone_number:
        ex_phone_number = PhoneNumber.query.filter_by(phone_number=phone_number).first()

        if ex_phone_number:
            nickname = ex_phone_number.phone_number[-4:]
            return jsonify({'nickname': nickname}), 200
        else:
            return jsonify({'message': 'Phone number not found'}), 404
    else:
        return jsonify({'message': 'Phone number is missing'}), 400

# 자동 | 수동 신호 전달
@app.route('/auto_manu', methods=['POST'])
def manu_outo():
    data = request.get_json()
    mo = data.get('mo')
    if mo:
        try:
            ras_url = "http://10.150.150.80:<Port>/receive_data"
            response = request.post(ras_url, json={'mo': mo})
            if response.status_code == 200:
                return jsonify({'message': 'Data sent to Raspberry Pi successfully!'}), 200
            else:
                return jsonify({'message': 'Data send failed!'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'message': 'mo parameter is missing'}), 400       

def translate_trash(trash):
    translations = {
        '플라스틱': 'plastic',
        '비닐': 'vinyl',
        '캔': 'can',
        '일반쓰레기': 'general'
    }
    return translations.get(trash, None)

# 쓰레기 종류와 라벨 비교
@app.route('/label', methods=['POST'])
def compare_with_data():
    data = request.get_json()
    trash = data.get('trash')  # 쓰레기 종류
    ras_value = 'vinyl'  # 예시 값으로 라벨을 직접 지정, 실제 라벨은 라즈베리파이에서 받아올 것
    if not trash:
        return jsonify({'message': 'Trash is missing'}), 400

    # 번역된 쓰레기 종류
    translated_trash = translate_trash(trash)
    if not translated_trash:
        return jsonify({'message': 'Invalid trash type'}), 400
    
    # 비교
    if ras_value == translated_trash:
        result = 'Right'
        score = plus
    else:
        result = 'Wrong'
        score = minus

    # 가장 최근에 저장된 전화번호 찾기
    recent_phone_number = PhoneNumber.query.order_by(PhoneNumber.id.desc()).first()
    if not recent_phone_number:
        return jsonify({'message': 'No phone number found'}), 404

    # 비교 결과 저장
    compare_result = CompareResult(result=result, score=score, phone_number_id=recent_phone_number.id)
    db.session.add(compare_result)
    db.session.commit()

    return jsonify({'message': result, 'score': score}), 200

# 비교 결과 조회 엔드포인트
@app.route('/compare_result', methods=['GET'])
def get_compare_result():
    recent_results = CompareResult.query.order_by(CompareResult.id.desc()).all()
    if recent_results:
        results = [{'result': r.result, 'score': r.score, 'phone_number': r.phone_number.phone_number} for r in recent_results]
        return jsonify(results), 200
    else:
        return jsonify({'message': 'No comparison results found'}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080)

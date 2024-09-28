from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

plus = 200
minus = -200

app = Flask(__name__)

# CORS 설정
CORS(app, resources={r"/*": {"origins": "*"}})

# DB 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/viewinging'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# DB 모델 정의
class PhoneNumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(13), unique=True)
    nickname = db.Column(db.String(4), unique=True)
    trash_counts = db.relationship('TrashCount', backref='phone_number', lazy=True)
    compare_results = db.relationship('CompareResult', backref='phone_number', lazy=True)

    def __repr__(self):
        return f'<PhoneNumber {self.phone_number}>'

class TrashCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(4), db.ForeignKey('phone_number.nickname'))
    trash_type = db.Column(db.String(30))
    count = db.Column(db.Integer, default=0)
    def __repr__(self):
        return f'<TrashCount {self.nickname} - {self.trash_type}: {self.count}>'

class CompareResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.String(10))
    score = db.Column(db.Integer)
    nickname = db.Column(db.String(4), db.ForeignKey('phone_number.nickname'))

    def __repr__(self):
        return f'<CompareResult {self.result} - {self.score} - {self.nickname}>'

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
            nickname = phone_number[-4:]
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
            nickname = ex_phone_number.nickname
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

    # 가장 최근에 저장된 전화번호 찾기
    recent_phone_number = PhoneNumber.query.order_by(PhoneNumber.id.desc()).first()
    if not recent_phone_number:
        return jsonify({'message': 'No phone number found'}), 404

    # 기존 점수 계산
    existing_scores = [result.score for result in recent_phone_number.compare_results]  # CompareResult에서 점수 가져오기
    total_score = sum(existing_scores)

    # 비교
    if ras_value == translated_trash:
        result = 'Right'
        total_score += plus  # 점수 추가
    else:
        result = 'Wrong'
        total_score += minus  # 점수 추가

    # 기존 결과 삭제
    CompareResult.query.filter_by(nickname=recent_phone_number.nickname).delete()

    # 새로운 비교 결과 저장
    compare_result = CompareResult(result=result, score=total_score, nickname=recent_phone_number.nickname)
    db.session.add(compare_result)

    # 쓰레기 갯수 저장
    trash_count = TrashCount.query.filter_by(nickname=recent_phone_number.nickname, trash_type=translated_trash).first()

    if trash_count:
        trash_count.count += 1  # 갯수 증가
    else:
        trash_count = TrashCount(nickname=recent_phone_number.nickname, trash_type=translated_trash, count=1)
        db.session.add(trash_count)

    db.session.commit()

    return jsonify({'message': result, 'score': total_score}), 200

# 쓰레기 갯수 조회
@app.route('/get-trash-counts', methods=['GET'])
def get_trash_counts():
    results = []
    trash_counts = TrashCount.query.all()

    for trash_count in trash_counts:
        results.append({
            'nickname': trash_count.nickname,
            'trash_type': trash_count.trash_type,
            'count': trash_count.count
        })

    return jsonify(results), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080)

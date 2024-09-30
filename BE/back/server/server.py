from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

plus = 200
minus = -200
auto_score_increment = 100  # 자동 점수 증가 값

app = Flask(__name__)

# CORS 설정
CORS(app, resources={r"/*": {"origins": "*"}})

# DB 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/viewinging'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# DB 모델 정의
class PhoneNumber(db.Model):  # 폰번호
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(13), unique=True)
    nickname = db.Column(db.String(4), unique=True)
    trash_counts = db.relationship('TrashCount', backref='phone_number', lazy=True)
    compare_results = db.relationship('CompareResult', backref='phone_number', lazy=True)
    auto_scores = db.relationship('AutoScore', backref='phone_number', lazy=True)  # 추가

    def __repr__(self):
        return f'<PhoneNumber {self.phone_number}>'


class TrashCount(db.Model):  # 쓰레기 종류/갯수
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(4), db.ForeignKey('phone_number.nickname'))
    plastic_count = db.Column(db.Integer, default=0)
    vinyl_count = db.Column(db.Integer, default=0)
    can_count = db.Column(db.Integer, default=0)
    general_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<TrashCount {self.nickname} - Plastic: {self.plastic_count}, Vinyl: {self.vinyl_count}, Can: {self.can_count}, General: {self.general_count}>'


class Label(db.Model):  # 라벨
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(20))

    def __repr__(self):
        return f'<Label {self.label}>'


class CompareResult(db.Model):  # 비교값
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.String(10))
    score = db.Column(db.Integer)
    nickname = db.Column(db.String(4), db.ForeignKey('phone_number.nickname'))

    def __repr__(self):
        return f'<CompareResult {self.result} - {self.score} - {self.nickname}>'


class AutoScore(db.Model):  # 자동 점수
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(4), db.ForeignKey('phone_number.nickname'))
    score = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<AutoScore {self.nickname} - Score: {self.score}>'


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


# 자동 점수 업데이트
@app.route('/auto-value', methods=['POST'])
def auto_value():
    data = request.get_json()
    auto_values = data.get('autoValues')

    if auto_values:
        # 가장 최근에 저장된 전화번호 찾기
        recent_phone_number = PhoneNumber.query.order_by(PhoneNumber.id.desc()).first()

        if not recent_phone_number:
            return jsonify({'message': 'No phone number found'}), 404

        # 자동 점수 증가
        auto_score = AutoScore.query.filter_by(nickname=recent_phone_number.nickname).first()
        if not auto_score:
            auto_score = AutoScore(nickname=recent_phone_number.nickname)
            db.session.add(auto_score)

        auto_score.score += auto_score_increment

        # DB에 저장
        db.session.commit()

        return jsonify({'message': 'The auto values get', 'nickname': recent_phone_number.nickname, 'score': auto_score.score}), 200
    else:
        return jsonify({'message': 'Missing auto values'}), 400

@app.route('/get-auto-value', methods=['GET'])
def get_auto_value():
    # 가장 최근에 저장된 전화번호 찾기
    recent_phone_number = PhoneNumber.query.order_by(PhoneNumber.id.desc()).first()
    
    if not recent_phone_number:
        return jsonify({'message': 'No phone number found'}), 404

    # 해당 전화번호에 대한 자동 점수 찾기
    auto_score = AutoScore.query.filter_by(nickname=recent_phone_number.nickname).first()

    if not auto_score:
        return jsonify({'message': 'No auto score found for this nickname'}), 404

    # 결과 반환
    return jsonify({
        'nickname': auto_score.nickname,
        'score': auto_score.score
    }), 200


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
    trash = data.get('trash')
    # label = data.get('label')

    if not trash:
        return jsonify({'message': 'Trash is missing'}), 400

    # 번역된 쓰레기 종류
    translated_trash = translate_trash(trash)
    if not translated_trash:
        return jsonify({'message': 'Invalid trash type'}), 400

    correct_trash_types = ['vinyl', 'can']  # 임의의 라벨값

    # # 기존 결과 삭제
    # Label.query.filter_by(label=label).delete()

    # # 새로운 비교 결과 저장
    # new_label = Label(label=label)
    # db.session.add(new_label)
    # db.session.commit()

    # 가장 최근에 저장된 전화번호 찾기
    recent_phone_number = PhoneNumber.query.order_by(PhoneNumber.id.desc()).first()
    if not recent_phone_number:
        return jsonify({'message': 'No phone number found'}), 404

    # 기존 점수 계산
    existing_scores = [result.score for result in recent_phone_number.compare_results]
    total_score = sum(existing_scores)

    # 쓰레기 및 라벨값 비교
    if translated_trash in correct_trash_types:
        result = 'Right'
        total_score += plus

        # 쓰레기 갯수 저장
        trash_count = TrashCount.query.filter_by(nickname=recent_phone_number.nickname).first()

        if not trash_count:
            # 새로운 사용자의 경우 TrashCount 레코드 생성
            trash_count = TrashCount(nickname=recent_phone_number.nickname)
            db.session.add(trash_count)

        # 기존 사용자의 경우 해당 사용자에 대한 쓰레기 종류에 따른 카운트 업데이트
        if translated_trash == 'plastic':
            trash_count.plastic_count = (trash_count.plastic_count or 0) + 1
        elif translated_trash == 'vinyl':
            trash_count.vinyl_count = (trash_count.vinyl_count or 0) + 1
        elif translated_trash == 'can':
            trash_count.can_count = (trash_count.can_count or 0) + 1
        elif translated_trash == 'general':
            trash_count.general_count = (trash_count.general_count or 0) + 1

    else:
        result = 'Wrong'
        total_score += minus

    # 기존 결과 삭제
    CompareResult.query.filter_by(nickname=recent_phone_number.nickname).delete()

    # 새로운 비교 결과 저장
    compare_result = CompareResult(result=result, score=total_score, nickname=recent_phone_number.nickname)
    db.session.add(compare_result)

    db.session.commit()

    # 쓰레기 갯수 조회
    counts = {}
    trash_count = TrashCount.query.filter_by(nickname=recent_phone_number.nickname).first()
    if trash_count:
        counts['plastic'] = trash_count.plastic_count
        counts['vinyl'] = trash_count.vinyl_count
        counts['can'] = trash_count.can_count
        counts['general'] = trash_count.general_count

    return jsonify({
        'result': result,
        'score': total_score,
        'trash_counts': counts
    }), 200

@app.route('/get-trash-counts', methods=['GET'])
def get_trash_counts():
    # 가장 최근에 저장된 전화번호 찾기
    recent_phone_number = PhoneNumber.query.order_by(PhoneNumber.id.desc()).first()
    
    if not recent_phone_number:
        return jsonify({'message': 'No phone number found'}), 404

    # 해당 사용자의 TrashCount 찾기
    trash_count = TrashCount.query.filter_by(nickname=recent_phone_number.nickname).first()

    if not trash_count:
        return jsonify({'message': 'No trash counts found for this nickname'}), 404

    # 카운트 정보 반환
    return jsonify({
        'plastic_count': trash_count.plastic_count,
        'vinyl_count': trash_count.vinyl_count,
        'can_count': trash_count.can_count,
        'general_count': trash_count.general_count
    }), 200


@app.route('/get-latest-score', methods=['GET'])
def get_latest_score():
    # 최근에 들어온 전화번호를 찾음
    recent_phone_number = PhoneNumber.query.order_by(PhoneNumber.id.desc()).first()
    
    if not recent_phone_number:
        return jsonify({'message': 'No phone number found'}), 404

    # 해당 전화번호에 대한 비교 결과를 찾음
    recent_compare_result = CompareResult.query.filter_by(nickname=recent_phone_number.nickname).order_by(CompareResult.id.desc()).first()

    if not recent_compare_result:
        return jsonify({'message': 'No compare result found for this nickname'}), 404

    # 결과 반환
    return jsonify({
        'nickname': recent_compare_result.nickname,
        'result': recent_compare_result.result,
        'score': recent_compare_result.score
    }), 200


# 점수 순위 조회
@app.route('/rankings', methods=['GET'])
def get_rankings():
    # CompareResult에서 모든 결과를 가져와서 점수에 따라 정렬
    results = CompareResult.query.order_by(CompareResult.score.desc()).all()

    # 결과를 순위 형식으로 변환
    rankings = []
    for rank, result in enumerate(results, start=1):
        rankings.append({
            'rank': rank,
            'nickname': result.nickname,
            'score': result.score
        })
    return jsonify(rankings), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080)
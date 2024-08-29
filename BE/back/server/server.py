from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin   

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) 

#DB설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/viewinging' #DB URI
db = SQLAlchemy(app)    

#DB모델
class PhoneNumber(db.Model): #폰번호
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(13), unique=True)

    def __repr__(self):
        return f'<PhoneNumber {self.phone_number}>'

# class TrashKind(db.Model): #쓰레기종류
#     id = db.Column(db.Integer, primary_key=True)
#     trash_name = db.Column(db.String(30), unique=True)

#     def __repr__(self) -> str:
#         return super().__repr__()


@app.route('/submit-phone', methods=['POST'])
def submit_phone():
    data = request.get_json()
    phone_number = data.get('phoneNumber')

    if phone_number:
        if PhoneNumber.query.filter_by(phone_number=phone_number).first():
            return jsonify({'message': 'Phone number already exists'}), 400
        
        new_phone_number = PhoneNumber(phone_number=phone_number)
        db.session.add(new_phone_number)
        db.session.commit()
        
        return jsonify({'message': 'Phone number received'}), 200
    else:
        return jsonify({'message': 'Phone number is missing'}), 400

# @app.route('/trach-kind', methods=['POST'])


if __name__ == '__main__':
    with app.app_context():
        db.create_all() #DB 테이블 생성
    app.run(host='0.0.0.0', port=5000)
from multiprocessing.pool import ApplyResult
from flask import Flask, render_template, request, url_for, redirect, jsonify
import hashlib
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime
import jwt
from pymongo import MongoClient
import json
import requests
from bs4 import BeautifulSoup
with open("key.json", "r") as json_file:
    json_data = json.load(json_file)
secret_key = json_data['SECRET_KEY']
algorithm_key = json_data['ALGORITHM']

#MongoDB
uri = "mongodb+srv://cluster0.ctkbc.mongodb.net/myFirstDatabase?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = MongoClient(uri,tls=True, tlsCertificateKeyFile='X509-cert-6481087293358866486.pem')
db = client.account
db_video = client.data
db_record = client.record

# Flask
application = Flask(import_name = __name__)
application.config["JWT_SECRET_KEY"] = secret_key


# 메인화면
@application.route("/")
def open_mainPage(): return render_template('index.html')

# 회원가입페이지 이동
@application.route("/signup")
def open_SignUpPage(): return render_template('signup.html')

# 로그인 버튼
@application.route("/login", methods=['POST'])
def api_login():
	# 아이디, 비밀번호가 일치하는 경우
	user_id = request.form.get('userId', False)
	user_pw = request.form.get('userPw', False)
 
	# 비밀번호 hash암호화
	pw_hash = hashlib.sha256(user_pw.encode('utf-8')).hexdigest()
 
	#DB조회
	result = db.user.find_one({'id': user_id, 'pw': pw_hash})
	# 아이디, 비밀번호가 일치하는 경우
	if result is not None:
		payload = {
			'id': user_id,
			'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)  # 로그인 24시간 유지
		}
		token = jwt.encode(payload, secret_key, algorithm=algorithm_key)

		return jsonify({'result': 'success', 'token': token})
	# 아이디, 비밀번호가 일치하지 않는 경우
	else:
		return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 로그인한 후 홈으로 이동
@application.route('/result')
def home():
	token_receive = request.cookies.get('mytoken')
	try:
		payload = jwt.decode(token_receive, secret_key, algorithms=[algorithm_key])
		user_info = db.user.find_one({'id': payload['id']})
		return render_template('result.html', user=user_info)
	except jwt.ExpiredSignatureError:
		return redirect("http://localhost:5000/")
	except jwt.exceptions.DecodeError:
		return redirect("http://localhost:5000/")
		

# 운동완료 버튼
@application.route('/finish', methods=['POST'])
def record_finish():
	user_id_receive = request.form['user_id_give']
	video_id_receive = request.form['video_id_give']
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
	data = requests.get(video_id_receive, headers=headers)
	soup = BeautifulSoup(data.text, 'html.parser')
	hour = soup.select('#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > div.ytp-left-controls > div.ytp-time-display.notranslate > span:nth-child(2) > span.ytp-time-duration')

	db_record.record.insert_one({
		'user': user_id_receive,
		'video': video_id_receive,
		'timestamp': request.form['timestamp_give'],
		'tag': request.form['tag_give'],
		'hour': hour
		})
	return jsonify({'result': 'success', 'msg': '서버연결됨'})

# [회원가입 API]
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@application.route('/register', methods=['POST'])
def api_register():
    pw_receive = request.form['userPw_give'] 
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    db.user.insert_one({'name': request.form['userName_give'], 
                        'gender': request.form['userSex_give'], 
                        'id': request.form['userId_give'], 
                        'pw': pw_hash})
    return jsonify({
        'result': 'success', 
        'msg':'회원가입이 완료되었습니다.'
        }) 

@application.route('/search', methods=['POST'])
def video_search():
	time_receive = request.form['time_give']
	tool_receive = request.form['tool_give']
	body_receive = request.form['body_give']
	if time_receive != 'u':
		videos = list(db_video.video.find({'HT_TIME':time_receive, 'HT_TOOL':tool_receive, 'HT_BODY':body_receive}, {'_id':False}))
	else:
		videos = list(db_video.video.find({}, {'_id':False}))
     
	return jsonify({'result':'success', 'video_list':videos})


@application.route('/mypage')
def myPage():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, secret_key, algorithms=[algorithm_key])
        user_info = db.user.find_one({'id': payload['id']})
        return render_template('mypage.html', username=user_info['name'])
    except jwt.ExpiredSignatureError:
        return redirect("http://localhost:5000/")
    except jwt.exceptions.DecodeError:
        return redirect("http://localhost:5000/")


@application.route('/load', methods=['GET'])
def user_info():
	token_receive = request.cookies.get('mytoken')
	try:
		payload = jwt.decode(token_receive, secret_key, algorithms=[algorithm_key])
		user_info = db.user.find_one({'id': payload['id']},{'_id':False})
		# print(payload)
		return jsonify({'result':'success', 'user':user_info})
	except jwt.ExpiredSignatureError:
		return redirect("http://localhost:5000/")
	except jwt.exceptions.DecodeError:
		return redirect("http://localhost:5000/")

@application.route('/account', methods=['GET'])
def user_account():
	token_receive = request.cookies.get('mytoken')
	try:
		payload = jwt.decode(token_receive, secret_key, algorithms=[algorithm_key])
		user_info = db.user.find_one({'id': payload['id']})
		return render_template('account.html', user_info=user_info)
	except jwt.ExpiredSignatureError:
		return redirect("http://localhost:5000/")
	except jwt.exceptions.DecodeError:
		return redirect("http://localhost:5000/")

if __name__ == '__main__':
	application.run(host = '0.0.0.0',port = 5000, debug = True)
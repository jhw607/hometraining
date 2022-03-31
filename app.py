from http import client
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
import collections
with open("key.json", "r") as json_file:
    json_data = json.load(json_file)
secret_key = json_data['SECRET_KEY']
algorithm_key = json_data['ALGORITHM']

#MongoDB

# client = MongoClient('mongodb://jungle:jungle@13.125.166.86',27017)
client = MongoClient('mongodb://jungle:jungle@54.180.104.183',27017)
# client = MongoClient('localhost', 27017)
db = client.HomeTrainingDB
# HomeTrainingDB 안에 user, video, record 테이블이 있음!
# db_video = client.data
# db_record = client.record

# Flask
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = secret_key


# 메인화면
@app.route("/")
def open_mainPage(): return render_template('index.html')

# 회원가입페이지 이동
@app.route("/signup")
def open_SignUpPage(): return render_template('signup.html')

# 로그인 버튼

@app.route("/login", methods=['POST'])
def api_login():
	print('api_login()')
	# 아이디, 비밀번호가 일치하는 경우
	user_id = request.form['userId']
	user_pw = request.form['userPw']
 
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
		
		print(token)

		return jsonify({'result': 'success', 'token': token})
	# 아이디, 비밀번호가 일치하지 않는 경우
	else:
		return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 로그인한 후 홈으로 이동
@app.route('/result')
def home():
	print('home()')
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
@app.route('/finish', methods=['POST'])
def record_finish():
	user_id_receive = request.form['user_id_give']
	video_id_receive = request.form['video_id_give'].replace('embed/','watch?v=')
	print(video_id_receive)
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
	data = requests.get(video_id_receive, headers=headers)
	soup = BeautifulSoup(data.text, 'html.parser')
	hour = int(str(soup).split("u0026dur=")[1].split(".")[0])

	video_id = video_id_receive.split('watch?v=')[1]
	video = db.video.find_one({'url':video_id})
	print(video)
	tag = video['HT_TIME']+','+video['HT_TOOL']+','+video['HT_BODY']
	print(tag)
	db.record.insert_one({
		'user': user_id_receive,
		'video': video_id,
		'timestamp': request.form['timestamp_give'],
		'tag': tag,
		'hour': hour
		})
	return jsonify({'result': 'success', 'msg': '수고하셨습니다!'})

# [회원가입 API]
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/register', methods=['POST'])
def api_register():
	print('api_register()')
	name_receive = request.form['userName_give']
	id_receive = request.form['userId_give']
	pw_receive = request.form['userPw_give'] 
	gender_receive = request.form['userSex_give']
	count = len(list(db.user.find({'id': id_receive})))
	print(count)
	if name_receive == '' or id_receive == '' or pw_receive == '':
		return jsonify({'result': 'empty', 'msg':'빈칸을 채워주세요'})
	elif count > 0:
		return jsonify({'result': 'error', 'msg':'존재하는 아이디입니다.'})
	else:
		pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
		db.user.insert_one({'name': name_receive, 'gender': gender_receive, 'id': id_receive, 'pw': pw_hash})
		return jsonify({'result': 'success','msg':'회원가입이 완료되었습니다.'})

@app.route('/search', methods=['POST'])
def video_search():
	time_receive = request.form['time_give']
	tool_receive = request.form['tool_give']
	body_receive = request.form['body_give']
	if time_receive != 'u':
		videos = list(db.video.find({'HT_TIME':time_receive, 'HT_TOOL':tool_receive, 'HT_BODY':body_receive}, {'_id':False}))
	else:
		videos = list(db.video.find({}, {'_id':False}))
     
	return jsonify({'result':'success', 'video_list':videos})


@app.route('/mypage')
def myPage():
	token_receive = request.cookies.get('mytoken')
	try:
		payload = jwt.decode(token_receive, secret_key, algorithms=[algorithm_key])
		user_info = db.user.find_one({'id': payload['id']})
		testdata = db.record.find({'user': user_info['id']})
		temp = 0
		for i in testdata:
			temp += i['hour']
		recent = "http://www.youtube.com/embed/"+list(db.record.find({'user': user_info['id']}))[-1]['video']
		print(recent)
		l1 = list(db.record.find({'user': user_info['id']}))
		t1, t2, t3 = sorted(collections.Counter([i['tag'] for i in l1]).items(), reverse=True)[0][0].split(',')
		return render_template('mypage.html', username=user_info['name'], total_hour = temp//60, recentvideo = recent, t1=t1, t2=t2, t3=t3)
	except jwt.ExpiredSignatureError:
		return redirect("http://localhost:5000/")
	except jwt.exceptions.DecodeError:
		return redirect("http://localhost:5000/")

@app.route('/load', methods=['GET'])
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

@app.route('/account', methods=['GET'])
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

@app.route('/edit', methods=['POST'])
def account_edit():
	id_receive = request.form['userId_give']
	name_receive = request.form['editName_give']
	pw_receive = request.form['editPw_give']
	db.user.update_one({'id':id_receive},{'$set':{'name':name_receive, 'pw':pw_receive}})
	return jsonify({'result':'success', 'msg':'수정완료!'})



if __name__ == '__main__':
	app.run(host = '0.0.0.0',port = 5000, debug = True)
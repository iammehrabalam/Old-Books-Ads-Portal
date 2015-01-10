from flask import json,Flask,url_for,session,request,render_template,jsonify,g,Response,redirect,abort,flash,send_from_directory
import sqlite3
from werkzeug import generate_password_hash,check_password_hash,secure_filename
import datetime
from hashlib import md5
import random
from PIL import Image
import os
import s_email
import math
import re
app=Flask(__name__)


DATABASE='your sqlite database name'
SECRET_KEY='secret key'
UPLOAD_FOLDER="/home/oldbooks/mysite/static/uploads/"
UPLOADT_FOLDER="/home/oldbooks/mysite/static/uploadst/"
#RESIZE_ROOT=="static\\uploads\\"
ALLOWED_EXTENSIONS=set(['png','jpg','jpeg','gif','tif','pdf'])
PER_PAGE=12
page=0
MAX_PAGE=0
app.config.from_object(__name__)
app.config.from_envvar('FIRST_SETTING',silent=True)
oauth = OAuth(app)

def get_db():
	if not hasattr(g,'conn'):
		g.conn=sqlite3.connect(app.config['DATABASE'])
		g.conn.row_factory=sqlite3.Row
	return g.conn
def query_db(query,args=()):
	cur=get_db().execute(query,args)
	record=cur.fetchall()
	if record:
		return record
	else:
		return None
def imgthumb(p):
	f=p
	p=os.path.join(app.config['UPLOAD_FOLDER']+p)
	image=Image.open(p)
	image.thumbnail((150,150),Image.ANTIALIAS)
	image.save(app.config['UPLOADT_FOLDER']+f)

def img(p):
	p=os.path.join(app.config['UPLOAD_FOLDER']+p)
	image=Image.open(p)
	image.thumbnail((500,500),Image.ANTIALIAS)
	image.save(p)

def first_send(email,code):
		if s_email.mail(email,"mail confimation code  ..\n\n",code)=='sent':
		    	print('sent')
		else:
		    	print('error')
		return
def check_extention_file(filename):
	if '.'in filename:
		extn=filename.rsplit('.',1)[1];
		if extn in app.config['ALLOWED_EXTENSIONS']:
			return extn
		else:
			return None
	return None

@app.teardown_request
def close_db(exception):
	"""close database at the end of request"""
	if getattr(g,'conn',None):
		g.conn.close()

@app.before_request
def before_request():
	ipp=(request.headers.get('X-Real-IP'))
	#ipp=request.remote_addr
	if ipp:
		record=query_db('select * from visit where ip = ?',[str(ipp)])
		if not record:
			date=datetime.datetime.now()
			cdate=date.strftime("%d-%m-%Y @ %H:%M:%S")
			db=get_db()
			db.execute('insert into visit (ip,datetime) values(?,?)',[str(ipp),str(cdate)])
			db.commit()
	if 'username' in session:
		try:
			g.user = query_db('select * from profile where username = ?',[session['username']])
			if g.user:
			    g.user=g.user[0]
		except:
			pass


@app.route('/sdmail/',methods=['POST'])
def sdmail():
	mg_j=request.get_json()
	book_head="Title: "+str(mg_j['se_n'])+'\n'+"Author: "+str(mg_j['se_a'])+'\n'+"message by viewer\n\n"+mg_j['mg']
	if s_email.mail(mg_j['se_id'],"Mail from ",book_head)=='sent':
		return jsonify({'result':'sent'})#change it plzzzz
	else:
		return jsonify({'result':'fail'})

@app.route('/sdmail_foruser/',methods=['POST'])
def sdmail_foruser():
	mg_j=request.get_json()
	if s_email.mail(mg_j['se_id'],mg_j['se_s'],mg_j['mg'])=='sent':
		return jsonify({'result':'sent'})#change it plzzzz
	else:
		return jsonify({'result':'fail'})

#@app.route('/search')
#def search():
#	return render_template('search.html',page=page,MAX_PAGE=MAX_PAGE)

@app.route('/logout')
def logout():
	if 'username' in session:
		session.pop('username', None)
	return redirect(url_for('home'))


#@app.route('/signup')
#def signup():
#	if 'username' in session:
#		return render_template('next.html')
#	return render_template('signup.html')

@app.route('/delt/<int:id>')
def delt(id):
	if 'username' in session:
		record=query_db('select pic_name from posts where post_id = ?',[str(id)])
		if record:
			try:
				os.remove(os.getcwd()+'/static/uploads/'+record[0][0])
				os.remove(os.getcwd()+'/static/uploadst/'+record[0][0])
			except:
				pass
		db=get_db()
		db.execute("delete from posts where post_id="+str(id))
		db.commit()
		return redirect(url_for('profile'))
	return render_template('pagenotaval.html')
@app.route('/sold/<int:id>')
def sold(id):
	if 'username' in session:
		record=query_db('select pic_name from posts where post_id = ?',[str(id)])
		if record:
			try:
				os.remove(os.getcwd()+'/static/uploads/'+record[0][0])
				#os.remove(os.getcwd()+'/static/uploadst/'+record[0][0])
			except:
				pass
		db=get_db()
		db.execute("update posts set status = ? where post_id = ?",[1,id])
		db.commit()
		return redirect(url_for('profile'))
	return render_template('pagenotaval.html')
@app.route('/a_not_4u/<tab>/')
@app.route('/a_not_4u/<tab>/<int:page>/')
@app.route('/a_not_4u/')
def a_not_4u(page=1,tab=None):
	if 'username' in session and session['username']=='admin@mehrab@jamia':
		po_ccc=query_db('select count (*) from posts',[])
		v_ccc=query_db('select count (*) from visit',[])
		u_ccc=query_db('select count (*) from users',[])
		f_ccc=query_db('select count (*) from feedback',[])
		c_ccc=query_db('select count (*) from comments',[])
		pro_ccc=query_db('select count (*) from profile',[])
		for i in po_ccc:
					po_c=i[0]
					break
		for i in v_ccc:
					v_c=i[0]
					break
		for i in f_ccc:
					f_c=i[0]
					break
		for i in c_ccc:
					c_c=i[0]
					break
		for i in pro_ccc:
					pro_c=i[0]
					break
		for i in u_ccc:
					u_c=i[0]
					break
		if tab=='p':
			p_count=query_db('select count (*) from posts',[])
			p_record=query_db('select * from posts order by post_id desc limit ? offset ?',[str(PER_PAGE),str((page-1)*PER_PAGE)])
			if p_record:
				for i in p_count:
					NUM_REC=i[0]
					break
				MAX_PAGE=math.ceil(NUM_REC/PER_PAGE)
			return render_template('a_view.html',p_record=p_record,page=page,MAX_PAGE=MAX_PAGE,po_c=po_c,v_c=v_c,f_c=f_c,c_c=c_c,pro_c=pro_c,u_c=u_c)
		elif tab=='pro':
			pro_count=query_db('select count (*) from profile',[])
			pro_record=query_db('select * from profile order by datetime desc limit ? offset ?',[str(PER_PAGE),str((page-1)*PER_PAGE)])
			if pro_record:
				for i in pro_count:
					NUM_REC=i[0]
					print(NUM_REC)
					break
				MAX_PAGE=math.ceil(NUM_REC/PER_PAGE)
			return render_template('a_view.html',pro_record=pro_record,pro_count=pro_count,page=page,MAX_PAGE=MAX_PAGE,po_c=po_c,v_c=v_c,f_c=f_c,c_c=c_c,pro_c=pro_c,u_c=u_c)
		elif tab=='f':
			f_count=query_db('select count (*) from feedback',[])
			f_record=query_db('select * from feedback where status = ? order by fed_id desc limit ? offset ?',[str(0),str(PER_PAGE),str((page-1)*PER_PAGE)])
			if f_record:
				for i in f_count:
					NUM_REC=i[0]
					break
				MAX_PAGE=math.ceil(NUM_REC/PER_PAGE)
			return render_template('a_view.html',f_record=f_record,page=page,MAX_PAGE=MAX_PAGE,po_c=po_c,v_c=v_c,f_c=f_c,c_c=c_c,pro_c=pro_c,u_c=u_c)
		elif tab=='c':
			c_count=query_db('select count (*) from comments',[])
			c_record=query_db('select * from comments where status = ? order by comment_id desc limit ? offset ?',[str(0),str(PER_PAGE),str((page-1)*PER_PAGE)])
			c1_record=query_db('select * from comments where status = ? order by comment_id desc limit ? offset ?',[str(1),str(PER_PAGE),str((page-1)*PER_PAGE)])
			if c_record or c1_record:
				for i in c_count:
					NUM_REC=i[0]
					print(NUM_REC)
					print(c1_record)
					break
				MAX_PAGE=math.ceil(NUM_REC/PER_PAGE)
			return render_template('a_view.html',c_record=c_record,c1_record=c1_record,page=page,MAX_PAGE=MAX_PAGE,po_c=po_c,v_c=v_c,f_c=f_c,c_c=c_c,pro_c=pro_c,u_c=u_c)
		elif tab=='u':
			pass
		elif tab=='v':
			pass
		else:
			return render_template('a_view.html',po_c=po_c,v_c=v_c,f_c=f_c,c_c=c_c,pro_c=pro_c,u_c=u_c)
	return render_template('pagenotaval.html')

@app.route('/profile/')
def profile():
	try:
		if 'username' in session:
			if session['username']=='admin name':
				return redirect(url_for('a_not_4u'))
			else:
				record=query_db("select * from posts where username = ? order by datetime desc",[session['username']])
				if record:
					return render_template('next.html',record=record)
				else:
					return render_template('next.html')
	except:
		pass

	return redirect(url_for('home'))

@app.route('/feedback/',methods=['POST'])
def feedback():
	date=datetime.datetime.now()
	cdate=date.strftime("%d-%m-%Y @ %H:%M:%S")
	req=request.get_json()
	db=get_db()
	db.execute('insert into feedback (name,email,text,datetime) values(?,?,?,?)',[req['n'],req['e'],req['d'],str(cdate)])
	db.commit()
	return jsonify({'result':'1234'})

#@app.route('/login',methods=['GET'])
@app.route('/login/',methods=['POST'])
def login():
		req = request.get_json()
		ck=query_db("select * from users where username=?",[req['u']])
		if ck:
			if check_password_hash(ck[0]['password'],req['p']):
				session['username']=req['u']
				return jsonify({'result':'1234'})
			else:
				return jsonify({'result':'noo'})
		else:
				return jsonify({'result':'noo'})


@app.route('/get_email_username/',methods=['POST'])
def get_email_username():
	j_jqury=request.get_json()
	u_name=query_db('select * from users where username = ?',[j_jqury['u']])
	e_email=query_db('select * from profile where email = ?',[j_jqury['e']])
	if u_name is not  None and e_email is not  None:
		return jsonify({'result':'b_exist'})
	elif u_name is not  None:
		return jsonify({'result':'u_exist'})
	elif e_email is not  None:
		return jsonify({'result':'e_exist'})
	else:
		return jsonify({'result':'1234'})

@app.route('/register/',methods=['POST'])
def register():
	code=(random.randint(1000,10000000))
	j_jqury=request.get_json()
	date=datetime.datetime.now()
	cdate=date.strftime("%d-%m-%Y @ %H:%M:%S")
	print(code)
	code_a="Your confirmation code is "+str(code)
	print(code_a)
	if s_email.mail(j_jqury['e'],"mail confimation code from oldbooks.pythonanywhere.com ..",code_a)=='sent':
		    pass
	try:
		db=get_db()
		db.execute('insert into profile (name,email,username,datetime,email_conf) values(?,?,?,?,?)',[j_jqury['n'],j_jqury['e'],j_jqury['u'],str(cdate),code])
		db.execute('insert into users (username,password) values(?,?)',[j_jqury['u'],generate_password_hash(j_jqury['p'])])
		db.commit()
		session['username']=j_jqury['u']
		return jsonify({'result':'1234'})
	except:
		return jsonify({'result':'not'})

@app.route('/uploadform/')
def uploadform():
	if 'username' in session:
		return render_template('uploadform.html')
	return redirect(url_for('home'))

@app.route('/uploaddata/',methods=['POST','GET'])
def uploaddata():
	temp=['a','b','f','q','t','2','_','-','w','t','i','c','o','z']
	if request.method=="POST":
			file=request.files['file']
			bk=request.form['nuppp1']
			aut=request.form['nuppp2']
			cost=request.form['nuppp3']
			typ=request.form['nuppp4']
			des=request.form['nuppp6']
			mob=request.form['nuppp5']
			publ=request.form['nuppp21']
			loca=request.form['nuppp41']
			sbk=(re.sub('[ .,\-\@\_\&()]','',bk)).lower()
			saut=(re.sub('[ .,\-\@\_\&()]','',aut)).lower()
			spubl=(re.sub('[ .,\-\@\_\&()]','',publ)).lower()
			date=datetime.datetime.now()
			cdate=date.strftime("%d-%m-%Y @ %H:%M:%S")
			if file :
				extn=check_extention_file(file.filename)
				if extn!=None:
						filename=secure_filename(file.filename)
						filename=md5((filename+random.choice(temp)+str(random.randint(0,100000))).encode('utf-8')).hexdigest()+'.'+extn
						db=get_db()
						db.execute("insert into posts (username,pic_name,title,author,description,cost,type,mobile,datetime,pub,city,stitle,sauthor,spub) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",\
							[session['username'],filename,bk,aut,des,cost,typ,mob,cdate,publ,loca,sbk,saut,spubl])
						db.commit()
						file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
						img(filename)
						imgthumb(filename)
						succe="File uploaded successfully"
						return render_template('uploadform.html',succe=succe)
			error="Sorry,File format not allowed"
			return render_template('uploadform.html',error=error)
	return redirect(url_for('home'))



@app.route('/instantsearch/',methods=['POST'])
def instantsearch():
	data=request.get_json()
	d2=re.sub('[ .,\-\@\_\&()]','',data['d'])
	if data['b']=='title':
		count_rec=query_db('select count (*) from posts where stitle like ? and city = ?',['%'+d2+'%',str(data['l'])])
		for i in count_rec:
			REC=i[0]
			break
	elif data['b']=='author':
		count_rec=query_db('select count (*) from posts where sauthor like ? and city = ?',['%'+d2+'%',str(data['l'])])
		for i in count_rec:
			REC=i[0]
			break
	elif data['b']=='pub':
		count_rec=query_db('select count (*) from posts where spub like ? and city = ?',['%'+d2+'%',str(data['l'])])
		for i in count_rec:
			REC=i[0]
			break
	return jsonify({'result':REC})
@app.route('/searchbox/')
@app.route('/searchbox/<int:page>/')
@app.route('/searchbox/<data>/<by>/<inn>/')
@app.route('/searchbox/<data>/<by>/<inn>/<int:page>/')
def searchbox(data=None,by=None,page=1,inn='darbhanga'):
	if data:
		d2=re.sub('[ .,\-\@\_\&()]','',data)
	if (data is None or by is None) and (by is None or data is None):
			cout=query_db("select count (*) from posts")
			recent=query_db('select * from posts  order by post_id desc ,status asc limit ? offset ?',[PER_PAGE,str((page-1)*PER_PAGE)])#this also
			if recent:
				for i in cout:
					NUM_REC=i[0]
					break
				MAX_PAGE=math.ceil(NUM_REC/PER_PAGE)
				if MAX_PAGE > 10:
					MAX_PAGE=10
				return render_template('search.html',recent=recent,MAX_PAGE=MAX_PAGE,NUM_REC=NUM_REC,page=page)#this also
			else:
				return render_template('search.html',rec_not=1)
	if by=='title':
		count_rec=query_db('select count (*) from posts where stitle like ? and city = ?',['%'+d2+'%',str(inn)])
		record=query_db('select * from posts  where stitle like ? and city = ? order by title limit ? offset ?',\
			['%'+d2+'%',str(inn),str(PER_PAGE),str((page-1)*PER_PAGE)])
	elif by=='author':
		count_rec=query_db('select count (*) from posts where sauthor like ? and city = ?',['%'+d2+'%',str(inn)])
		record=query_db('select * from posts where sauthor like ? and city = ? order by author limit ? offset ?',\
			['%'+d2+'%',str(inn),str(PER_PAGE),str((page-1)*PER_PAGE)])
	elif by=='pub':
		count_rec=query_db('select count (*) from posts where spub like ? and city = ?',['%'+d2+'%',str(inn)])
		record=query_db('select * from posts where spub like ? and city = ? order by pub limit ? offset ?',\
			['%'+d2+'%',str(inn),str(PER_PAGE),str((page-1)*PER_PAGE)])
	if record:
		for i in count_rec:
				NUM_REC=i[0]
				break
		MAX_PAGE=math.ceil(NUM_REC/PER_PAGE)
		return render_template('search.html',data=data,by=by,page=page,inn=inn,MAX_PAGE=MAX_PAGE,record=record,NUM_REC=NUM_REC)
	else:
		return render_template('search.html',rec=by,MAX_PAGE=0,page=0)
@app.route('/searchdata/',methods=['POST'])
def searchdata():
	return redirect(url_for('searchbox',data=request.form['keywords'],by=request.form['tty'],inn=request.form['tty1']))

@app.route('/uploads/<filename>/')
def uploaded_file(filename):
	hel=send_from_directory(app.config['UPLOAD_FOLDER'],filename)
	return hel
@app.route('/uploadst/<filename>/')
def uploaded_filet(filename):
	hel=send_from_directory(app.config['UPLOADT_FOLDER'],filename)
	return hel
@app.route('/showdetail/<int:post_id>/')
def showdetail(post_id):
	record=query_db("select * from posts where post_id = ?",[str(post_id)])
	if record:
		info=query_db("select * from profile where username = ?",[str(record[0][1])])
		return render_template('showdetail.html',record=record[0],info=info[0])
	return render_template('search.html')
@app.route('/comment_submit/',methods=['POST'])
def comment_submit():
	try:
		date=datetime.datetime.now()
		cdate=date.strftime("%d-%m-%Y @ %H:%M:%S")
		com_data=request.get_json()
		db=get_db()
		db.execute('insert into comments (name,email,text,datetime) values(?,?,?,?)',[str(com_data['n_n']),str(com_data['e_e']),str(com_data['t_t']),str(cdate)])
		db.commit()
		return jsonify({'result':'1234'})
	except:
		return jsonify({'result':'not'})
@app.route('/feed_comment_verify/<int:cid>/<int:actn>/<int:page>/<tab>/')
def feed_comment_verify(cid,actn,tab,page):
	if 'username' in session and session['username']=='admin@mehrab@jamia':
		if actn==0:
			db=get_db()
			db.execute("delete from comments where comment_id="+str(cid))
			db.commit()
		elif actn==1:
			db=get_db()
			db.execute("update comments set status = ? where comment_id = ?",[1,cid])
			db.commit()
		elif actn==10:
			db=get_db()
			db.execute("delete from feedback where fed_id="+str(cid))
			db.commit()
		return redirect(url_for('a_not_4u',page=page,tab=tab))
	return render_template('pagenotaval.html')

@app.route('/checking.../',methods=['POST'])
def checking():
	chek=request.get_json()
	record=query_db('select * from profile where username = ?',[str(chek['u'])])
	if record:
		for i in record:
			if(i[1]==chek['e'] and i[0]==chek['n']):
				temp=['a12','31b','68f','q62','55t','2s','a0','h3','1w','9t','i4','c7','2o','9z','a01','2h3','31w','59t','3i4','6c7','2o7']
				code=random.choice(temp)+random.choice(temp)+random.choice(temp)
				db=get_db()
				db.execute('update users set password = ? where username = ?',[generate_password_hash(str(code)),str(chek['u'])])
				db.commit()
				print(code)
				code="\n\n..Your temp. password is "+str(code)+" \n\n..Plesae change your password"
				s_email.mail(chek['e'],"mail from oldbooks.pythonanywhere.com ..\n\n",code)
				return jsonify({'result':'1234','username':chek['u']})
			else:
				return jsonify({'result':'not'})
	return jsonify({'result':'not'})
@app.route('/setting.../',methods=['POST'])
def setting():
	chek=request.get_json()
	try:
		db=get_db()
		db.execute('update users set password = ? where username = ?',[generate_password_hash(chek['p']),str(chek['u'])])
		db.commit()
		return jsonify({'result':'1234'})
	except:
	    return jsonify({'result':'not'})

@app.route('/confirmation/<v>/')
@app.route('/confirmation/<v>/<m>/')
def confirmation(v,m=None):
	if v=='verify user':
		return render_template('confirm.html',v=v)
	elif v=='set password':
		return render_template('confirm.html',v=v,m=m)
	else:
		return render_template('pagenotaval.html')
@app.route('/faq/')
def faq():
	return render_template('faq.html')
@app.route('/terms/')
def terms():
	return render_template('terms.html')

@app.route('/privacypolicy/')
def privacypolicy():
	return render_template('privacypolicy.html')

@app.route('/contact/')
def contact():
	return render_template('contact.html')

@app.route('/check_code/',methods=['POST'])
def check_code():
	g_g=request.get_json()
	record=query_db('select * from profile where username = ?',[g_g['u']])
	if record:
		if str(record[0][5])==str(g_g['k']):
			db=get_db()
			db.execute('update profile set e_conf = ? where username = ? ',[1,g_g['u']])
			db.commit()
			return jsonify({'result':'1234'})
	return jsonify({'result':'not'})

@app.route('/comments/<int:page>/')
def comments(page=1):
	MAX_PAGE=0
	count_rec=query_db('select count(*) from comments where status = ?',[1])
	if count_rec:
		for i in count_rec:
			NUM_REC=i[0]
			break
		MAX_PAGE=math.ceil(NUM_REC/15)
	record=query_db('select * from comments where status = ? order by comment_id desc limit ? offset ?',[1,15,str((page-1)*15)])
	return render_template('comments.html',record=record,page=page,MAX_PAGE=MAX_PAGE)

@app.route('/send_code/',methods=['POST'])
def send_code():
	g_g=request.get_json()
	code=(random.randint(1000,10000000))
	try:
		db=get_db()
		db.execute('update profile set email_conf = ? where username = ?',[code,g_g['u']])
		db.commit()
	except:
		pass
	if g.user[4]==0:
		code_a="Your confirmation code is "+str(code)
		if s_email.mail(g.user[1],"mail confimation code from oldbooks.pythonanywhere.com ..\n\n",code_a)=='sent':
				return jsonify({'result':'1234'})
		else:
				return jsonify({'result':'not'})
@app.route('/papers/')
@app.route('/papers/<typ>/')
def paper(typ=None):
	if typ is None:
		return render_template('paper.html')
	else:
		return render_template('paper.html',typ=typ)
@app.route('/sitemap/')
def sitemap():
    return render_template('sitemap.html')

@app.route('/')
def home():
	record=query_db('select * from comments where status = ? order by comment_id desc limit ?',[1,3])
	return render_template('home.html',record=record)

@app.errorhandler(405)
def page_not_found(error):
	return render_template('pagenotaval.html'), 404

@app.errorhandler(404)
def page_not_found(error):
		return render_template('pagenotaval.html'), 404

if __name__ == '__main__':
	app.run(debug=True)

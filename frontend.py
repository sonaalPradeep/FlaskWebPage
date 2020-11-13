from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from forms import LoginForm

import requests
import base64

from exif import Image

import json
import glob
import os
import random

app = Flask(__name__)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

class WebStatus():
	LOGIN_STATUS = None
	POSTS = None
	GUEST_USRNAME = None
	ATTRIBUTES_SET = []

status = WebStatus()

@app.route("/", methods=['GET'])
def offline():
	status.LOGIN_STATUS = False
	return render_template('offline.html')

@app.route("/home", methods=['GET'])
def home():
	if status.LOGIN_STATUS == True:
		random.shuffle(status.ATTRIBUTES_SET)
		return render_template('home.html', attributes = status.ATTRIBUTES_SET[:min(len(status.ATTRIBUTES_SET), 10)])
	else:
		return redirect(url_for('offline'))
	

@app.route("/home", methods=['POST'])
def home2():
	data=request.form
	payload = dict(data.lists())
	num_of_constrs = -1

	for key, value in payload.items():
		if key == 'member':
			num_of_constrs = int(value[0])
			break

	list_of_attrs = [None] * num_of_constrs
	list_of_relops = [None] * num_of_constrs
	list_of_constrs = [None] * num_of_constrs

	for key, value in payload.items():
		if key == 'member':
			continue

		if key[0] == 'a':
			list_of_attrs[int(key.lstrip('attribute'))] = value[0]
		elif key[0] == 'r':
			list_of_relops[int(key.lstrip('relop'))] = value[0]
		else:
			list_of_constrs[int(key.lstrip('constraint'))] = value[0]


	ops = {'==' : '$eq', '!=' : '$ne', '<' : '$lt', '>' : '$gt', '<=' : '$lte', '>=' : '$gte'}
	list_of_payloads = []
	payload={}

	for ind in range(num_of_constrs):
		curr_attr = list_of_attrs[ind]
		curr_relop = list_of_relops[ind]
		curr_constr = list_of_constrs[ind]

		try:
			if curr_relop == "^":
				list_of_payloads.append({"metadata."+ curr_attr : {"$regex":"^"+curr_constr, "$options":"i"}})
			elif curr_relop == "$":
				list_of_payloads.append({"metadata."+ curr_attr : {"$regex":curr_constr+"$", "$options":"i"}})
			elif curr_constr.isdigit():
				list_of_payloads.append({"metadata."+ curr_attr : {ops[curr_relop]:int(curr_constr)}})
			elif "." in curr_constr:
				list_of_payloads.append({"metadata."+ curr_attr : {ops[curr_relop]:float(curr_constr)}})
			else:
				list_of_payloads.append({"metadata."+ curr_attr : {ops[curr_relop]:curr_constr}})
		except:
			pass


	for dict_pair in list_of_payloads:
		key, value = list(dict_pair.keys())[0], list(dict_pair.values())[0]
		payload[key] = value


	r=requests.post("http://localhost:5000/query_records",json=payload)
	r=r.json()

	status.POSTS = []
	tmp_download_imgs = glob.glob('./tmp_uploads/*')
	if tmp_download_imgs != []:
		for img_loc in tmp_download_imgs:
			os.remove(img_loc)

	tmp_download_imgs = glob.glob('./static/tmp_downloads/*')
	if tmp_download_imgs != []:
		for img_loc in tmp_download_imgs:
			os.remove(img_loc)

	if r == {'error': 'data not found'}:
		flash("No pictures found", "warning")
	else:
		for ind, img in enumerate(r):    
			tmp_post = {}
			new_meta = {}

			for key, value in img['metadata'].items():
				if key[0] == "_" or len(str(value)) > 50 or key in ['user_comment', "MakerNote"]:
					continue
				if type(value) == str:
					new_meta[key] = value.strip()
				else:
					new_meta[key] = value

			tmp_post["metadata"] = new_meta
			tmp_post["title"] = img["name"]
			tmp_post["author"] = status.GUEST_USRNAME
			tmp_post["date_posted"] = img["time"]
			tmp_post["content"] = "temp"+str(ind)+".jpg"
			
			status.POSTS.append(tmp_post)

			with open("static/tmp_downloads/"+"temp"+str(ind)+".jpg",'wb') as t:
				te=base64.b64decode(img['image'])
				t.write(te)

	print(status.POSTS)
	random.shuffle(status.ATTRIBUTES_SET)
	return render_template('home.html', posts = status.POSTS, attributes = status.ATTRIBUTES_SET[:min(len(status.ATTRIBUTES_SET), 10)])


@app.route("/about")
def about():
	if status.LOGIN_STATUS == False:
		return redirect(url_for('offline'))
	return render_template('about.html', title = "About")

@app.route("/about_off")
def about2():
    return render_template('about_off.html', title = "About")

@app.route("/upload", methods=['POST'])
def upload():
	payload={}
	file = request.files['file']
	file.save("tmp_uploads/" + file.filename)
	fname=file.filename.split('.')
	if fname[-1].lower()!="jpg":
		flash("Incompatibe image format. Please use JPG", "warning")
	else:
		payload['name']=file.filename
		if 'file' in request.files:
			with open("tmp_uploads/" + file.filename,'rb') as imgfile:
				image_enc=base64.b64encode(imgfile.read())
				imgfile.seek(0)

				myimage=Image(imgfile)
				if myimage.has_exif==False:
					flash("Image does not have exif metadata")
				else:
					payload['image']=str(image_enc)[2:-1]
					payload['metadata']={}
					for attr in dir(myimage):
						try:
							value=myimage.get(attr)
							if value!=None or value!=null or (type(value) not in [float,int,str]):
								payload['metadata'][attr]=myimage.get(attr)
								if type(payload['metadata'][attr])==str:
									payload['metadata'][attr]=payload['metadata'][attr].strip()

								if attr not in status.ATTRIBUTES_SET and (attr[0] != "_" and attr not in ['user_comment', "MakerNote"]) and str(type(value)) in ["<class 'float'>", "<class 'int'>", "float", "int"]:
									status.ATTRIBUTES_SET.append(attr)

						except:
							continue

					r=requests.post("http://localhost:5000/create_record",json=payload)
	return redirect(url_for('home'))

@app.route("/upload", methods=['GET'])
def upload2():
	if status.LOGIN_STATUS == False:
		return redirect(url_for('offline'))

	random.shuffle(status.ATTRIBUTES_SET)
	return render_template('upload.html', title = "Submit", attributes = status.ATTRIBUTES_SET[:min(len(status.ATTRIBUTES_SET), 10)])

@app.route("/login", methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == 'guest' and form.password.data == 'guest':
            flash("Logged in Succesfully", 'success')
            status.GUEST_USRNAME = form.username.data
            status.LOGIN_STATUS = True
            return redirect(url_for('about'))
        else:
            flash("Login Unsuccesful for : {}".format(form.username.data), 'warning')
            return redirect(url_for('offline'))

    return render_template('login.html', title = "Login", form = form)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug = False)

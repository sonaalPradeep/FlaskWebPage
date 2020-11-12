import json
from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine
import datetime

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'images',
    'host': 'mongodb://mongodb:27017/imagedb',
    'port': 27017
}
db = MongoEngine()
db.init_app(app)

class User(db.Document):
    name = db.StringField()
    metadata = db.DictField()
    image = db.StringField()
    time = db.StringField()
    def to_json(self):
        return {"name": self.name,
                "image": self.image,
                "metadata": self.metadata,
                "time": self.time}

@app.route('/query_records', methods=['GET','POST'])
def query_records():
    query = json.loads(request.data)
    #print(query)
    user = User.objects(__raw__=query)
    if not user:
        return jsonify({'error': 'data not found'})
    else:
        return jsonify(user)

@app.route('/create_record', methods=['PUT','POST','GET'])
def create_record():
    record = json.loads(request.data)
    user = User(name=record['name'],
                image=record['image'],
                metadata=record['metadata'],
                time = str(datetime.datetime.now()).split('.')[0])
    user.save()
    return jsonify(user.to_json())

if __name__ == "__main__":
    app.run(debug=True)
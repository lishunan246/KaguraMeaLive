from KaguraMeaLive import app,db
from .schema import Channel

@app.route('/websub')
def websub():
    a = Channel(name="sdf",id="sdfd")
    db.session.add(a)
    db.session.commit()
    return 's'

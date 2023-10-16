from app.extensions import db

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=True)
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=False)

    def __init__(self, url, folder_id):
        self.url = url
        self.folder_id = folder_id

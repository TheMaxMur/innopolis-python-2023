from app import db


class Phone(db.Model):
    phone_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32))
    os = db.Column(db.String(32))
    cpu = db.Column(db.String(128))
    ram = db.Column(db.Integer)
    disk = db.Column(db.Integer)

    def to_dict(self):
        return {
            "phone_id": self.phone_id,
            "name": self.name,
            "os": self.os,
            "cpu": self.cpu,
            "ram": self.ram,
            "disk": self.disk,
        }

import json

from google.appengine.ext import db


class Assets(db.Model):
    json = db.TextProperty(required=True)

    @staticmethod
    def update_assets(assets):
        db.delete(Assets.all(keys_only=True))
        db.put(Assets(json=json.dumps(assets)))

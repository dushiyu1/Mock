from .database import db
from sqlalchemy.dialects.mysql import JSON
from datetime import datetime


class MockRoute(db.Model):
    __tablename__ = 'mock_routes'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(500), nullable=False, unique=True)
    methods = db.Column(db.String(200), nullable=False, default='GET')
    response = db.Column(JSON, nullable=False)
    status_code = db.Column(db.Integer, nullable=False, default=200)
    headers = db.Column(JSON, nullable=False, default=dict)
    delay = db.Column(db.Float, nullable=False, default=0)
    description = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'path': self.path,
            'methods': self.methods.split(','),
            'response': self.response,
            'status_code': self.status_code,
            'headers': self.headers,
            'delay': self.delay,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
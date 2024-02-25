from flask import Flask
from .routes import hue_blueprint

def create_module(app: Flask, **kwargs):
    app.register_blueprint(hue_blueprint, url_prefix='/philips_hue')
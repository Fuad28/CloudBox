from flask import Flask, render_template, Blueprint, request

core= Blueprint('core', __name__, url_prefix='/api/v1/core/')

@core.route("/")
@core.route("/home")
def home():
    pass
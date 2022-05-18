from flask import Flask, render_template, Blueprint, request

main= Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')
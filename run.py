from flask import url_for
from main import create_app

if __name__=='__main__':
    app = create_app()
    app.run()
from flask_frozen import Freezer
from myapp import app                #依照第一步驟的檔名來決定

freezer = Freezer(app)

if __name__ == '__main__':
    freezer.freeze()

from flask import Flask, send_file
from os import listdir
from random import randint
from tkinter.filedialog import askdirectory

app = Flask(__name__)

imgs_path = askdirectory(title='请选择本地图片文件夹路径')
imgs = listdir(imgs_path)
imgs_sum = len(imgs)


<<<<<<< HEAD
=======
@app.route('/', methods=['GET'])
def img_test():
    return 'hello world!'


>>>>>>> dd0a01c (2023年1月2日 发布到Github 版本3.0)
@app.route('/Img_Test', methods=['GET'])
def img_test():
    img_name = imgs[randint(0, imgs_sum)]
    img_path = imgs_path + img_name
    print(img_path)
    return send_file(img_path)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5050)

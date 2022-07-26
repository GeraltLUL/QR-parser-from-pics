from flask import Flask, render_template, request, send_from_directory
import requests
import pandas as pd
import os
from matplotlib import pyplot as plt
import skimage
from skimage import util, exposure, measure, feature
from scipy import ndimage as ndi
import numpy as np
import cv2

app = Flask(__name__)
app.secret_key = '5239i1i5of5jd6sij9290jd#@'
app.config['UPLOAD_IMAGE_FOLDER'] = './static/data/img'
app.config['UPLOAD_XLS_FOLDER'] = './static/data/xls'


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/static/xls/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    xls = os.path.join(app.root_path, app.config['UPLOAD_XLS_FOLDER'])
    xls = f"{xls}".replace('.', '')
    filename = str(filename).split(':')[1]

    return send_from_directory(directory=xls, path=xls + filename, filename=filename)


@app.route('/sendData', methods=['GET', 'POST'])
def sendData():
    if request.method == 'POST':
        pics = request.files.getlist('pictures')
        for pic in pics:
            if pic is not None and ('.jpg' in pic.filename or '.png' in pic.filename):
                picPath = os.path.join(app.config['UPLOAD_IMAGE_FOLDER'], pic.filename)
                pic.save(picPath)

                try:
                    qrCode = qrReader(picPath)

                    if qrCode is None or qrCode == '':
                        newImg = normalizeImg(picPath)
                        qrCode = qrReader(newImg)

                    url = 'https://proverkacheka.com/api/v1/check/get'
                    data = {
                        'token': '15035.F3Dub771H7j4pP6Tg',
                        'qrraw': qrCode
                    }

                    r = requests.post(url, data=data)
                    resp = r.json()
                    json2xls(resp['data']['json']['items'], pic.filename)
                except:
                    print(f'Error: {pic.filename}')

    return render_template('index.html')


def json2xls(data, filename):
    mainArr = []
    totalPrice = 0

    for item in data:
        obj = {"Имя товара": item["name"], "Цена": item["price"] / 100,
               "Количество": item["quantity"], "Итого": item["sum"] / 100}
        totalPrice += item["sum"] / 100
        mainArr.append(obj)

    mainArr.append({'ИТОГО=': totalPrice})

    df = pd.DataFrame(mainArr)

    xlsName = f'{filename.split(".")[0]}.xls'

    xlsPath = os.path.join(app.config['UPLOAD_XLS_FOLDER'], xlsName)
    df.to_excel(xlsPath, index=False)


def qrReader(img):
    img = plt.imread(img)
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img)

    if data:
        return data
    else:
        return None


def normalizeImg(img):
    image = ndi.median_filter(util.img_as_float(img), size=9)
    image = skimage.color.rgb2gray(image)
    # plt.imshow(image, cmap='gray')

    pores_gamma = exposure.adjust_gamma(image, gamma=0.5)
    # plt.imshow(pores_gamma, cmap='gray')

    thresholded = (pores_gamma <= 0.3)
    # plt.imshow(thresholded, cmap='gray')

    edge = feature.canny(thresholded, sigma=6)
    # plt.imshow(edge)

    contours = measure.find_contours(edge, 0.5)
    # plt.imshow(edge)
    for contour in contours:
        plt.plot(contour[:, 1], contour[:, 0], linewidth=2)

    positions = np.concatenate(contours, axis=0)
    min_pos_x = int(min(positions[:, 1]))
    max_pos_x = int(max(positions[:, 1]))
    min_pos_y = int(min(positions[:, 0]))
    max_pos_y = int(max(positions[:, 0]))

    start = (min_pos_x, min_pos_y)
    end = (max_pos_x, max_pos_y)
    cv2.rectangle(img, start, end, (255, 0, 0), 5)
    # io.imshow(img)

    new_img = img[min_pos_y:max_pos_y, min_pos_x:max_pos_x]
    # plt.imshow(new_img)

    return new_img


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")

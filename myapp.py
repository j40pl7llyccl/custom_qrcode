import io
from flask import Flask, request, send_file, render_template, jsonify
from PIL import Image
import qrcode

app = Flask(__name__)

@app.route('/generate_qrcode', methods=['GET', 'POST'])
def generate_qrcode():
    """
    - GET:  直接回傳前端頁面 (index.html)，提供圖片上傳與文字輸入介面
    - POST: 接收使用者上傳的圖片和文字，生成一張中心帶有該圖片的 QR Code，然後回傳 PNG 圖檔
    """
    if request.method == 'GET':
        # 直接用瀏覽器開 http://127.0.0.1:5000/generate_qrcode 時，回傳index.html
        return render_template('/templates/index.html')

    # 以下處理POST請求
    file = request.files.get('image')   # 對應 <input name="image">
    data = request.form.get('data')     # 對應 formData.append('data', ...)

    if not file or not data:
        return jsonify({'error': 'No file or data provided'}), 400

    try:
        # 1. 生成基礎 QR Code（使用較高容錯，方便在中心貼logo）
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        qr.add_data(data)
        qr.make(fit=True)
        qr_code_img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')

        # 2. 將上傳圖片縮放後貼在QR Code的中心
        user_img = Image.open(file).convert("RGBA")
        logo_size = (qr_code_img.width // 4, qr_code_img.height // 4)
        user_img.thumbnail(logo_size, Image.Resampling.BICUBIC) #Image.Resampling.BICUBIC Image.Resampling.LANCZOS

        # 計算要貼到 QR Code 圖片中央的位置
        pos = (
            (qr_code_img.width - user_img.width) // 2,
            (qr_code_img.height - user_img.height) // 2
        )
        # 貼上去(並保留透明度)
        qr_code_img.paste(user_img, pos, user_img)

        # 3. 將最終合成的圖片輸出為 PNG 回傳
        img_bytes = io.BytesIO()
        qr_code_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return send_file(img_bytes, mimetype='image/png')

    except Exception as e:
        print("Error while generating QR code:", e)
        return jsonify({'error': 'Failed to generate QR Code'}), 500

if __name__ == '__main__':
    app.run(debug=True)

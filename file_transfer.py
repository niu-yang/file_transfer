import os
import socket
import qrcode
import base64
from io import BytesIO
from flask import Flask, render_template, request, send_from_directory, redirect, url_for

app = Flask(__name__)

# 配置上传文件夹
UPLOAD_FOLDER = 'D:\\'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 生成二维码图片
def generate_qrcode(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 将图片转换为Base64编码
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

# 获取本地IP地址
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# 首页 - 显示二维码和文件列表
@app.route('/')
def index():
    local_ip = get_local_ip()
    port = 5000
    server_url = f'http://{local_ip}:{port}'
    qr_img = generate_qrcode(server_url)
    
    # 获取上传的文件列表
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(file_path):
            files.append({
                'name': filename,
                'size': os.path.getsize(file_path),
                'url': url_for('download_file', filename=filename)
            })
    
    return render_template('index.html', qr_img=qr_img, server_url=server_url, files=files)

# 处理文件上传
@app.route('/upload/', methods=['POST'])
def upload_file():
    # 检查是否有文件上传
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    # 如果用户没有选择文件，浏览器也可能会提交一个空的文件
    if file.filename == '':
        return redirect(url_for('index'))
    
    # 保存文件
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return redirect(url_for('index'))

# 下载文件
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"服务器运行中,请在手机浏览器中访问:http://{local_ip}:5000")
    app.run(host='0.0.0.0', port=5000)
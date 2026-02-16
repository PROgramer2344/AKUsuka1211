from flask import Flask, render_template_string, request, send_file
import yt_dlp
import os
import tempfile

app = Flask(__name__)

# Menggunakan temp directory agar bisa berjalan di server cloud manapun
TEMP_DIR = tempfile.gettempdir()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud YT Downloader</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; text-align: center; background: #1a1a1a; color: white; padding: 20px; }
        .container { max-width: 600px; margin: auto; background: #2d2d2d; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h2 { color: #ff0000; }
        input { width: 80%; padding: 15px; border-radius: 30px; border: none; margin-bottom: 20px; font-size: 16px; }
        button { padding: 12px 25px; background: #ff0000; color: white; border: none; border-radius: 30px; cursor: pointer; font-weight: bold; transition: 0.3s; }
        button:hover { background: #cc0000; transform: scale(1.05); }
        .preview { margin-top: 30px; display: {{ 'block' if info else 'none' }}; border-top: 1px solid #444; padding-top: 20px; }
        img { width: 100%; border-radius: 10px; max-width: 400px; }
        select { width: 100%; padding: 12px; margin: 15px 0; border-radius: 8px; background: #3d3d3d; color: white; border: 1px solid #555; }
        .status { margin-top: 10px; font-size: 14px; color: #aaa; }
    </style>
</head>
<body>
    <div class="container">
        <h2>YouTube Video Downloader</h2>
        <form method="POST" action="/get_info">
            <input type="text" name="url" placeholder="Masukkan link YouTube..." value="{{ url or '' }}" required>
            <br>
            <button type="submit">Cek Detail Video</button>
        </form>

        <div class="preview">
            {% if info %}
                <h3>{{ info.title }}</h3>
                <img src="{{ info.thumbnail }}" alt="Thumbnail">
                
                <form method="POST" action="/download">
                    <input type="hidden" name="url" value="{{ url }}">
                    <label for="format">Pilih Resolusi:</label>
                    <select name="format_id" id="format">
                        {% for f in info.formats %}
                            <option value="{{ f.id }}">{{ f.res }} - {{ f.ext }}</option>
                        {% endfor %}
                    </select>
                    <button type="submit" style="background: #28a745;">Mulai Download</button>
                </form>
                <p class="status">Catatan: Proses download mungkin memakan waktu tergantung ukuran video.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, info=None, url=None)

@app.route('/get_info', methods=['POST'])
def get_info():
    url = request.form['url']
    try:
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(url, download=False)
            formats = []
            # Filter hanya format yang ada video + audio agar tidak butuh ffmpeg tambahan di cloud
            for f in meta.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    formats.append({
                        'id': f['format_id'],
                        'res': f.get('resolution', 'N/A'),
                        'ext': f['ext']
                    })
            
            info = {
                'title': meta.get('title'),
                'thumbnail': meta.get('thumbnail'),
                'formats': formats[::-1] # Kualitas terbaik di atas
            }
        return render_template_string(HTML_TEMPLATE, info=info, url=url)
    except Exception as e:
        return f"Terjadi Kesalahan: {str(e)}"

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format_id = request.form['format_id']
    
    # Simpan di folder sementara server
    out_tmpl = os.path.join(TEMP_DIR, '%(title)s.%(ext)s')
    
    ydl_opts = {
        'format': format_id,
        'outtmpl': out_tmpl,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            return send_file(path, as_attachment=True)
    except Exception as e:
        return f"Gagal mengunduh: {str(e)}"

if __name__ == '__main__':
    # Gunakan port dari environment variable jika ada (penting untuk hosting)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

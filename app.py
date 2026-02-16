    # Gunakan port dari environment variable jika ada (penting untuk hosting)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
import os
from flask import Flask, render_template_string, request, send_file
import yt_dlp
import tempfile

app = Flask(__name__)

# Template HTML
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>YT Downloader Pro</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; text-align: center; background: #121212; color: white; padding: 20px; }
        input { width: 80%; padding: 12px; border-radius: 25px; border: none; margin-bottom: 10px; }
        button { padding: 10px 20px; background: #ff0000; color: white; border: none; border-radius: 25px; cursor: pointer; }
    </style>
</head>
<body>
    <h2>YouTube Downloader Online</h2>
    <form method="POST">
        <input type="text" name="url" placeholder="Paste Link YouTube..." required>
        <button type="submit">Download Sekarang</button>
    </form>
    {% if pesan %}<p>{{ pesan }}</p>{% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    pesan = ""
    if request.method == 'POST':
        url = request.form['url']
        try:
            # Gunakan folder temp agar bisa jalan di Cloud
            with tempfile.TemporaryDirectory() as tmpdir:
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    return send_file(filename, as_attachment=True)
        except Exception as e:
            pesan = f"Error: {str(e)}"
    return render_template_string(HTML_TEMPLATE, pesan=pesan)

if __name__ == '__main__':
    # Port 8000 adalah standar Koyeb
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)

import os
from flask import Flask, render_template_string, request, send_file
import yt_dlp
import tempfile

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>YT Downloader</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; text-align: center; background: #121212; color: white; padding: 20px; }
        input { width: 80%; padding: 15px; border-radius: 30px; border: none; margin-bottom: 10px; }
        button { padding: 12px 25px; background: #ff0000; color: white; border: none; border-radius: 30px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <h2>YouTube Downloader Online</h2>
    <form method="POST">
        <input type="text" name="url" placeholder="Paste Link YouTube di Sini..." required>
        <button type="submit">Download ke HP</button>
    </form>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form['url']
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                opts = {'format': 'best', 'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s')}
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    path = ydl.prepare_filename(info)
                    return send_file(path, as_attachment=True)
        except Exception as e:
            return f"Error: {str(e)}"
    return render_template_string(HTML)

if __name__ == "__main__":
    # INI KUNCI AGAR RAILWAY BERHASIL:
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

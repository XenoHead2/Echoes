import http.server
import socketserver
import json
import os
import cgi
import shutil
from PIL import Image
import io

PORT = 8000

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/save_chapters':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                chapters = data.get('chapters', [])
                with open('chapters.txt', 'w', encoding='utf-8') as f:
                    for chapter in chapters:
                        f.write(f"{chapter}\n")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode())
            except Exception as e:
                self.send_error(500, f"Error saving chapters: {str(e)}")

        elif self.path == '/api/save_milestones':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                with open('milestones.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode())
            except Exception as e:
                self.send_error(500, f"Error saving milestones: {str(e)}")

        elif self.path == '/api/save_bgm':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                with open('bgm.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode())
            except Exception as e:
                self.send_error(500, f"Error saving bgm: {str(e)}")

        elif self.path == '/api/upload_audio':
            try:
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST',
                             'CONTENT_TYPE': self.headers['Content-Type'],
                             }
                )
                
                if 'audio' not in form:
                    self.send_error(400, "No audio uploaded")
                    return
                    
                fileitem = form['audio']
                
                if not fileitem.file:
                    self.send_error(400, "Invalid file upload")
                    return
                    
                filename = os.path.basename(fileitem.filename)
                
                os.makedirs(os.path.join('audio', 'bgm'), exist_ok=True)
                filepath = os.path.join('audio', 'bgm', filename)
                
                with open(filepath, 'wb') as f:
                    shutil.copyfileobj(fileitem.file, f)
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "filepath": f"audio/bgm/{filename}"}).encode())
                
            except Exception as e:
                self.send_error(500, f"Error uploading audio: {str(e)}")

        elif self.path == '/api/upload_image':
            try:
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST',
                             'CONTENT_TYPE': self.headers['Content-Type'],
                             }
                )
                
                if 'image' not in form:
                    self.send_error(400, "No image uploaded")
                    return
                    
                fileitem = form['image']
                
                if not fileitem.file:
                    self.send_error(400, "Invalid file upload")
                    return
                    
                filename = os.path.basename(fileitem.filename)
                filepath = os.path.join('images', filename)
                
                # Ensure images directory exists
                os.makedirs('images', exist_ok=True)
                
                ext = os.path.splitext(filename)[1].lower()
                if ext in ['.gif', '.webp']:
                    # Bypass Pillow processing to preserve animation
                    with open(filepath, 'wb') as f:
                        shutil.copyfileobj(fileitem.file, f)
                else:
                    # Process image with Pillow
                    try:
                        img = Image.open(fileitem.file)
                        
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        
                        # Center Crop to Square
                        width, height = img.size
                        new_size = min(width, height)
                        left = (width - new_size) / 2
                        top = (height - new_size) / 2
                        right = (width + new_size) / 2
                        bottom = (height + new_size) / 2
                        
                        img = img.crop((left, top, right, bottom))
                        
                        # Resize to 800x800
                        img = img.resize((800, 800), Image.Resampling.LANCZOS)
                        
                        img.save(filepath, quality=85)
                    except Exception as img_err:
                        self.send_error(500, f"Error processing image: {str(img_err)}")
                        return
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "filepath": f"images/{filename}"}).encode())
                
            except Exception as e:
                self.send_error(500, f"Error uploading image: {str(e)}")
        else:
            self.send_error(404, "Endpoint not found")

# We use socketserver.TCPServer with allow_reuse_address to avoid "Address already in use"
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    with ThreadedTCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

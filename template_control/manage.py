import sys
sys.path.append('../')

from template_control.api import create_app
app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=12345)

"""Native window shell.

Only needed if Edge app mode turns out to be insufficient — see
docs/decisions.md. Uses the WebView2 runtime already present in Windows;
no bundled Chromium.

Package with:  pyinstaller --onedir --noconsole launcher.py
(--onedir, not --onefile: temp-directory unpacking is a primary
antivirus heuristic.)
"""
import os
import threading

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

HOST, PORT = "127.0.0.1", 8731


def _serve():
    from waitress import serve
    from config.wsgi import application
    serve(application, host=HOST, port=PORT, threads=8)


def main():
    import webview
    threading.Thread(target=_serve, daemon=True).start()
    window = webview.create_window(
        "IASG MIS",
        f"http://{HOST}:{PORT}/",
        width=1600, height=980, maximized=True,
    )
    webview.start(window)


if __name__ == "__main__":
    main()

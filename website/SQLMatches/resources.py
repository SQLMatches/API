import os


class Sessions:
    pass


class Config:
    frontend_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "frontend"
    )
    assets_dir = os.path.join(frontend_dir, "assets")
    templates_dir = os.path.join(frontend_dir, "templates")

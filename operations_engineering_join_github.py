from join_github_app import create_app


# Gunicorn entry point, return the object without running it
def app():
    return create_app()


# Run Flask locally entry point for makefile and debugger
def run_app():
    flask_app = create_app()
    flask_app.run(port=4567)
    return flask_app


if __name__ == "__main__":
    run_app()

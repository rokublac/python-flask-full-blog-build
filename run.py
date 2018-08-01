from flaskblog import create_app


app = create_app()

# run in DEBUG mode when script is ran directly (python flaskblog.py)
if __name__ == '__main__':
    app.run(debug=True)




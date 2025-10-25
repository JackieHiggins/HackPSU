from app import create_app
# create app
app = create_app()

if __name__ == '__main__':
    # run server
    app.run(debug=True)
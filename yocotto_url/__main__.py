from .application import setup_app

app = setup_app()
app.run(port=8080)

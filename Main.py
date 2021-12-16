from flask import Flask, make_response, redirect, request

from PIL import Image, ImageGrab
import io

import PuzzleSolver

app = Flask(__name__)
solver = PuzzleSolver.PuzzleSolver()

###############################################################################

@app.route("/")
def index():
    return redirect("/static/index.html")

###############################################################################

@app.route("/result")
def result():
    # check for any parameters passed in the url
    debug = request.args.get("debug", 0, type=int)

    # grab a screenshot
    img = ImageGrab.grab()

    # get the solution
    try:
        result = solver.run(img, bool(debug))
    except BaseException as e:
        result = None
        print("Caught exception: " + str(e.args))

    # return the result
    if (result is None):
        return redirect("/static/error.html")
    else:
        # convert Image object to the raw binary data that can be sent over the network
        output = io.BytesIO()
        result.save(output, format='PNG')
        hex_data = output.getvalue()

        # create the http response and send it
        response = make_response()
        response.set_data(hex_data)
        response.content_type = "image/png"
        response.content_length = len(hex_data)

        return response

###############################################################################

if __name__ == "__main__":
    app.run("0.0.0.0", 6512)

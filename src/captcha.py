from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
# import PySimpleGUI as sg
import re
from twocaptcha import TwoCaptcha
import sys
from decouple import config

def captcha_builder(resp):
    with open('../captcha.svg', 'w') as f:
        f.write(re.sub('(<path d=)(.*?)(fill=\"none\"/>)', '', resp['captcha']))

    drawing = svg2rlg('../captcha.svg')
    renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")

    #solved using 2Captcha
    solver = TwoCaptcha(config('API_KEY'))
    try:
        result = solver.normal('captcha.png')

    except Exception as e:
        sys.exit(e)

    else:
        return str(result.get('code'))


    # layout = [[sg.Image('captcha.png')],
    #           [sg.Text("Enter Captcha Below")],
    #           [sg.Input()],
    #           [sg.Button('Submit', bind_return_key=True)]]
    #
    # window = sg.Window('Enter Captcha', layout)
    # event, values = window.read()
    # window.close()
    # return values[1]


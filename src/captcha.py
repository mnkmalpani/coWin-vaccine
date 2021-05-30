from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
# import PySimpleGUI as sg
import re
from twocaptcha import TwoCaptcha
import sys
# import os

def captcha_builder(resp):
    with open('../captcha.svg', 'w') as f:
        f.write(re.sub('(<path d=)(.*?)(fill=\"none\"/>)', '', resp['captcha']))

    drawing = svg2rlg('../captcha.svg')
    renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")

    api_key = 'b9f8e9e1521dafe55f2ff2dbb74d4895'
    #solved using 2Captcha
    solver = TwoCaptcha(api_key)
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


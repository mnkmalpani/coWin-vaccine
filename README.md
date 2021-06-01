# coWin-vaccine
This project is developed to book vaccine slots automatically that comes on coWin website. 

## Updates
### Important: 
- This is a just proof of concept project.
- Make sure that all the beneficiaries selected are supposed to be of same age and to get the same vaccine and dose. 
- There is no option to register new mobile or add beneficiaries. This can be used only after beneficiary has been added through the official app/site.
- And finally, I know code quality isn't great. Suggestions are welcome.

### Usage:

Use **Python 3.7** and install all the dependencies with:
```
pip install -r requirements.txt
```

Then, run the script file as show below:
```
python src\main.py
```

If you already have a bearer token, you can also use:
```
python src\main.py --token=YOUR-TOKEN-HERE
```

### Third-Party Package Dependency:
- ```PrettyTable``` : For displaying data in tabular format.
- ```requests``` : For making GET and POST requests to the API.
- ```decouple``` : For picking values from an env file
- ```svglib``` : For rendering the captcha
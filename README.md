# Overview

This simple project has been created for the recruitment purposes. It is a calculator which takes as an input HTTP POST request with mathematical equation (for example {’’expression’’:”2+2”}) and gives back an evaluated result of the equation in form of HTTP response.

## Technologies used:
- Python 3.8.3
- Flask 2.1.0 
## How to run:

To run this app you’ll need one of the popular IDEs like Pycharm. You can download the python file from GitHub and open it by using IDE or create new python file on your device and just copy paste the code to it. After that you have to download flask framework to your virtual environment, the simplest way to do that is by using pip. You run the app and copy the link which will poop out down below. Then now you have to options:

1. By pip you download requests library then you create a new file where you can sent POST request. When you will be doing that add ”/evaluate” to the link.
2. You can just use terminal with curl and remember to add ”/evaluate” to the link as well.

## IMPORTANT

Message pattern must look like this: ’{"expression":"YOUR MATHEMATICAL EXPRESSION”}’. If you don’t put expression string as a key then the app will sent an error messeage in response. Supported operations:
- "+" - addition
- "-" - subtraction
- "/" - division
- "*" - multiplication
- "(" - left parenthesis
- ")" - right parenthesis

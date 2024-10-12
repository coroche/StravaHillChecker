from flask import Flask, Request, Response, render_template_string
from data.config import getHTMLTemplate
from data.userDAO import getUserHillList
from http import HTTPStatus

app = Flask(__name__)

def serve_chart(done: int, toGo: int) -> Response:
    html = getHTMLTemplate('pieChart.html')
    html = html\
        .replace('{Done}', str(done))\
        .replace('{ToGo}', str(toGo))
    return Response(html, HTTPStatus.OK)


def return_error(message, code: HTTPStatus) -> Response:
    template = getHTMLTemplate('message.html')
    html = render_template_string(template, message=message)
    return Response(html, code)


def gcf_entry_point(request: Request) -> Response:
    userId = request.args.get('UserId')
    listId = request.args.get('ListId')
   
    if not userId:
        return return_error('No userId provided', HTTPStatus.BAD_REQUEST)
    
    if not listId:
        return return_error('No listId provided', HTTPStatus.BAD_REQUEST)

    hillList = getUserHillList(userId, listId)
    if not hillList:
        return return_error('Invalid parameters', HTTPStatus.BAD_REQUEST)
    done = hillList.numberCompleted
    toGo = len(hillList.hills) - done

    return serve_chart(done, toGo)


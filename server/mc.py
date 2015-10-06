#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, socketio, eventlet
from flask import Flask, request
from mcstatus import MinecraftServer

sio = socketio.Server()
app = Flask(__name__)
server = MinecraftServer.lookup('example.org:1234')

def ping():
    try:
        status = server.status()
        query = server.query()
        data = '{"status": "Online", "online": "%s", "max": "%s", "players": "%s", "motd": "%s"}' % (status.players.online, query.players.max, format(','.join(query.players.names)), query.motd.replace('"', '\\"'))
        sio.emit('status', data)
    except:
        data = '{"status": "Offline", "online": "0", "max": "?", "players": "", "motd": ""}'
        sio.emit('status', data)

@app.route('/', methods=['POST'])
def index():
    data = json.loads(request.form.get('payload'))
    parsedData = '{"username": "%s", "text": "%s"}' % (data['username'], data['text'].replace('"', '\\"'))
    sio.emit('event', parsedData)
    if (data['text'] == '_joined_' or data['text'] == '_quit_'):
        ping()
    return 'OK'

@sio.on('connect')
def connect(sid, environ):
    print('connect ', sid)
    ping()

@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)

@sio.on('status')
def status():
    ping()

if __name__ == '__main__':
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)

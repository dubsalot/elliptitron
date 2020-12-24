from bottle import route, run

@route('/hello')
def hello():
    return "Hello World!"

@route('/array')
def returnarray():
    from bottle import response
    from json import dumps
    rv = [{ "id": 1, "name": "Test Item 1" }, { "id": 2, "name": "Test Item 2" }]
    response.content_type = 'application/json'
    return dumps(rv)


run(host='localhost', port=8080, debug=True)
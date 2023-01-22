#!/usr/bin/python3

try:
    from wsgiref.handlers import CGIHandler
    from app import app

    CGIHandler().run(app)
except Exception as e:
    # TODO remove block for prod
    print("Content-Type: text/html\n\n")
    print(e)

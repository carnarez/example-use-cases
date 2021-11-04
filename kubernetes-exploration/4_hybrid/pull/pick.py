import falcon
import falcon_cors
import json
import os
import time

if os.environ['HOARD'].lower() in ['1', 'on', 'true', 'yes']:
    import pile

strftime = lambda s: time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(s))

class Docs:

    def on_get(self, req, resp):
        resp.text = json.dumps({
            '/docs': 'Returns this. Available on the root endpoint also.',
            '/list?since=<int>&until=<int>': 'Returns the messages stored in the relational database, time-bounded through the [optional] parameters (in seconds since epoch).',
            '/time?shift=<int>': 'Returns the current time, formatted as a date or in seconds since epoch. If a shift (in second) is provided the date will be shifted by that much.'
        }, indent=4)

class List:

    def on_get(self, req, resp):
        since = 0
        if 'since' in req.params:
            since = int(round(int(req.params['since']), 0))
        until = int(round(time.time(), 0))
        if 'until' in req.params:
            until = int(round(int(req.params['until']), 0))
        if os.environ['HOARD'].lower() in ['1', 'on', 'true', 'yes']:
            pile.create_tables_if_not_existing()
            records = pile.query(pile.Data, since, until)
            results = [{
                'id': r.id_,
                'timestamp': f'{r.timestamp}: {strftime(r.timestamp)}',
                'message': r.message
            } for r in records ]
        else:
            results = 'No database or no access to this latter.'
        resp.text = json.dumps(results, indent=4)

class Time:

    def on_get(self, req, resp):
        shift = 0
        if 'shift' in req.params:
            shift = int(round(int(req.params['shift']), 0))
        seconds = int(round(time.time() + shift, 0))
        resp.text = json.dumps({
            'date': strftime(seconds),
            'seconds': seconds,
            'shift': shift
        }, indent=4)

cors = falcon_cors.CORS(
    allow_all_headers=True,
    allow_all_methods=True,
    allow_all_origins=True,
    allow_credentials_all_origins=True,
    max_age=2.628e6
)

api = falcon.App(middleware=[cors.middleware])
api.add_route('/', Docs())
api.add_route('/docs', Docs())
api.add_route('/list', List())
api.add_route('/time', Time())

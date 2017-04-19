import json
import os

import requests


class Monitor(object):
    def __init__(self, api_key=None, time_zone='Asia/Kolkata'):
        self.api_endpoint = 'https://cronitor.io/v3/monitors'
        self.api_key = api_key or os.getenv('CRONITOR_API_KEY')
        self.timezone = time_zone

    def create(self, name=None, notifications=None, rules=None, tags=None):
        payload = self.__prepare_payload(tags, name, notifications, rules)
        return self.__create(payload=payload)

    def update(self, name=None, code=None, notifications=None, rules=None, tags=None):
        payload = self.__prepare_payload(tags, name, notifications, rules)
        return self.__update(payload=payload, code=code)

    def delete(self, code):
        return self.__delete(code)

    def get(self, code):
        return self.__get('{}/{}'.format(self.api_endpoint, code))

    def run(self, code):
        return self.__ping(code, 'run')

    def complete(self, code):
        return self.__ping(code, 'complete')

    def failed(self, code):
        return self.__ping(code, 'failed')

    def pause(self, code, hours):
        return self.__get('{}/{}/pause/{}'.format(self.api_endpoint, code, hours))

    def clone(self, code, name=None):
        return requests.post(self.api_endpoint,
                             auth=(self.api_key, ''),
                             data=json.dumps({"code": code, name: name}),
                             headers={'content-type': 'application/json'})

    def __ping(self, code, method):
        return self.__get('{}/{}/{}'.format(self.api_endpoint, code, method))

    def __get(self, url):
        return requests.get(url,
                            auth=(self.api_key, ''),
                            headers={'content-type': 'application/json'}
                            )

    def __create(self, payload):
        return requests.post(self.api_endpoint,
                             auth=(self.api_key, ''),
                             data=json.dumps(payload),
                             headers={'content-type': 'application/json'})

    def __update(self, payload=None, code=None):
        return requests.put('{}/{}'.format(self.api_endpoint, code),
                            auth=(self.api_key, ''),
                            data=json.dumps(payload),
                            headers={'content-type': 'application/json'}
                            )

    def __delete(self, code):
        return requests.delete('{}/{}'.format(self.api_endpoint, code),
                               auth=(self.api_key, ''),
                               headers={'content-type': 'application/json'}
                               )

    @staticmethod
    def __prepare_notifications(notifications):
        if notifications:
            return {
                "emails": notifications.get('emails', []),
                "phones": notifications.get('phones', []),
                "hipchat": notifications.get('hipchat', []),
                "pagerduty": notifications.get('pagerduty', []),
                "slack": notifications.get('slack', []),
                "templates": notifications.get('templates', []),
                "webhooks": notifications.get('webhooks', [])
            }
        else:
            return {}

    def __prepare_payload(self, tags, name, notifications, rules):
        return {
            "code": "new_monitor",
            "name": "workflow_{}_{}".format(id, name),
            "type": "heartbeat",
            "timezone": self.timezone,
            "notifications": self.__prepare_notifications(notifications),
            "rules": rules or [],
            "tags": tags or [],
            "note": "Cron tab monitoring for {} workflow".format(name)
        }

import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from . import models

class JobConsumer(WebsocketConsumer):
    def connect(self):
        self.job_id = self.scope['url_route']['kwargs']['job_id']
        self.job_group_name = f'job_{self.job_id}'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.job_group_name,
            self.channel_name,
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.job_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        job = text_data_json['job']

        print("Job", job)

        if job.get('courier_latitude') and job.get('courier_longitude'):
            self.scope['user'].courier.latitude = job['courier_latitude']
            self.scope['user'].courier.longitude = job['courier_longitude']
            self.scope['user'].courier.save()

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.job_group_name,
            {
                'type': 'job_update',
                'job': job,
            }
        )

    # recieve message from job group
    def job_update(self, event):
        job = event['job']

        # send message to websocket
        self.send(text_data=json.dumps({
            'job': job,
        }))
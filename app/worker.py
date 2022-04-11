import requests
import config

def send_simple_message(notify_email, title):
    subject = f'Task {title} completed!'
    return requests.post(
		f'{config.base_url}/messages',
		auth=("api", f'{config.api_key}'),
		data={"from": "Excited User <aayushi_sanghi@berkeley.edu>",
			"to": notify_email,
			"subject": subject,
			"text": "Congrats on completing 1 out of 2374307 other tasks!"})
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.network.urlrequest import UrlRequest
import json  # Don't forget to import the 'json' module

class ChatApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.text_input = TextInput(hint_text='Enter your query...')
        send_button = Button(text='Send', on_press=self.send_query)
        self.response_label = Label(text='')
        layout.add_widget(self.text_input)
        layout.add_widget(send_button)
        layout.add_widget(self.response_label)
        return layout
    
    def send_query(self, instance):
        query = self.text_input.text
        data = {'session_id': 'your_session_id', 'query': query}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        UrlRequest(
            'http://localhost:5000/AIchatGeneric',  # Replace with your API URL
            req_body=json.dumps(data),
            req_headers=headers,
            on_success=self.display_response,
            on_failure=self.display_error
        )

    def display_response(self, req, result):
        response = json.loads(result)
        self.response_label.text = response['answer']

    def display_error(self, req, result):
        self.response_label.text = 'Error: Could not connect to the API'

if __name__ == '__main__':
    ChatApp().run()

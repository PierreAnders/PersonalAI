from flask import Blueprint, request
from .services import set_light_state

hue_blueprint = Blueprint('philips_hue', __name__)

@hue_blueprint.route('/toggle_light', methods=['POST'])
def toggle_light():
    light_id = request.json.get('light_id')
    state = request.json.get('state') == 'on'
    set_light_state(light_id, state)
    return ('', 204)
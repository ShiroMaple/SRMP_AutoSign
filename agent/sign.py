# agent/sign.py
import json
from pathlib import Path
from datetime import date
from maa.custom_action import CustomAction
from maa.context import Context
from logger import SignInLogger

STATE_FILE = Path("../assets/config/sign_state.json")

class BaseSignAction(CustomAction):
    def __init__(self):
        self.logger = SignInLogger(STATE_FILE)
    
    def should_skip(self, app_name: str) -> bool:
        return self.logger.should_skip(app_name)
    
    def mark_success(self, app_name: str):
        self.logger.mark_success(app_name)
    
    def mark_failed(self, app_name: str):
        self.logger.mark_failed(app_name)
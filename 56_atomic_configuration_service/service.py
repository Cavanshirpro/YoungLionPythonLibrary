from YoungLion import File
from models import Settings
class ConfigService:
    def __init__(self,root): self.files=File(root)
    def load(self): return Settings(self.files.json_read("settings.json",default={"version":1,"ui":{}}))
    def save(self,s): self.files.atomic_write_json("settings.json",s.to_dict()); return self.files.checksum("settings.json")
    def backup(self): return self.files.backup("settings.json")

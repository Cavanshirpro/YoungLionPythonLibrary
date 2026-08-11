from tempfile import TemporaryDirectory
from service import ConfigService
with TemporaryDirectory() as tmp:
    c=ConfigService(tmp); s=c.load(); s.ui.theme="light"; s.ui.scale=1.25; digest=c.save(s); backup=c.backup(); print(s.to_dict()); print("sha256",digest); print("backup",backup)

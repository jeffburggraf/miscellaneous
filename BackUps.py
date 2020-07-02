import BackUp
import datetime

map1 = "C:\ArkServer\ShooterGame\Saved\SavedArks\CrystalIsles.ark"

Jeff = "C:\ArkServer\ShooterGame\Saved\SavedArks\\76561198011567776.arkprofile"
Connor = "C:\ArkServer\ShooterGame\Saved\SavedArks\\76561198141610353.arkprofile"
Ryan = "C:\ArkServer\ShooterGame\Saved\SavedArks\\76561199007951900.arkprofile"
Tribe = "C:\ArkServer\ShooterGame\Saved\SavedArks\\1547751309.arktribe"
datetime.timedelta(minutes=2)
BackUp.auto_backup_files([map1, Jeff, Ryan, Connor, Tribe],
                  (
                  datetime.timedelta(minutes=4),
                  datetime.timedelta(hours=1),
                  datetime.timedelta(days=1),
                  datetime.timedelta(weeks=4))
                         )

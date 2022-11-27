token = '5680914852:AAHhLlsZhiGzP95hdxS0UXY4Emhvbp-pzwE'

admin_ids = [2054873802]  # 1215075747
json_dir = 'files'
photos_dir = 'photos'
request_dir = 'requests'
times = ['9:00 - 10:00', '10:00 - 11:00', '11:00 - 12:00',
         '12:00 - 13:00', '13:00 - 14:00', '14:00 - 15:00',
         '15:00 - 16:00', '16:00 - 17:00', '17:00 - 18:00']


class Equip:
    def __init__(self, name):
        self.name = name
        self.description = None
        self.photos = []
        self.time = ['9:00 - 10:00', '10:00 - 11:00', '11:00 - 12:00',
                     '12:00 - 13:00', '13:00 - 14:00', '14:00 - 15:00',
                     '15:00 - 16:00', '16:00 - 17:00', '17:00 - 18:00']


class Request:
    def __init__(self, equip_name):
        self.equip_name = equip_name
        self.time = None
        self.user_name = None
        self.user_id = None
        self.accepted = None

import requests

event = 'SS14'
id = '32975'
password = '61490'

response = requests.post('http://localhost:8000/generate-qr',
                         json={'event': event, 'id': id, 'pass': password})

if response.status_code == 200:
    print('QRコードが生成されました')
else:
    print('エラーが発生しました:', response.text)

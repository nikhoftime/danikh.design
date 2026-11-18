# Generates the QR module matrices used by the DECODE station demos (media/demos/decode/qr.js).
# Every code is version 4 / error correction H so the three markers fit all of them (Station 5),
# and halves of different codes look alike (Station 4).
import json, qrcode
from qrcode.constants import ERROR_CORRECT_H
def mat(data):
    q = qrcode.QRCode(version=4, error_correction=ERROR_CORRECT_H, border=0)
    q.add_data(data); q.make(fit=False)
    return [''.join('1' if c else '0' for c in row) for row in q.get_matrix()]
B = 'https://danikh.design'
codes = {'main': B}
for s in ['path', 'simon', 'minda', 'soundlab', 'decode', 'lilypad', 'bistrobox']:
    codes[s] = f'{B}/#{s}'
out = {k: {'url': v, 'm': mat(v)} for k, v in codes.items()}
assert all(len(o['m']) == 33 for o in out.values())
open('/home/claude/site/media/demos/decode/qr.js', 'w').write('window.QR=' + json.dumps(out, separators=(',', ':')) + ';')
print({k: len(v['m']) for k, v in out.items()})

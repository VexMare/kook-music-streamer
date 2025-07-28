import requests
import re

# 输入歌单链接或ID
def extract_playlist_id(playlist_input):
    match = re.search(r'id=(\d+)', playlist_input) or re.search(r'playlist/(\d+)', playlist_input) or re.search(r'(\d{6,})', playlist_input)
    return match.group(1) if match else playlist_input

cookie = "_iuqxldmzr_=32; _ntes_nnid=f8d17ff9e05eeabfb8c72fe67ad97c16,1751683757404; _ntes_nuid=f8d17ff9e05eeabfb8c72fe67ad97c16; NMTID=00Oizgk-WYcmXqiDUmNm5Rtpyrf5kMAAAGX2H0B3A; WEVNSM=1.0.0; WNMCID=udswoz.1751683758155.01.0; WM_TID=HCqXgqTIIQNFBEQABRaSb7OBKqYFM%2BEq; sDeviceId=YD-oVtKGUmBDkdAAxEVQRbTe6KUerYUO4mm; ntes_utid=tid._.FIXa1T4qo25AEhQUQFPDaqPBa6YUf9ni._.0; __snaker__id=cQV1B7woOE1YivlC; __remember_me=true; _ns=NS1.2.460637847.1752213999; timing_user_id=time_bxhYvDdYla; ntes_kaola_ad=1; gdxidpyhxdE=xLinAr2KQACRbE6dMJbuW9QHVUy4%2F7EdTxW0OxNNZmLcZC1gYUnT6oEQJDur5ATAiBKne3epmAamVcl5CZXZobploHbM%2B%5CsTfWQPX4OXQR6VGf7nUJs%2FRD2a%5C3Z4uWnB%2F4duBVlvRco%2B%2B%2F7LCcxDMkAm4q8b9mk7yw%5CjexIlE%5C%5CYhpa7%3A1752995592949; MUSIC_U=002371E7668FBD67FCE25C294FB8E0EA024932A8812D854E56DBE11FF5693F2C236EF3C290D8367EA82922470229347DFF3EF32EEAD0B2135900F60923C9A27D2CF508C2883D16BB477CABE04883B3195059B483F0472E8D8676B1756658C0BD3B38F52BAF43FB61BA5F48E8696D4936AE51F2DB9A84398BDA0937008A642323BFED0BAE292D581E6A273CF0ABDE9F7C9ED74F79A5E5D334878482277B23E1C71978122714DDCB04FE08F4C7CDBCD32A58A0802DC22B1C1DD40E114F58DC9F5DBE177D1077EFC5AB9CCA72FF8A073970A1F92640723BDC516337EF18ED884ED048EC0F272C146D654525D55A9A18112C6CEA76F972DE126B1E4FAF018B65F2FA9C6302E06830BAD9FFB8C8F4BA2D5E3413EB6DD6DA1A062EAB26337AB07C7C3855115AF6D6133A3C084A4E5C3392BDC8AC459200014988C553E9C8A8BA928A3AA7C6CD4F62AB9D047DE1DAEA15B8FF5F1020C5FC954183C0A670D6E86129711623BB9B86442E18C1488744E2B9FABC1DF746D048CE521AB607D89546F9A4BE2BC40BF86E4954F03C285C44E380F942DC1D8A8FA8FED69B52F27572960814110C44; __csrf=31df74b574317b691b1961de39798404; JSESSIONID-WYYY=XJChzC28SNq2HItYknBNsc9goMm77mpui%2FXSRPq%2FHZ2WEqdncxhd65ToKoQo%2F%2FRGhbvCpd28WT8frn%5C6jnnCwsZ19aO%2FxGwOw0dxbjI8w7Blxv854W%2BKfmqBAP1aqTVRIunVdAorMqjnEmmD5qVFp7m8WF4XhACXPZl7Mplty2l%2B%2FGcU%3A1753265767321; WM_NI=86y44SGto%2FVEZLbiLygPy5dl8AZvRxlayeuYdM%2FKoVXZiT7uV44T4C6EJqZB7wkKcBIF2nVcS4IWLBg7Hdl3YANEpOCIH34TTZw1MIcx7hCWZBdRDx9ylYbpolDJiWisR0c%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee86f56af692ac97c754aa8a8ea2d44a979e8faccb3c86e7c09ae543a8b5bf8bf82af0fea7c3b92afceab7d5b75985aca1d0d54f9a94ae8acf73a590b7d6e768fc9f9697d174b0bfb786f853a893e1acee5e9c86a7b5b67f96ecfcb5b749f69b8692d94af5a9a5ace24a8b9afe8fd56991ec87b8cf4aa5e98885ef399b9f82a6f345819788d4b7609886b9d2d043a1a8f989c25d9a9eacb3c774fba7a4bae17cadb48cabec5dabad9ed1e237e2a3"

playlist_input = input('请输入网易云歌单链接或ID: ')
playlist_id = extract_playlist_id(playlist_input)

# 获取歌单详情
res = requests.get(f"https://music-api.focalors.ltd/playlist/detail?id={playlist_id}", params={"cookie": cookie})
data = res.json()
print('tracks数量:', len(data['playlist']['tracks']))
print('trackIds数量:', len(data['playlist']['trackIds']))

# 获取歌单所有歌曲ID
res = requests.get(f"https://music-api.focalors.ltd/playlist/track/all?id={playlist_id}")
data = res.json()
ids = [str(song['id']) for song in data.get('songs', [])]
if not ids:
    print('未获取到歌单歌曲')
    exit(1)

# 获取所有歌曲的直链
url_res = requests.get(f"https://music-api.focalors.ltd/song/url?id={','.join(ids)}")
url_data = url_res.json()
urls = [item['url'] for item in url_data['data'] if item['url']]

if not urls:
    print('未获取到任何可用直链')
    exit(1)

# 保存到list.txt
with open('list.txt', 'w', encoding='utf-8') as f:
    for url in urls:
        f.write(url + '\n')
print(f'已保存{len(urls)}首歌曲直链到list.txt') 
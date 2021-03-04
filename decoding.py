import geobuf
import json

def GEOjson2buf():
    # file = 'D:/work/Contour/lll/222222.json'
    
    f=open('D:/work/Contour/lll/222222.json','r', )
    r= f.read()
    r=r.decode("utf-8")
    myjson = json.loads(r)
    ed = geobuf.encode(myjson)
    with open('D:/work/Contour/lll/222225.bpf', "wb") as f:
        f.write(ed)
        print("^_^ write success")

    
    
if __name__ == '__main__':
    # 读取信息
    GEOjson2buf()
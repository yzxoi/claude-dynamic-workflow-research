import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).parent
out=root/'decoded-assets'
out.mkdir(exist_ok=True)
records=[]
for p in sorted((root/'bun-files').iterdir()):
 if not p.is_file(): continue
 b=p.read_bytes()
 if b[:4]!=bytes([40,181,47,253]): continue
 result=subprocess.run(['zstd','-d','--stdout',str(p)],capture_output=True,check=True).stdout
 target=out/p.name.removesuffix('.zst')
 target.write_bytes(result)
 records.append({'source':'bun-files/'+p.name,'output':'decoded-assets/'+target.name,'compressed_bytes':len(b),'decoded_bytes':len(result),'source_sha256':hashlib.sha256(b).hexdigest(),'sha256':hashlib.sha256(result).hexdigest()})
(root/'decoded-assets-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print(json.dumps({'assets':len(records),'decoded_bytes':sum(x['decoded_bytes'] for x in records)}))


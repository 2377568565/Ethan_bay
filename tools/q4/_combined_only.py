import os,re,subprocess,render
avail=sorted(int(f[1:3]) for f in os.listdir(os.path.join(render.Q4,'data')) if re.fullmatch(r'l\d\d\.py',f))
print(render.build_combined(avail))
subprocess.run(['python3',os.path.join(render.Q4,'online.py'),os.path.join(render.OUT,'gift-of-prophecy-all.html'),os.path.join(render.OUT,'..','..')],check=True)

# Puts each DECODE station GIF on the standard off-white plate (rounded card + soft shadow).
import subprocess
from PIL import Image, ImageDraw, ImageFilter
G=[('pff2XEeVnJoNOVYSxdjkp3Bv9Pk',666,1253),('lpVU8NUnBsur3yPZcd6HeWd0',600,1319),('EBL6vmyiuJQUVPo2pKYXwbw1Xs',664,1255),
   ('dEd4pi6yy2a2A5B2wrCAZuh1Zg',666,1253),('RRoVr3GBus2bm2iilRyqV5hsG8',600,1319),('WTJbK7QOGohmjI8aPDG2csneQRI',664,1254),('MuSQujdbniW32DGuAuhXquzaLc',600,1319)]
TOP,BOT=158,842   # plate drawn at 1600x900
import sys
for i,(g,x0,x1) in enumerate(G):
    if len(sys.argv)>1 and str(i+1)!=sys.argv[1]: continue
    x0+=x0%2; x1-= (x1-x0)%2; cw=x1-x0
    H=BOT-TOP; W=round(cw*H/1080/2)*2; X=(1600-W)//2
    bg=Image.open(f'/tmp/plates/out/decode-bg-{i+1}.png').convert('RGB').resize((1600,900),Image.LANCZOS)
    sh=Image.new('L',bg.size,0); ImageDraw.Draw(sh).rounded_rectangle((X,TOP+20,X+W,BOT+20),15,fill=70); sh=sh.filter(ImageFilter.GaussianBlur(23))
    bg=Image.composite(Image.new('RGB',bg.size,(15,14,14)),bg,sh); bg.save(f'/tmp/dbg{i}.png')
    m=Image.new('L',(W,H),0); ImageDraw.Draw(m).rounded_rectangle((0,0,W-1,H-1),15,fill=255); m.save(f'/tmp/dm{i}.png')
    out=f'/home/claude/site/originals/decode-plate-{i+1}.mp4'
    dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'/home/claude/site/plate-src/decode/{g}.gif']).decode().strip())
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'/home/claude/site/plate-src/decode/{g}.gif','-loop','1','-i',f'/tmp/dbg{i}.png','-loop','1','-i',f'/tmp/dm{i}.png','-filter_complex',
      f'[0:v]crop={cw-8}:1072:{x0+4}:4,scale={W}:{H},format=rgba[v];[2:v]format=gray[m];[v][m]alphamerge[vm];[1:v][vm]overlay={X}:{TOP}:shortest=1,format=yuv420p',
      '-t',f'{dur:.2f}','-r','25','-c:v','libx264','-crf','22','-preset','veryfast','-an','-movflags','+faststart',out],check=True)
    print(out)

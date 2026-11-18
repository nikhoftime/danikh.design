// Kalian, Joget-Joget: stage + puppet code from the laptop sketch (p5.js),
// by Danikh Nizam. Networking (Ably) and music removed so it runs standalone;
// everything else (stage, 4 characters, states, disco balls, spotlight,
// explosions, proximity sparks) is the original project code.
let bgMusic;
let musicStarted = false;
let appStarted   = false;

let breathe   = 0;
let spinAngle = 0;

let particles=[], meteorites=[];

// Spotlight
let stageDarkness  = 0;
let spotlightRadius = 0;

// Multi player
const NUM_SLOTS = 4;

let slotData = [
  {state:"idle",character:"wayang",rotX:0,rotY:0,rotZ:0,accX:0,accY:0,accZ:0,shake:0,micLevel:0,tap:false,intensity:0,active:false,cameraDark:false,cameraBrightness:255},
  {state:"idle",character:"wayang",rotX:0,rotY:0,rotZ:0,accX:0,accY:0,accZ:0,shake:0,micLevel:0,tap:false,intensity:0,active:false,cameraDark:false,cameraBrightness:255},
  {state:"idle",character:"wayang",rotX:0,rotY:0,rotZ:0,accX:0,accY:0,accZ:0,shake:0,micLevel:0,tap:false,intensity:0,active:false,cameraDark:false,cameraBrightness:255},
  {state:"idle",character:"wayang",rotX:0,rotY:0,rotZ:0,accX:0,accY:0,accZ:0,shake:0,micLevel:0,tap:false,intensity:0,active:false,cameraDark:false,cameraBrightness:255}
];

let slots = Array.from({length:NUM_SLOTS}, (_,i)=>({
  smoothRotY:0, smoothRotX:0, smoothRotZ:0,
  smoothAccX:0, smoothAccY:0,
  smoothShake:0, smoothMic:0,
  puppetX:0, puppetY:0,
  agitatedScale:1.0,
  panicLevel:0,
  spinAngle:0,
  col:{r:160,g:168,b:208},
  currentState:"idle",
  currentChar:"wayang",
  lastState:"idle",
  active:false
}));

const SLOT_COLORS = ["#e03060","#30a0e0","#40c060","#e09030"];
const SLOT_NAMES  = ["Player 1","Player 2","Player 3","Player 4"];

const STATE_COLORS={
  idle:     {r:160,g:168,b:208},
  happy:    {r:96, g:232,b:144},
  excited:  {r:255,g:220,b:60 },
  surprised:{r:255,g:140,b:40 },
  sad:      {r:80, g:100,b:210},
  sleepy:   {r:160,g:130,b:220},
  scared:   {r:210,g:70, b:190},
  angry:    {r:255,g:60, b:32 },
  blown:    {r:255,g:160,b:40 },
  broken:   {r:80, g:80, b:80 },
};

const VALID_STATES=["idle","happy","excited","surprised","sad","sleepy","scared","angry","blown","broken"];

// ── PROXIMITY SPARKS ─────────────────────────────────────

function checkPuppetProximity() {
  let sparkCols = [
    {r:255,g:100,b:200},{r:100,g:240,b:255},{r:255,g:240,b:80},
    {r:100,g:255,b:140},{r:180,g:100,b:255},{r:255,g:180,b:80}
  ];

  for (let i=0;i<NUM_SLOTS;i++) {
    for (let j=i+1;j<NUM_SLOTS;j++) {
      let a=slots[i];
      let b=slots[j];
      if (!a.active||!b.active) continue;
      if (a.currentState==="blown"||a.currentState==="broken") continue;
      if (b.currentState==="blown"||b.currentState==="broken") continue;

      let d=dist(a.puppetX,a.puppetY,b.puppetX,b.puppetY);
      let threshold=280;

      if (d<threshold) {
        // More sparks the closer they are
        let intensity=map(d,0,threshold,6,1);
        let count=floor(intensity);

        for (let k=0;k<count;k++) {
          let t=random();
          let mx=lerp(a.puppetX,b.puppetX,t);
          let my=lerp(a.puppetY,b.puppetY,t)-random(20,80);
          let c=sparkCols[floor(random(sparkCols.length))];
          let angle=random(TWO_PI);
          let speed=random(2,8);
          particles.push({
            x:mx, y:my,
            vx:cos(angle)*speed,
            vy:sin(angle)*speed-random(1,4),
            life:1.0,
            decay:random(0.04,0.10),
            r:random(2,5),
            col:c,
            type:'spark'
          });
        }

        // Faint rainbow connection line when very close
        if (d<150) {
          let c=sparkCols[floor(frameCount/4 % sparkCols.length)];
          stroke(c.r,c.g,c.b,map(d,0,150,120,20)); // (fixed: c is a plain {r,g,b} object)
          strokeWeight(1.5); noFill();
          line(a.puppetX,a.puppetY-40,b.puppetX,b.puppetY-40);
        }
      }
    }
  }
}

// ── SPOTLIGHT ────────────────────────────────────────────

function updateSpotlight() {
  let anyDark=false;
  for (let i=0;i<NUM_SLOTS;i++) {
    if (slotData[i].active&&slotData[i].cameraDark) anyDark=true;
  }
  stageDarkness   = lerp(stageDarkness,  anyDark?1.0:0.0, 0.04);
  spotlightRadius = lerp(spotlightRadius, anyDark?200:0,   0.04);
}

function drawSpotlight() {
  if (stageDarkness<0.02) return;

  noStroke();
  fill(0,0,0,stageDarkness*210);
  rect(0,0,width,height);

  for (let i=0;i<NUM_SLOTS;i++) {
    let s=slots[i];
    if (!s.active) continue;

    let px=s.puppetX, py=s.puppetY;
    let r=spotlightRadius*s.agitatedScale;

    let beamW=r*0.4;
    noStroke();
    fill(255,240,180,stageDarkness*40);
    beginShape();
    vertex(px-beamW*0.3,0); vertex(px+beamW*0.3,0);
    vertex(px+beamW,py);    vertex(px-beamW,py);
    endShape(CLOSE);

    fill(255,248,210,stageDarkness*80);
    ellipse(px,py+55,r*0.9,r*0.28);
  }
}

// ── UPDATE SLOT ───────────────────────────────────────────

function updateSlot(i) {
  let d=slotData[i];
  let s=slots[i];

  let incoming=d.state||"idle";
  s.currentState=VALID_STATES.includes(incoming)?incoming:"idle";
  s.currentChar=d.character||"wayang";

  s.smoothRotY=lerp(s.smoothRotY,d.rotY||0,0.2);
  s.smoothRotX=lerp(s.smoothRotX,d.rotX||0,0.2);
  s.smoothRotZ=lerp(s.smoothRotZ,d.rotZ||0,0.15);
  s.smoothAccX=lerp(s.smoothAccX,constrain(d.accX||0,-15,15),0.25);
  s.smoothAccY=lerp(s.smoothAccY,constrain(d.accY||0,-15,15),0.25);

  let rawShake=constrain(d.shake||0,0,40);
  s.smoothShake=lerp(s.smoothShake,rawShake,0.3);
  if (s.smoothShake>20) s.panicLevel=min(1,s.panicLevel+0.05);
  s.panicLevel=max(0,s.panicLevel-0.015);
  s.smoothMic=lerp(s.smoothMic,d.micLevel||0,0.3);

  let zoneW=width/NUM_SLOTS;
  let zoneCenter=(i+0.5)*zoneW;
  let targetX;
  if (s.currentState!=="idle"&&s.currentState!=="blown"&&s.currentState!=="broken") {
    targetX=zoneCenter+map(s.smoothRotY,-60,60,-zoneW*.35,zoneW*.35);
    targetX=constrain(targetX,zoneW*i+50,zoneW*(i+1)-50);
  } else {
    targetX=zoneCenter;
  }
  s.puppetX=lerp(s.puppetX,targetX,s.currentState==="angry"?.15:.06);
  s.puppetY=lerp(s.puppetY,height-180,.05);

  let targetScale=(s.currentState==="angry"||s.currentState==="excited")?1.4:
                   s.currentState==="scared"?1.15:
                   s.currentState==="sad"?.85:
                   s.currentState==="sleepy"?.9:1.0;
  s.agitatedScale=lerp(s.agitatedScale,targetScale,0.04);

  if      (s.currentState==="excited") s.spinAngle+=0.14;
  else if (s.currentState==="angry")   s.spinAngle+=0.08;
  else if (s.currentState==="happy")   s.spinAngle=lerp(s.spinAngle,radians(s.smoothRotZ)*3,0.14);
  else                                  s.spinAngle*=0.85;

  let tc=STATE_COLORS[s.currentState]||STATE_COLORS.idle;
  s.col.r=lerp(s.col.r,tc.r,0.05);
  s.col.g=lerp(s.col.g,tc.g,0.05);
  s.col.b=lerp(s.col.b,tc.b,0.05);

  if (s.currentState==="blown"&&s.lastState!=="blown") spawnExplosionForSlot(i);
  s.lastState=s.currentState;
}

// ── DRAW PUPPET FOR SLOT ──────────────────────────────────

function drawPuppetForSlot(i) {
  let s=slots[i];
  if      (s.currentChar==="wayang")  drawCrane(s);
  else if (s.currentChar==="robot")   drawTrickster(s);
  else if (s.currentChar==="sumo")    drawSumo(s);
  else if (s.currentChar==="samurai") drawSamurai(s);
}

function drawSlotBadge(i) {
  let s=slots[i];
  if (!s.active) return;
  let bx=s.puppetX, by=s.puppetY-220*s.agitatedScale;
  noStroke(); fill(20,20,20,180);
  rect(bx-36,by-12,72,24,12);
  fill(SLOT_COLORS[i]||"#888");
  textSize(11); textAlign(CENTER,CENTER);
  text(SLOT_NAMES[i], bx, by);
}

// ── COLOUR HELPERS ────────────────────────────────────────

function getSlotCol(s)  { return color(s.col.r,s.col.g,s.col.b); }
function getSlotDark(s) { return color(s.col.r*.55,s.col.g*.55,s.col.b*.55); }
function getSlotMid(s)  { return color(s.col.r*.78,s.col.g*.78,s.col.b*.78); }
function shadeColObj(c,amt) {
  return color(constrain(c.r+amt,0,255),constrain(c.g+amt,0,255),constrain(c.b+amt,0,255));
}

// ── EMOTION PARAMS ────────────────────────────────────────

function getEmotionParamsForSlot(s) {
  switch(s.currentState) {
    case "idle":     return {bob:sin(breathe*.6)*1.5,  lean:0,   armMult:0,   legMult:0,   speed:1  };
    case "happy":    return {bob:sin(breathe*1.4)*5,   lean:0,   armMult:1,   legMult:1,   speed:1  };
    case "excited":  return {bob:sin(breathe*3)*10,    lean:0,   armMult:1.4, legMult:1.4, speed:3  };
    case "surprised":return {bob:sin(breathe*8)*3-8,   lean:0,   armMult:1.2, legMult:.5,  speed:8  };
    case "sad":      return {bob:sin(breathe*.5)*2+6,  lean:.12, armMult:.4,  legMult:.3,  speed:.5 };
    case "sleepy":   return {bob:sin(breathe*.3)*1+4,  lean:.08, armMult:.2,  legMult:.2,  speed:.3 };
    case "scared":   return {bob:sin(breathe*6)*8,     lean:0,   armMult:1.3, legMult:1.2, speed:6  };
    case "angry":    return {bob:sin(breathe*5)*6,     lean:0,   armMult:1.5, legMult:1.3, speed:7  };
    default:         return {bob:sin(breathe*.6)*1.5,  lean:0,   armMult:0,   legMult:0,   speed:1  };
  }
}

// ── STAGE ────────────────────────────────────────────────

function drawStage() {
  const W=width, H=height, g=drawingContext, u=W/1100;
  const floorTop=H-Math.max(78*u, H*.165);
  // backdrop: teal radial glow
  let rg=g.createRadialGradient(W*.5,H*.42,0,W*.5,H*.42,W*.62);
  rg.addColorStop(0,'#1f6b63'); rg.addColorStop(.72,'#0c2a2a'); rg.addColorStop(1,'#0a2424');
  g.fillStyle=rg; g.fillRect(0,0,W,H);
  // spotlight beams
  noStroke();
  const beam=(x,top,ang,w)=>{ push(); translate(x,top); rotate(ang);
    let lg=g.createLinearGradient(0,0,0,H*1.1); lg.addColorStop(0,'rgba(255,240,200,.26)'); lg.addColorStop(1,'rgba(255,240,200,0)');
    g.fillStyle=lg; g.beginPath(); g.moveTo(-w*.06,0); g.lineTo(w*.06,0); g.lineTo(w*.5,H*1.1); g.lineTo(-w*.5,H*1.1); g.closePath(); g.fill(); pop(); };
  beam(W*.27,H*.06,-.28,W*.24); beam(W*.73,H*.06,.28,W*.24); beam(W*.5,H*.05,0,W*.2);
  // stage floor
  let fg=g.createRadialGradient(W*.5,floorTop,0,W*.5,floorTop,W*.7);
  fg.addColorStop(0,'#e2a53d'); fg.addColorStop(1,'#a8691e');
  g.fillStyle=fg; g.beginPath(); g.moveTo(-20,H+10); g.lineTo(-20,floorTop+H*.05);
  g.quadraticCurveTo(W*.5,floorTop-H*.05,W+20,floorTop+H*.05); g.lineTo(W+20,H+10); g.closePath(); g.fill();
  g.strokeStyle='rgba(244,194,92,.7)'; g.lineWidth=Math.max(3,8*u); g.beginPath(); g.moveTo(-20,floorTop+H*.05);
  g.quadraticCurveTo(W*.5,floorTop-H*.05,W+20,floorTop+H*.05); g.stroke();
  // curtains
  const stripes=(x0,x1)=>{ for(let x=x0;x<x1;x+=92*u*.5){ g.fillStyle='#b3561c'; g.fillRect(x,0,46*u*.5,H); g.fillStyle='#d77a2c'; g.fillRect(x+46*u*.5,0,24*u*.5,H); g.fillStyle='#9a4614'; g.fillRect(x+70*u*.5,0,22*u*.5,H);} };
  const cw=W*.21, cb=H*.8;
  g.save(); g.beginPath(); g.moveTo(0,0); g.lineTo(cw,0); g.bezierCurveTo(cw,cb*.55,cw*.55,cb*.9,0,cb); g.closePath(); g.clip(); stripes(0,cw+10);
  let sh=g.createLinearGradient(0,0,cw,0); sh.addColorStop(0,'rgba(0,0,0,.25)'); sh.addColorStop(.7,'rgba(0,0,0,0)'); sh.addColorStop(1,'rgba(0,0,0,.25)'); g.fillStyle=sh; g.fillRect(0,0,cw,H); g.restore();
  g.save(); g.beginPath(); g.moveTo(W,0); g.lineTo(W-cw,0); g.bezierCurveTo(W-cw,cb*.55,W-cw*.55,cb*.9,W,cb); g.closePath(); g.clip(); stripes(W-cw-10,W);
  sh=g.createLinearGradient(W,0,W-cw,0); sh.addColorStop(0,'rgba(0,0,0,.25)'); sh.addColorStop(.7,'rgba(0,0,0,0)'); sh.addColorStop(1,'rgba(0,0,0,.25)'); g.fillStyle=sh; g.fillRect(W-cw,0,cw,H); g.restore();
  // valance
  const vh=H*.085;
  g.save(); g.shadowColor='rgba(0,0,0,.35)'; g.shadowBlur=18*u; g.shadowOffsetY=10*u;
  g.beginPath(); g.moveTo(0,0); g.lineTo(W,0); g.lineTo(W,vh*.55); g.quadraticCurveTo(W*.5,vh*1.5,0,vh*.55); g.closePath();
  g.fillStyle='#c0631f'; g.fill(); g.restore();
  g.save(); g.beginPath(); g.moveTo(0,0); g.lineTo(W,0); g.lineTo(W,vh*.55); g.quadraticCurveTo(W*.5,vh*1.5,0,vh*.55); g.closePath(); g.clip();
  for(let x=0;x<W;x+=70*u){ g.fillStyle='#a24f17'; g.fillRect(x+60*u,0,10*u,vh*1.6); } g.restore();
  // disco balls
  const ball=(x,y,r)=>{ let bg=g.createRadialGradient(x-r*.3,y-r*.3,0,x,y,r); bg.addColorStop(0,'#fff'); bg.addColorStop(.4,'#bfc7d6'); bg.addColorStop(1,'#7c8597');
    g.save(); g.shadowColor='rgba(255,255,255,.4)'; g.shadowBlur=r*1.2; g.fillStyle=bg; g.beginPath(); g.arc(x,y,r,0,TWO_PI); g.fill(); g.restore(); };
  ball(W*.18,H*.2,16*u); ball(W*.8,H*.25,13*u); ball(W*.71,H*.15,9*u); ball(W*.27,H*.36,7*u);
  // title
  textAlign(CENTER,CENTER); noStroke(); textStyle(BOLD);
  fill(80,35,5,150); textSize(22*u); text('Kalian, Joget-Joget',W*.5+2*u,vh*.5+2*u);
  fill(255,235,170); text('Kalian, Joget-Joget',W*.5,vh*.5); textStyle(NORMAL);
}

// ── DISCO BALL METEORITES ─────────────────────────────────

function spawnDiscoBalls(slotIndex) {
  let count=floor(random(6,14));
  for (let i=0;i<count;i++) {
    let angle=random(PI*.55,PI*.75);
    let speed=random(6,14);
    let r=random(18,36);
    meteorites.push({
      x:random(width*.05,width*.95),
      y:random(-120,-20),
      vx:cos(angle)*speed*(random()<.5?1:-1),
      vy:sin(angle)*speed,
      r, spin:random(TWO_PI),
      spinSpeed:random(.04,.12)*(random()<.5?1:-1),
      trail:[], life:1.0, hit:false,
      fromSlot:slotIndex
    });
  }
}

function updateDiscoBalls() {
  meteorites.forEach(m=>{
    if (m.hit) return;
    m.trail.push({x:m.x,y:m.y,r:m.r});
    if (m.trail.length>8) m.trail.shift();
    m.x+=m.vx; m.y+=m.vy; m.vy+=0.3;
    m.spin+=m.spinSpeed;
    for (let i=0;i<NUM_SLOTS;i++) {
      let s=slots[i];
      if (!s.active) continue;
      if (dist(m.x,m.y,s.puppetX,s.puppetY)<120*s.agitatedScale+m.r) {
        m.hit=true; m.life=0;
        spawnDiscoBurst(m.x,m.y);
        s.panicLevel=min(1,s.panicLevel+0.5);
        break;
      }
    }
    if (m.y>height+80||m.x<-80||m.x>width+80) m.life=0;
  });
  meteorites=meteorites.filter(m=>m.life>0);
}

function drawDiscoBall(x,y,r,spin,alpha) {
  push(); translate(x,y);
  noStroke(); fill(200,200,215,alpha*255); circle(0,0,r*2);
  fill(140,140,160,alpha*180); arc(0,0,r*2,r*2,0,PI);
  let tileColors=[color(255,100,200),color(100,240,255),color(255,240,80),color(100,255,140),color(255,100,100),color(180,100,255),color(255,255,255),color(255,180,80)];
  let rows=5,cols=8;
  for (let row=0;row<rows;row++) {
    for (let col2=0;col2<cols;col2++) {
      let a=(col2/cols)*TWO_PI+spin;
      let elev=((row/rows)-.5)*PI;
      let tx=cos(a)*cos(elev)*r*.82, ty=sin(elev)*r*.82;
      if (sqrt(tx*tx+ty*ty)>r*.9) continue;
      let c=tileColors[(row*3+col2)%tileColors.length];
      let glint=sin(breathe*3+col2*.8+row*.5+spin)*.5+.5;
      fill(red(c),green(c),blue(c),(0.5+glint*.5)*alpha*255);
      circle(tx,ty,r*.22);
    }
  }
  fill(255,255,255,alpha*200); circle(-r*.3,-r*.3,r*.35);
  pop();
}

function drawDiscoBallsBehind() {
  meteorites.forEach(m=>{
    for (let i=0;i<m.trail.length;i++) {
      let t2=m.trail[i];
      noStroke(); fill(200,200,220,map(i,0,m.trail.length-1,0,.25)*255);
      circle(t2.x,t2.y,t2.r*.8);
    }
  });
}

function drawDiscoBallsFront() {
  meteorites.forEach(m=>{
    if (m.hit) return;
    drawDiscoBall(m.x,m.y,m.r,m.spin,1.0);
  });
}

function spawnDiscoBurst(x,y) {
  let burstCols=[{r:255,g:100,b:200},{r:100,g:240,b:255},{r:255,g:240,b:80},{r:100,g:255,b:140},{r:180,g:100,b:255},{r:255,g:180,b:80}];
  for (let i=0;i<40;i++) {
    let a=random(TWO_PI),sp=random(3,14);
    let c=burstCols[floor(random(burstCols.length))];
    particles.push({x,y,vx:cos(a)*sp,vy:sin(a)*sp-random(2,6),life:1.0,decay:random(.02,.06),r:random(2,6),col:c,type:'spark'});
  }
  for (let i=0;i<20;i++) {
    let a=random(TWO_PI),sp=random(1,6);
    particles.push({x,y,vx:cos(a)*sp,vy:sin(a)*sp-random(1,4),life:1.0,decay:random(.03,.08),r:random(3,8),col:{r:200,g:200,b:220},type:'shard'});
  }
}

// ── EXPLOSIONS ────────────────────────────────────────────

let slotExplosions=[[],[],[],[]];

function spawnExplosionForSlot(i) {
  let s=slots[i];
  let burstCols=[{r:255,g:100,b:200},{r:100,g:240,b:255},{r:255,g:240,b:80},{r:100,g:255,b:140},{r:180,g:100,b:255},{r:255,g:180,b:80},{r:255,g:60,b:32},{r:255,g:160,b:40}];
  slotExplosions[i]=[];
  for (let j=0;j<400;j++) {
    let a=random(TWO_PI),sp=random(2,14);
    let c=burstCols[floor(random(burstCols.length))];
    slotExplosions[i].push({x:s.puppetX+random(-50,50),y:s.puppetY+random(-130,130),vx:cos(a)*sp,vy:sin(a)*sp-random(3,8),life:1.0,decay:random(.005,.018),r:random(1,5),col:c,type:'spark'});
  }
}

function drawExplosionForSlot(i) {
  let s=slots[i];
  let exp=slotExplosions[i]||[];
  noStroke();
  exp.forEach(p=>{
    fill(p.col.r,p.col.g,p.col.b,p.life*220);
    if (p.type==='shard') { push(); translate(p.x,p.y); rotate(p.life*5); rectMode(CENTER); rect(0,0,p.r*2,p.r*2); rectMode(CORNER); pop(); }
    else circle(p.x,p.y,p.r*2);
  });
  if (s.currentState==="broken"&&exp.length<10) {
    fill(220,180,80); textSize(14); textAlign(CENTER,CENTER);
    text(SLOT_NAMES[i]+" shattered!", s.puppetX, s.puppetY);
  }
  slotExplosions[i]=exp.filter(p=>{ p.x+=p.vx; p.y+=p.vy; p.vy+=.18; p.life-=p.decay; return p.life>0; });
}

function updateParticles() {
  particles.forEach(p=>{ p.x+=p.vx; p.y+=p.vy; p.vy+=.18; p.life-=p.decay; p.vx*=.98; });
  particles=particles.filter(p=>p.life>0);
  noStroke();
  particles.forEach(p=>{
    fill(p.col.r,p.col.g,p.col.b,p.life*220);
    if (p.type==='shard') { push(); translate(p.x,p.y); rotate(p.life*5); rectMode(CENTER); rect(0,0,p.r*2,p.r*2); rectMode(CORNER); pop(); }
    else circle(p.x,p.y,p.r*2);
  });
}

// ── CHARACTERS ───────────────────────────────────────────

function drawCrane(s) {
  let cx=s.puppetX+s.panicLevel*random(-10,10);
  let cy=s.puppetY+s.panicLevel*random(-5,5);
  push(); translate(cx,cy); scale(s.agitatedScale); translate(-cx,-cy);

  let {bob,armMult,legMult,speed}=getEmotionParamsForSlot(s);
  let C=getSlotCol(s),D=getSlotDark(s),M=getSlotMid(s);
  let handLR=constrain(s.smoothRotY/35,-1,1);
  let handFB=constrain(s.smoothRotX/35,-1,1);
  let legLR=constrain(s.smoothAccX/10,-1,1);
  let legFB=constrain(s.smoothAccY/10,-1,1);
  let wingAngle=0,legSwing=0,legKick=0,neckCurl=0,headTilt=0;
  let st=s.currentState;

  if      (st==="idle")     { wingAngle=sin(breathe*.5)*.08; }
  else if (st==="happy")    { wingAngle=handLR*.8+handFB*.3+sin(s.spinAngle*.6)*.4; legSwing=legLR*.6+sin(breathe*2)*.12; legKick=legFB*.3; neckCurl=sin(breathe*1.8)*8; headTilt=sin(breathe*1.8)*.08; }
  else if (st==="excited")  { wingAngle=sin(breathe*3)*1.0+handLR*.5; legSwing=legLR*.6+sin(breathe*3)*.3; neckCurl=sin(breathe*3)*12; }
  else if (st==="sad")      { wingAngle=-.3; neckCurl=-18; headTilt=.22; }
  else if (st==="sleepy")   { wingAngle=-.2; neckCurl=-12; headTilt=.28; }
  else if (st==="surprised"){ wingAngle=.6+sin(breathe*8)*.2; neckCurl=sin(breathe*8)*4; headTilt=-.15; }
  else if (st==="scared")   { wingAngle=sin(breathe*6+random(-.2,.2))*.8; legSwing=sin(breathe*6)*.4+random(-.1,.1); neckCurl=sin(breathe*6)*10; }
  else if (st==="angry")    { wingAngle=sin(breathe*7)*1.1+random(-.3,.3); legSwing=sin(breathe*5)*.5+random(-.15,.15); neckCurl=sin(breathe*6)*30+random(-5,5); headTilt=sin(breathe*8)*.4+random(-.1,.1); }

  let by=cy+bob*.3;
  fill(M); stroke(D); strokeWeight(2);
  beginShape(); vertex(cx-16,by+38); vertex(cx-22,by+75); vertex(cx-8,by+88); vertex(cx,by+92); vertex(cx+8,by+88); vertex(cx+22,by+75); vertex(cx+16,by+38); endShape(CLOSE);
  fill(C); stroke(D); strokeWeight(2.5); ellipse(cx,by,68,84);
  let wBaseY=by-10;
  fill(M); stroke(D); strokeWeight(2);
  beginShape(); vertex(cx-28,wBaseY); quadraticVertex(cx-72,wBaseY-10+wingAngle*70,cx-54,wBaseY+32); quadraticVertex(cx-40,wBaseY+20,cx-28,wBaseY); endShape(CLOSE);
  beginShape(); vertex(cx+28,wBaseY); quadraticVertex(cx+72,wBaseY-10-wingAngle*70,cx+54,wBaseY+32); quadraticVertex(cx+40,wBaseY+20,cx+28,wBaseY); endShape(CLOSE);
  let neckTipX=cx+neckCurl*.3+4,neckTipY=by-105+bob;
  fill(C); stroke(D); strokeWeight(2.5);
  beginShape(); vertex(cx-12,by-36); bezierVertex(cx-10+neckCurl*.4,by-60,neckTipX-8,neckTipY+20,neckTipX-6,neckTipY); bezierVertex(neckTipX+6,neckTipY,cx+14+neckCurl*.4,by-60,cx+14,by-36); endShape(CLOSE);
  let headX=neckTipX+sin(headTilt)*14,headY=neckTipY-14;
  fill(C); stroke(D); strokeWeight(2.5); ellipse(headX,headY,34,30);
  fill('#e03030'); noStroke(); ellipse(headX-2,headY-14,16,8);
  fill('#e8c040'); stroke('#b08020'); strokeWeight(1.5);
  if (st==="happy"||st==="excited") { beginShape(); vertex(headX+14,headY+1); bezierVertex(headX+24,headY+8,headX+32,headY+2,headX+14,headY-2); endShape(CLOSE); }
  else if (st==="angry"||st==="scared") { beginShape(); vertex(headX+14,headY+3); vertex(headX+26,headY-5); vertex(headX+34,headY+4); vertex(headX+14,headY); endShape(CLOSE); }
  else { beginShape(); vertex(headX+14,headY-1); vertex(headX+34,headY-1); vertex(headX+14,headY+2); endShape(CLOSE); }
  fill(color(30,30,40)); noStroke(); circle(headX+7,headY-4,10);
  fill(255); circle(headX+6,headY-5,3.5);
  if (st==="angry") { stroke(D); strokeWeight(2); noFill(); line(headX+2,headY-10,headX+11,headY-7); }
  else if (st==="sad") { stroke(color(100,150,255)); strokeWeight(1.5); noFill(); line(headX+8,headY-2,headX+10,headY+6); }
  else if (st==="sleepy") { fill(C); noStroke(); rect(headX+2,headY-6,12,4); }
  let fCount=st==="angry"||st==="excited"?8:st==="happy"||st==="surprised"?5:3;
  fill(M); stroke(D); strokeWeight(1.5);
  for (let i=0;i<fCount;i++) {
    let fx=headX-8+i*4,flen=st==="angry"||st==="excited"?20+random(10):st==="happy"?16:st==="sad"||st==="sleepy"?6:10;
    let fa=st==="angry"?random(-.5,.5):st==="sad"?.25:0;
    line(fx,headY-12,fx+sin(fa)*flen,headY-12-cos(fa)*flen);
  }
  let lKnX=cx-16+(st==="idle"?0:legSwing*26+legKick*16),lKnY=by+50;
  let rKnX=cx+16+(st==="idle"?0:-legSwing*26-legKick*16),rKnY=by+50;
  stroke(D); strokeWeight(7); noFill();
  line(cx-8,by+38,lKnX,lKnY); line(lKnX,lKnY,lKnX-8,lKnY+42);
  line(cx+8,by+38,rKnX,rKnY); line(rKnX,rKnY,rKnX+8,rKnY+42);
  stroke(M); strokeWeight(4);
  line(cx-8,by+38,lKnX,lKnY); line(lKnX,lKnY,lKnX-8,lKnY+42);
  line(cx+8,by+38,rKnX,rKnY); line(rKnX,rKnY,rKnX+8,rKnY+42);
  stroke(D); strokeWeight(5);
  line(lKnX-20,lKnY+42,lKnX+8,lKnY+42); line(rKnX-8,rKnY+42,rKnX+20,rKnY+42);
  stroke(180,180,180,140); strokeWeight(1.5);
  line(headX,headY-12,headX,headY-90);
  line(cx-54,wBaseY+20,cx-54,wBaseY-70);
  line(cx+54,wBaseY+20,cx+54,wBaseY-70);
  pop();
}

function drawTrickster(s) {
  let cx=s.puppetX+s.panicLevel*random(-10,10);
  let cy=s.puppetY+s.panicLevel*random(-5,5);
  push(); translate(cx,cy); scale(s.agitatedScale); translate(-cx,-cy);

  let {bob,lean,armMult,legMult,speed}=getEmotionParamsForSlot(s);
  let C=getSlotCol(s),D=getSlotDark(s),M=getSlotMid(s);
  let st=s.currentState;
  let handLR=constrain(s.smoothRotY/35,-1,1),handFB=constrain(s.smoothRotX/35,-1,1);
  let legLR=constrain(s.smoothAccX/10,-1,1),legFB=constrain(s.smoothAccY/10,-1,1);
  let baseLean=lean,hatTilt=lean*.5,armSwingL=0,armSwingR=0,legSwing=0,legKick=0;

  if      (st==="idle")     { baseLean=sin(breathe*.4)*.02; }
  else if (st==="happy")    { baseLean=sin(breathe*1.8)*.06+handLR*.08; hatTilt=baseLean*.5; armSwingL=handLR*1.1+handFB*.5+sin(s.spinAngle*.7)*.4; armSwingR=-handLR*1.1+handFB*.5-sin(s.spinAngle*.7)*.4; legSwing=legLR*.7+sin(breathe*2)*.1; legKick=legFB*.5; }
  else if (st==="excited")  { baseLean=sin(breathe*3)*.12+handLR*.1; armSwingL=handLR*1.3+sin(breathe*3)*.8; armSwingR=-handLR*1.3+sin(breathe*3)*.8; legSwing=legLR*.7+sin(breathe*3)*.3; }
  else if (st==="sad")      { baseLean=.18; hatTilt=.15; armSwingL=-.35; armSwingR=-.35; }
  else if (st==="sleepy")   { baseLean=.14; hatTilt=.12; armSwingL=-.2; armSwingR=-.2; }
  else if (st==="surprised"){ armSwingL=.7+sin(breathe*8)*.2; armSwingR=.7+sin(breathe*8)*.2; }
  else if (st==="scared")   { baseLean=sin(breathe*6+random(-.1,.1))*.1; armSwingL=sin(breathe*6)*.9+random(-.2,.2); armSwingR=-sin(breathe*6)*.9+random(-.2,.2); legSwing=sin(breathe*5)*.3+random(-.1,.1); }
  else if (st==="angry")    { baseLean=sin(breathe*7)*.35+random(-.1,.1); armSwingL=sin(breathe*6)*1.3+random(-.2,.2); armSwingR=-sin(breathe*6)*1.3+random(-.2,.2); legSwing=sin(breathe*5)*.5+random(-.1,.1); hatTilt=baseLean*.5; }

  let topX=cx+sin(baseLean)*65,topY=cy-65+bob;
  let headX=topX+sin(baseLean)*14,headY=topY-20;
  fill(C); stroke(D); strokeWeight(2.5);
  beginShape(); vertex(cx-12,cy+18+bob*.3); vertex(cx+12,cy+18+bob*.3); vertex(topX+10,topY+14); vertex(topX-10,topY+14); endShape(CLOSE);
  fill(C); stroke(D); strokeWeight(2.5); circle(headX,headY,38);
  if (st==="idle"||st==="sleepy") {
    stroke(D); strokeWeight(2); noFill(); line(headX-9,headY-2,headX-3,headY-2); line(headX+3,headY-2,headX+9,headY-2); line(headX-6,headY+7,headX+6,headY+7);
  } else if (st==="happy"||st==="excited") {
    fill(color(30,30,40)); noStroke(); circle(headX-9,headY-3,9); circle(headX+9,headY-3,9);
    fill('#e03030'); stroke(D); strokeWeight(1.5); arc(headX,headY+4,16,14,0,PI);
  } else if (st==="sad") {
    fill(color(30,30,40)); noStroke(); circle(headX-9,headY-3,7); circle(headX+9,headY-3,7);
    stroke(D); strokeWeight(2); noFill(); arc(headX,headY+12,16,10,PI,TWO_PI);
    stroke(color(100,150,255)); strokeWeight(1.5); line(headX-4,headY+2,headX-2,headY+10); line(headX+4,headY+2,headX+2,headY+10);
  } else if (st==="surprised"||st==="scared") {
    fill(color(30,30,40)); noStroke(); circle(headX-9,headY-3,11); circle(headX+9,headY-3,11);
    fill(255); circle(headX-8,headY-4,4); circle(headX+10,headY-4,4);
    stroke(D); strokeWeight(2); noFill(); circle(headX,headY+8,10);
  } else {
    fill('#e03030'); noStroke(); circle(headX-9,headY-3,9); circle(headX+9,headY-3,9);
    fill(255); circle(headX-8,headY-4,3); circle(headX+10,headY-4,3);
    stroke(D); strokeWeight(2.5); noFill(); line(headX-12,headY-12,headX-3,headY-7); line(headX+3,headY-7,headX+12,headY-12);
    stroke(D); strokeWeight(2); beginShape(); vertex(headX-7,headY+6); vertex(headX-3,headY+11); vertex(headX+1,headY+6); vertex(headX+5,headY+11); vertex(headX+8,headY+6); endShape();
  }
  let hatX=headX+sin(hatTilt)*8,hatY=headY-20;
  fill(M); stroke(D); strokeWeight(2); ellipse(hatX,hatY+2,48,14);
  fill(shadeColObj(s.col,-30)); stroke(D); strokeWeight(2); rect(hatX-14,hatY-40,28,42,4);
  fill(shadeColObj(s.col,-50)); noStroke(); rect(hatX-14,hatY-14,28,6);
  let lShX=cx-12+sin(baseLean)*30,lShY=cy-8+bob*.4;
  let lElbX=lShX-30,lElbY=lShY+22;
  let lHandX=lElbX-16+armSwingL*30,lHandY=lElbY+32-abs(armSwingL)*12;
  stroke(D); strokeWeight(11); noFill(); line(lShX,lShY,lElbX,lElbY); line(lElbX,lElbY,lHandX,lHandY);
  stroke(C); strokeWeight(7); line(lShX,lShY,lElbX,lElbY); line(lElbX,lElbY,lHandX,lHandY);
  fill(C); stroke(D); strokeWeight(2); circle(lHandX,lHandY+8,18);
  stroke(D); strokeWeight(3); line(lHandX-6,lHandY+14,lHandX-8,lHandY+22); line(lHandX,lHandY+16,lHandX-1,lHandY+24); line(lHandX+5,lHandY+14,lHandX+5,lHandY+22);
  let rShX=cx+12+sin(baseLean)*30,rShY=cy-8+bob*.4;
  let rElbX=rShX+30,rElbY=rShY+22;
  let rHandX=rElbX+16+armSwingR*30,rHandY=rElbY+32-abs(armSwingR)*12;
  stroke(D); strokeWeight(11); noFill(); line(rShX,rShY,rElbX,rElbY); line(rElbX,rElbY,rHandX,rHandY);
  stroke(C); strokeWeight(7); line(rShX,rShY,rElbX,rElbY); line(rElbX,rElbY,rHandX,rHandY);
  fill(C); stroke(D); strokeWeight(2); circle(rHandX,rHandY+8,18);
  stroke(D); strokeWeight(3); line(rHandX-5,rHandY+14,rHandX-5,rHandY+22); line(rHandX+1,rHandY+16,rHandX,rHandY+24); line(rHandX+6,rHandY+14,rHandX+8,rHandY+22);
  let lKnX=cx-10+(st==="idle"?0:legSwing*30+legKick*16),lKnY=cy+52+bob*.1;
  let lFtX=lKnX+(st==="idle"?0:-6+legKick*8),lFtY=cy+95;
  stroke(D); strokeWeight(11); noFill(); line(cx-7,cy+18+bob*.3,lKnX,lKnY); line(lKnX,lKnY,lFtX,lFtY);
  stroke(C); strokeWeight(7); line(cx-7,cy+18+bob*.3,lKnX,lKnY); line(lKnX,lKnY,lFtX,lFtY);
  fill(M); stroke(D); strokeWeight(2); ellipse(lFtX-10,lFtY+7,22,10);
  let rKnX=cx+10-(st==="idle"?0:legSwing*30+legKick*16),rKnY=cy+52+bob*.1;
  let rFtX=rKnX+(st==="idle"?0:6-legKick*8),rFtY=cy+95;
  stroke(D); strokeWeight(11); noFill(); line(cx+7,cy+18+bob*.3,rKnX,rKnY); line(rKnX,rKnY,rFtX,rFtY);
  stroke(C); strokeWeight(7); line(cx+7,cy+18+bob*.3,rKnX,rKnY); line(rKnX,rKnY,rFtX,rFtY);
  fill(M); stroke(D); strokeWeight(2); ellipse(rFtX+10,rFtY+7,22,10);
  stroke(180,180,180,140); strokeWeight(1.5);
  line(hatX,hatY-40,hatX,hatY-110); line(lHandX,lHandY,lHandX,lHandY-100); line(rHandX,rHandY,rHandX,rHandY-100);
  pop();
}

function drawSumo(s) {
  let cx=s.puppetX+s.panicLevel*random(-10,10);
  let cy=s.puppetY+s.panicLevel*random(-5,5);
  push(); translate(cx,cy); scale(s.agitatedScale); translate(-cx,-cy);

  let {bob,armMult,legMult,speed}=getEmotionParamsForSlot(s);
  let C=getSlotCol(s),D=getSlotDark(s),M=getSlotMid(s);
  let st=s.currentState;
  let handLR=constrain(s.smoothRotY/35,-1,1),handFB=constrain(s.smoothRotX/35,-1,1);
  let legLR=constrain(s.smoothAccX/10,-1,1);
  let armSwing=handLR*.8*armMult+handFB*.3+sin(s.spinAngle*.5)*.3*armMult;
  let legSwing=legLR*.6*legMult+sin(breathe*2*speed)*.1;
  let sq=1+sin(breathe*speed*.8)*.05*armMult;
  if (st==="sad"||st==="sleepy") { armSwing*=.2; legSwing*=.1; sq=1; }
  if (st==="angry"||st==="scared") { armSwing=sin(breathe*6)*1.0+random(-.2,.2); legSwing=sin(breathe*5)*.5+random(-.1,.1); sq=1+sin(breathe*8)*.12; }

  let by=cy+bob*.3;
  fill(C); stroke(D); strokeWeight(3); ellipse(cx,by,168*sq,156/sq);
  stroke(D); strokeWeight(2); noFill(); arc(cx,by+22,100*sq,40,0,PI);
  fill(M); stroke(D); strokeWeight(2); ellipse(cx-28,by-30,68,48); ellipse(cx+28,by-30,68,48);
  fill(C); stroke(D); strokeWeight(2.5); ellipse(cx,by-68,56,32);
  fill(C); stroke(D); strokeWeight(3); ellipse(cx,by-98,88,84);
  fill(M); stroke(D); strokeWeight(1.5); ellipse(cx-36,by-94,32,28); ellipse(cx+36,by-94,32,28);
  fill(D); stroke(D); strokeWeight(1.5); ellipse(cx,by-138,28,20); ellipse(cx,by-148,18,24);
  let hy=by-98;
  if (st==="idle"||st==="sleepy") {
    stroke(D); strokeWeight(2.5); noFill(); line(cx-16,hy-4,cx-6,hy-4); line(cx+6,hy-4,cx+16,hy-4); arc(cx,hy+12,20,12,0,PI);
  } else if (st==="happy"||st==="excited") {
    fill(color(30,30,40)); noStroke(); arc(cx-14,hy-4,14,12,PI,TWO_PI); arc(cx+14,hy-4,14,12,PI,TWO_PI);
    fill('#e03030'); stroke(D); strokeWeight(2); arc(cx,hy+10,28,18,0,PI);
  } else if (st==="sad") {
    stroke(D); strokeWeight(2.5); noFill(); line(cx-16,hy-4,cx-6,hy-4); line(cx+6,hy-4,cx+16,hy-4);
    arc(cx,hy+18,22,14,PI,TWO_PI);
    stroke(color(100,150,255)); strokeWeight(2); line(cx-6,hy+2,cx-4,hy+12); line(cx+6,hy+2,cx+4,hy+12);
  } else if (st==="surprised"||st==="scared") {
    fill(color(30,30,40)); noStroke(); circle(cx-14,hy-4,16); circle(cx+14,hy-4,16);
    fill(255); circle(cx-12,hy-6,6); circle(cx+16,hy-6,6);
    stroke(D); strokeWeight(2); noFill(); circle(cx,hy+12,16);
  } else {
    fill(color(30,30,40)); noStroke(); circle(cx-14,hy-4,12); circle(cx+14,hy-4,12);
    stroke(D); strokeWeight(3); noFill(); line(cx-20,hy-16,cx-6,hy-9); line(cx+6,hy-9,cx+20,hy-16);
    fill('#111'); noStroke(); circle(cx,hy+12,20);
  }
  fill(M); stroke(D); strokeWeight(2.5); ellipse(cx-76,by-24,48,44); ellipse(cx+76,by-24,48,44);
  let lfx=cx-86+sin(armSwing)*36,lfy=by+10+cos(armSwing)*26;
  let rfx=cx+86-sin(armSwing)*36,rfy=by+10-cos(armSwing)*26;
  fill(M); stroke(D); strokeWeight(2); ellipse(lfx,lfy,44,40); ellipse(rfx,rfy,44,40);
  fill(C); stroke(D); strokeWeight(2); ellipse(lfx-5,lfy+24,38,38); ellipse(rfx+5,rfy+24,38,38);
  fill(D); stroke(D); strokeWeight(2); ellipse(cx,by+46,164,36);
  fill(M); stroke(D); strokeWeight(2); ellipse(cx,by+52,48,36);
  stroke(D); strokeWeight(4); for (let i=-2;i<=2;i++) line(cx+i*10,by+60,cx+i*10,by+90);
  fill(M); stroke(D); strokeWeight(2.5); ellipse(cx-26,by+72,60,56);
  let lkx=cx-28+sin(legSwing)*35,lky=by+108;
  fill(M); stroke(D); strokeWeight(2.5); ellipse(lkx,lky,52,48);
  fill(D); stroke(D); strokeWeight(2); ellipse(lkx-6,lky+28,56,24);
  fill(M); stroke(D); strokeWeight(2.5); ellipse(cx+26,by+72,60,56);
  let rkx=cx+28-sin(legSwing)*35,rky=by+108;
  fill(M); stroke(D); strokeWeight(2.5); ellipse(rkx,rky,52,48);
  fill(D); stroke(D); strokeWeight(2); ellipse(rkx+6,rky+28,56,24);
  stroke(180,180,180,140); strokeWeight(1.5);
  line(cx,by-148,cx,by-205); line(lfx-5,lfy+24,lfx-5,lfy-90); line(rfx+5,rfy+24,rfx+5,rfy-90);
  pop();
}

function drawSamurai(s) {
  let cx=s.puppetX+s.panicLevel*random(-10,10);
  let cy=s.puppetY+s.panicLevel*random(-5,5);
  push(); translate(cx,cy); scale(s.agitatedScale); translate(-cx,-cy);

  let {bob,lean,armMult,legMult,speed}=getEmotionParamsForSlot(s);
  let C=getSlotCol(s),D=getSlotDark(s),M=getSlotMid(s);
  let st=s.currentState;
  let handLR=constrain(s.smoothRotY/35,-1,1),handFB=constrain(s.smoothRotX/35,-1,1);
  let legLR=constrain(s.smoothAccX/10,-1,1);
  let baseLean=lean+sin(breathe*2*speed)*.04*armMult;
  let armSwing=handLR*.8*armMult+handFB*.4+sin(s.spinAngle*.6)*.3*armMult;
  let legSwing=legLR*.5*legMult+sin(breathe*2*speed)*.15;
  if (st==="sad")   { baseLean=.2; armSwing=-.3; }
  if (st==="sleepy"){ baseLean=.15; armSwing=-.1; }
  if (st==="angry"||st==="scared") { baseLean=sin(breathe*7)*.2+random(-.1,.1); armSwing=sin(breathe*6)*.9+random(-.1,.1); legSwing=sin(breathe*5)*.4+random(-.1,.1); }

  let by=cy+bob*.3,lx=cx+sin(baseLean)*14;
  fill(C); stroke(D); strokeWeight(2.5);
  beginShape(); vertex(lx-58,by-50); vertex(lx+58,by-50); vertex(lx+66,by-12); vertex(lx+66,by+36); vertex(lx+50,by+62); vertex(lx-50,by+62); vertex(lx-66,by+36); vertex(lx-66,by-12); endShape(CLOSE);
  stroke(D); strokeWeight(2); noFill(); line(lx-58,by-26,lx+58,by-26); line(lx-62,by+6,lx+62,by+6); line(lx-62,by+38,lx+62,by+38);
  fill(M); stroke(D); strokeWeight(2);
  quad(lx-64,by-60,lx-64,by+4,lx-96,by+8,lx-96,by-56);
  line(lx-64,by-36,lx-96,by-36); line(lx-64,by-16,lx-96,by-16);
  quad(lx+64,by-60,lx+64,by+4,lx+96,by+4,lx+96,by-56);
  line(lx+64,by-36,lx+96,by-36); line(lx+64,by-16,lx+96,by-16);
  fill(C); stroke(D); strokeWeight(2); quad(lx-18,by-70,lx+18,by-70,lx+15,by-50,lx-15,by-50);
  fill(M); stroke(D); strokeWeight(2);
  quad(lx-46,by-74,lx+46,by-74,lx+52,by-67,lx-52,by-67);
  quad(lx-52,by-78,lx+52,by-78,lx+58,by-70,lx-58,by-70);
  fill(C); stroke(D); strokeWeight(2.5);
  beginShape(); vertex(lx-38,by-78); vertex(lx+38,by-78); vertex(lx+46,by-102); vertex(lx+32,by-124); vertex(lx,by-132); vertex(lx-32,by-124); vertex(lx-46,by-102); endShape(CLOSE);
  stroke(D); strokeWeight(1.5); noFill(); line(lx-38,by-78,lx-32,by-124); line(lx+38,by-78,lx+32,by-124); line(lx,by-78,lx,by-132);
  fill(M); stroke(D); strokeWeight(2); quad(lx-6,by-132,lx+6,by-132,lx+3,by-162,lx-3,by-162);
  fill(D); stroke(D); strokeWeight(1.5);
  beginShape(); vertex(lx-30,by-114); vertex(lx-38,by-120); vertex(lx-64,by-158); vertex(lx-56,by-158); vertex(lx-30,by-122); endShape(CLOSE);
  beginShape(); vertex(lx+30,by-114); vertex(lx+38,by-120); vertex(lx+64,by-158); vertex(lx+56,by-158); vertex(lx+30,by-122); endShape(CLOSE);
  fill(M); stroke(D); strokeWeight(2); quad(lx-30,by-74,lx+30,by-74,lx+26,by-52,lx-26,by-52);
  stroke(D); strokeWeight(1.5); noFill(); line(lx-22,by-66,lx+22,by-66);
  let ex=lx,ey=by-92;
  if (st==="idle"||st==="sleepy") { stroke(D); strokeWeight(2); noFill(); line(ex-15,ey,ex-4,ey); line(ex+4,ey,ex+15,ey); }
  else if (st==="happy"||st==="excited") { fill(color(30,30,40)); noStroke(); circle(ex-10,ey,11); circle(ex+10,ey,11); fill(255); circle(ex-9,ey-1,4); circle(ex+11,ey-1,4); }
  else if (st==="surprised"||st==="scared") { fill(color(30,30,40)); noStroke(); circle(ex-10,ey,13); circle(ex+10,ey,13); fill(255); circle(ex-9,ey-1,5); circle(ex+11,ey-1,5); }
  else if (st==="sad") { stroke(D); strokeWeight(2); noFill(); line(ex-15,ey+3,ex-4,ey); line(ex+4,ey,ex+15,ey+3); }
  else { fill('#e03030'); noStroke(); circle(ex-10,ey,11); circle(ex+10,ey,11); stroke(D); strokeWeight(2.5); noFill(); line(ex-18,ey-10,ex-4,ey-4); line(ex+4,ey-4,ex+18,ey-10); }
  fill(M); stroke(D); strokeWeight(2);
  quad(lx-66,by-8,lx-66,by+8,lx-92+sin(armSwing)*32,by+30+cos(armSwing)*20,lx-88+sin(armSwing)*32,by+18+cos(armSwing)*20);
  let lhx=lx-94+sin(armSwing)*36,lhy=by+36+cos(armSwing)*22;
  fill(D); quad(lhx-12,lhy-9,lhx+12,lhy-9,lhx+14,lhy+9,lhx-14,lhy+9);
  fill(M); stroke(D); strokeWeight(2);
  quad(lx+66,by-8,lx+66,by+8,lx+88-sin(armSwing)*22,by+26,lx+84-sin(armSwing)*22,by+14);
  let rhx=lx+90-sin(armSwing)*24,rhy=by+30;
  fill(D); quad(rhx-12,rhy-9,rhx+12,rhy-9,rhx+14,rhy+9,rhx-12,rhy+9);
  let sAngle=st==="angry"?-PI*.42+sin(breathe*5)*.35:st==="excited"?-PI*.5+sin(breathe*4)*.4:st==="happy"?-PI*.32+handLR*.2:-PI*.28;
  let bx2=rhx+cos(sAngle)*130,by2=rhy+sin(sAngle)*130;
  push(); translate(rhx,rhy); rotate(sAngle);
  fill(220,230,255); stroke(D); strokeWeight(1.5); rect(0,-3,130,6,1);
  stroke(255,255,255,180); strokeWeight(1); line(0,0,130,0);
  fill(D); stroke(D); strokeWeight(1); quad(0,-14,10,0,0,14,-10,0);
  fill(M); stroke(D); strokeWeight(2); rect(-32,-5,32,10,2);
  pop();
  fill(C); stroke(D); strokeWeight(2);
  for (let i=-3;i<=3;i++) { let px=lx+i*17; quad(px-8,by+62,px+8,by+62,px+10,by+94,px-10,by+94); }
  stroke(D); strokeWeight(2); noFill(); line(lx,by+62,lx,by+94);
  let llx=lx-22+sin(legLR)*20+sin(legSwing)*28,rlx=lx+22-sin(legLR)*20-sin(legSwing)*28;
  fill(M); stroke(D); strokeWeight(2);
  quad(lx-26,by+92,lx-18,by+92,llx+12,by+124,llx-12,by+124);
  quad(llx-14,by+122,llx+14,by+122,llx+16,by+138,llx-16,by+138);
  quad(lx+18,by+92,lx+26,by+92,rlx+12,by+124,rlx-12,by+124);
  quad(rlx-14,by+122,rlx+14,by+122,rlx+16,by+138,rlx-16,by+138);
  stroke(180,180,180,140); strokeWeight(1.5);
  line(lx,by-162,lx,by-210); line(lx-96,by+4,lx-96,by-106); line(bx2,by2,bx2,by2-100);
  pop();
}
"""Convierte la app de Claude (mi-dieta-semanal.html) en la web independiente con usuarios
web-dieta/index.html: cada persona entra con su email y contraseña y solo ve SUS datos (Supabase).

Uso:  .venv\\Scripts\\python.exe -I herramientas\\construir_web_dieta.py

Si cambias la app de Claude, vuelve a ejecutarlo y sube web-dieta a GitHub (se publica sola).
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "mi-dieta-semanal.html"
DST = RAIZ / "web-dieta" / "index.html"

SB_URL = "https://eralhpnstnbyznwthkmz.supabase.co"
SB_KEY = "sb_publishable_8_hwEm1tK5NS3G0iRbj9kw_CZMsvBbu"   # clave pública: la seguridad la ponen las reglas de Supabase

HEAD = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0E0E0E">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Mi Dieta">
<link rel="icon" href="icono.png">
<link rel="apple-touch-icon" href="icono.png">
<link rel="manifest" href="manifest.webmanifest">
<style>*,*::before,*::after{box-sizing:border-box}html,body{margin:0}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}img{max-width:100%}[hidden]{display:none!important}</style>
"""

SHIM = r"""<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.110.0/dist/umd/supabase.js"></script>
<style>
/* Pantalla de entrada (cuentas de usuario) */
#auth{position:fixed;inset:0;z-index:50;background:var(--band);color:var(--band-ink);display:grid;place-items:center;overflow:auto;padding:24px max(16px,env(safe-area-inset-right,0px)) 24px max(16px,env(safe-area-inset-left,0px))}
#auth::before{content:"";position:fixed;left:0;right:0;bottom:0;height:14px;background:repeating-linear-gradient(-45deg,var(--hi) 0 14px,var(--band) 14px 28px)}
#auth .abox{width:100%;max-width:400px;display:grid;gap:16px}
#auth .atitle{font-family:var(--f-title);text-transform:uppercase;font-size:clamp(2.2rem,11vw,3.2rem);line-height:.95;text-align:center;margin:0}
#auth .atitle span{color:var(--hi);font-style:italic;display:inline-block;transform:skewX(-7deg)}
#auth .asub{text-align:center;color:var(--band-muted);margin:0}
#auth form{background:var(--surface);color:var(--fg);border-radius:18px;padding:18px;display:grid;gap:12px;box-shadow:0 20px 50px rgba(0,0,0,.4)}
#auth form h2{margin:0;font-family:var(--f-display);text-transform:uppercase;font-size:1.4rem}
#auth .alinks{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;font-size:.88rem}
#auth .alinks button{background:none;border:0;padding:0;color:var(--fg);text-decoration:underline;text-decoration-color:var(--hi);text-decoration-thickness:2px;text-underline-offset:3px;font-weight:600}
#auth .amsg{min-height:1.3em;font-size:.9rem;margin:0}
#auth .amsg.err{color:var(--bad)} #auth .amsg.ok{color:var(--good)}
.userbar{display:flex;justify-content:flex-end;align-items:center;gap:10px;width:100%;font-size:.78rem;color:var(--band-muted)}
.userbar span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0}
.userbar button{background:transparent;border:1px solid rgba(255,255,255,.3);color:var(--band-ink);border-radius:8px;padding:3px 10px;font:inherit;font-weight:700;cursor:pointer}
</style>
<script>
/* Puente con Supabase: imita la base de datos y las fotos de claude.ai, con cuentas de usuario.
   Cada usuario solo lee y escribe sus filas (reglas de seguridad de Supabase). */
const SB_URL='%SB_URL%',SB_KEY='%SB_KEY%';
const SB=supabase.createClient(SB_URL,SB_KEY,{auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:true,storageKey:'mi-dieta-semanal'}});
const CAT_BASE=SB_URL+'/storage/v1/object/public/catalogo/mercadona/';
const fotoUrl=id=>SB_URL+'/storage/v1/object/public/dieta-fotos/'+String(id).split('/').map(encodeURIComponent).join('/');
let UID=null,EMAIL='';let authResolve;const AUTH_READY=new Promise(r=>authResolve=r);
const newId=()=>(crypto.randomUUID?crypto.randomUUID():Date.now().toString(36)+Math.random().toString(36).slice(2)).replace(/-/g,'');
const SBDB=(()=>{
  const W={},timers={};let chan=null;
  const META={fromCache:false,hasPendingWrites:false};
  const fire=col=>{clearTimeout(timers[col]);timers[col]=setTimeout(()=>(W[col]||new Set()).forEach(f=>f()),100)};
  const fireAll=()=>Object.keys(W).forEach(fire);
  const listen=()=>{if(chan)return;chan=SB.channel('dieta-'+UID).on('postgres_changes',{event:'*',schema:'public',table:'dieta_docs',filter:'user_id=eq.'+UID},p=>{const c=(p.new&&p.new.col)||(p.old&&p.old.col);c?fire(c):fireAll()}).subscribe(s=>{if(s==='SUBSCRIBED')fireAll()})};
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)fireAll()});
  const err=e=>{const x=new Error((e&&e.message)||'error');x.code=(e&&e.code)||'unavailable';return x};
  const watch=(col,f)=>{(W[col]||(W[col]=new Set())).add(f);listen();f();return()=>{W[col]&&W[col].delete(f)}};
  const merge=(a,b)=>{if(!a||typeof a!=='object'||Array.isArray(a)||!b||typeof b!=='object'||Array.isArray(b))return b;const o={...a};for(const k in b)o[k]=merge(a[k],b[k]);return o};
  const docRef=(col,id)=>({id,path:col+'/'+id,
    async get(){const{data,error}=await SB.from('dieta_docs').select('data').eq('col',col).eq('id',id).maybeSingle();if(error)throw err(error);return{id,exists:!!data,data:()=>data?data.data:undefined,metadata:META}},
    async set(d){const{error}=await SB.from('dieta_docs').upsert({user_id:UID,col,id,data:d,updated_at:new Date().toISOString()},{onConflict:'user_id,col,id'});if(error)throw err(error);fire(col)},
    async update(d){const s=await this.get();if(!s.exists)throw err({code:'invalid_argument',message:'no existe'});await this.set(merge(s.data(),d))},
    async delete(){const{error}=await SB.from('dieta_docs').delete().eq('col',col).eq('id',id);if(error)throw err(error);fire(col)},
    onSnapshot(next,onErr){const r=this;return watch(col,async()=>{try{next(await r.get())}catch(e){onErr&&onErr(e)}})}});
  const colRef=col=>{const q={path:col,
    doc:id=>docRef(col,id||newId()),
    async add(d){const r=docRef(col,newId());await r.set(d);return r},
    async get(){const{data,error}=await SB.from('dieta_docs').select('id,data').eq('col',col).limit(2000);if(error)throw err(error);const docs=(data||[]).map(r=>({id:r.id,exists:true,data:()=>r.data,metadata:META}));return{docs,size:docs.length,empty:!docs.length,metadata:META,docChanges:()=>[]}},
    onSnapshot(next,onErr){return watch(col,async()=>{try{next(await q.get())}catch(e){onErr&&onErr(e)}})},
    where(){return q},orderBy(){return q},limit(){return q}};return q};
  return{doc:p=>{const i=p.lastIndexOf('/');return docRef(p.slice(0,i),p.slice(i+1))},collection:colRef};
})();
const SBASSETS={
  async upload(blob,o){const id=UID+'/'+newId()+'.jpg';const{error}=await SB.storage.from('dieta-fotos').upload(id,blob,{contentType:(o&&o.type)||'image/jpeg',upsert:false});
    if(error){const x=new Error(error.message);x.code=/size|large/i.test(error.message)?'too_large':'upstream_error';throw x}return{id,url:fotoUrl(id)}},
  async delete(id){await SB.storage.from('dieta-fotos').remove([id]);return{deleted:true}}};
window.claude={use:async name=>{await AUTH_READY;return name==='db'?SBDB:name==='assets'?SBASSETS:null}};
window.DIETA_PLANTILLA=async()=>{const{data,error}=await SB.from('dieta_plantillas').select('plan,platos').eq('id','fit24x7').single();if(error)throw error;return data};

/* ----- Entrar, crear cuenta, recuperar contraseña ----- */
const ESC=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const BASE=location.origin+location.pathname;
let AMODE='login';
const ERRS=[[/invalid login/i,'Email o contraseña incorrectos.'],[/not confirmed/i,'Todavía no has confirmado tu cuenta: abre el enlace del correo que te enviamos.'],[/already registered|already been registered/i,'Ya existe una cuenta con ese email. Entra o recupera la contraseña.'],[/rate limit|too many/i,'Demasiados intentos. Espera unos minutos y vuelve a probar.'],[/at least 6|password should/i,'La contraseña debe tener al menos 6 caracteres.'],[/valid email|invalid email|unable to validate email/i,'Ese email no parece válido.'],[/signups? not allowed|disabled/i,'Ahora mismo no se pueden crear cuentas nuevas.']];
const errTxt=e=>{const m=(e&&e.message)||'';const f=ERRS.find(([r])=>r.test(m));return f?f[1]:'No se pudo completar. Revisa tu conexión y vuelve a probar.'};
function showAuth(mode,msg,ok){
  AMODE=mode;let el=document.getElementById('auth');
  if(!el){el=document.createElement('div');el.id='auth';el.setAttribute('role','dialog');el.setAttribute('aria-modal','true');document.body.appendChild(el)}
  const em=ESC(el.dataset.email||'');
  const F={
    login:`<h2>Entrar</h2><label class="f">Email<input id="a_em" type="email" autocomplete="username" required value="${em}"></label><label class="f">Contraseña<input id="a_pw" type="password" autocomplete="current-password" required></label><button class="btn primary">Entrar</button><div class="alinks"><button type="button" data-am="signup">Crear una cuenta</button><button type="button" data-am="forgot">He olvidado la contraseña</button></div>`,
    signup:`<h2>Crear cuenta</h2><label class="f">Email<input id="a_em" type="email" autocomplete="username" required value="${em}"></label><label class="f">Contraseña (mínimo 6 caracteres)<input id="a_pw" type="password" autocomplete="new-password" minlength="6" required></label><label class="f">Repite la contraseña<input id="a_pw2" type="password" autocomplete="new-password" minlength="6" required></label><button class="btn primary">Crear cuenta</button><div class="alinks"><button type="button" data-am="login">Ya tengo cuenta</button></div>`,
    forgot:`<h2>Recuperar contraseña</h2><label class="f">Email de tu cuenta<input id="a_em" type="email" autocomplete="username" required value="${em}"></label><button class="btn primary">Enviarme un enlace</button><div class="alinks"><button type="button" data-am="login">Volver a entrar</button></div>`,
    newpass:`<h2>Nueva contraseña</h2><label class="f">Contraseña nueva (mínimo 6 caracteres)<input id="a_pw" type="password" autocomplete="new-password" minlength="6" required></label><button class="btn primary">Guardar contraseña</button>`};
  el.innerHTML=`<div class="abox"><h1 class="atitle">Mi Dieta <span>Semanal</span></h1><p class="asub">Tu dieta, tu menú, tu compra y tu entreno. Cada cuenta ve solo sus datos.</p><form id="aform" novalidate>${F[mode]}<p class="amsg ${ok?'ok':'err'}" role="status">${ESC(msg||'')}</p></form></div>`;
  el.hidden=false;setTimeout(()=>{const i=el.querySelector('input:not([value]),input[value=""]')||el.querySelector('input');i&&i.focus()},30);
}
function hideAuth(){const el=document.getElementById('auth');if(el)el.hidden=true}
function signedIn(s){
  if(UID)return;UID=s.user.id;EMAIL=s.user.email||'';hideAuth();
  const hi=document.querySelector('.hero-in');
  if(hi&&!document.querySelector('.userbar'))hi.insertAdjacentHTML('afterbegin',`<div class="userbar"><span>${ESC(EMAIL)}</span><button type="button" id="logout">Salir</button></div>`);
  authResolve();
}
document.addEventListener('click',e=>{
  const b=e.target.closest('[data-am]');if(b){const el=document.getElementById('auth');const em=document.getElementById('a_em');if(em)el.dataset.email=em.value;showAuth(b.dataset.am);return}
  if(e.target.id==='logout'){SB.auth.signOut().finally(()=>location.reload())}
});
document.addEventListener('submit',async e=>{
  if(e.target.id!=='aform')return;e.preventDefault();
  const msg=e.target.querySelector('.amsg'),btn=e.target.querySelector('.btn.primary');
  const say=(t,ok)=>{msg.textContent=t;msg.className='amsg '+(ok?'ok':'err')};
  const em=(document.getElementById('a_em')||{}).value?.trim(),pw=(document.getElementById('a_pw')||{}).value||'';
  if(AMODE!=='newpass'&&!em){say('Escribe tu email.');return}
  if(AMODE!=='forgot'&&pw.length<6){say('La contraseña debe tener al menos 6 caracteres.');return}
  if(AMODE==='signup'&&pw!==document.getElementById('a_pw2').value){say('Las dos contraseñas no coinciden.');return}
  btn.disabled=true;say('Un momento…',true);
  try{
    if(AMODE==='login'){const{data,error}=await SB.auth.signInWithPassword({email:em,password:pw});if(error)throw error;signedIn(data.session)}
    else if(AMODE==='signup'){const{data,error}=await SB.auth.signUp({email:em,password:pw,options:{emailRedirectTo:BASE}});if(error)throw error;
      if(data.session)signedIn(data.session);else{document.getElementById('auth').dataset.email=em;showAuth('login','Cuenta creada. Te hemos enviado un correo: abre el enlace para confirmarla y después entra aquí.',true)}}
    else if(AMODE==='forgot'){const{error}=await SB.auth.resetPasswordForEmail(em,{redirectTo:BASE});if(error)throw error;say('Si existe una cuenta con ese email, te llegará un enlace para poner una contraseña nueva.',true)}
    else if(AMODE==='newpass'){const{data,error}=await SB.auth.updateUser({password:pw});if(error)throw error;const s=(await SB.auth.getSession()).data.session;if(s)signedIn(s)}
  }catch(err){say(errTxt(err))}finally{btn.disabled=false}
});
SB.auth.onAuthStateChange((ev,session)=>{
  if(ev==='PASSWORD_RECOVERY'){showAuth('newpass');return}
  if(ev==='SIGNED_IN'&&session&&AMODE!=='newpass')signedIn(session);
  if(ev==='SIGNED_OUT'&&UID)location.reload();
});
(async()=>{let s=null;try{s=(await SB.auth.getSession()).data.session}catch(_){}if(s&&AMODE!=='newpass')signedIn(s);else if(!UID)showAuth(AMODE==='newpass'?'newpass':'login')})();
</script>
"""

MANIFEST = """{
  "name": "Mi Dieta Semanal",
  "short_name": "Mi Dieta",
  "start_url": ".",
  "display": "standalone",
  "background_color": "#0E0E0E",
  "theme_color": "#0E0E0E",
  "icons": [{"src": "icono.png", "sizes": "512x512", "type": "image/png"}]
}
"""


def sub1(s, pat, rep):
    n = s.count(pat)
    if n != 1:
        sys.exit(f"No encuentro una sola vez: {pat!r} ({n})")
    return s.replace(pat, rep)


def main():
    s = SRC.read_text(encoding="utf-8")
    s = sub1(s, '<meta name="claude:viewport-fit-sides" content="cover">\n', "")
    s = HEAD + s
    s = s.replace("</style>", "</style>\n</head>\n<body>", 1)
    s = sub1(s, "<script>\n(() => {", SHIM.replace("%SB_URL%", SB_URL).replace("%SB_KEY%", SB_KEY) + "<script>\n(() => {")
    s = sub1(s, 'fetch("catalogo/mercadona/mercadona.json")', 'fetch(CAT_BASE+"mercadona.json")')
    s = sub1(s, "url(catalogo/mercadona/s${+r[6]}.jpg)", "url(${CAT_BASE}s${+r[6]}.jpg)")
    s = sub1(s, 'src="/_blob/${esc(p.foto)}"', 'src="${esc(fotoUrl(p.foto))}"')
    s = sub1(s, '<div class="btnrow"><button class="btn primary" data-act="askclaude">Pedir consejo a Claude</button></div>', "")
    s = sub1(s, 'setStatus("Sin guardado: abre la página con tu cuenta");', 'setStatus("No se pudo conectar: recarga la página");')
    if "/_blob/" in s or "catalogo/mercadona/" in s.replace("public/catalogo/mercadona/", ""):
        sys.exit("Queda alguna ruta de Claude sin cambiar")
    s += "\n</body>\n</html>\n"
    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(s, encoding="utf-8")
    (DST.parent / "manifest.webmanifest").write_text(MANIFEST, encoding="utf-8")
    (DST.parent / ".nojekyll").write_text("", encoding="utf-8")
    print("OK", DST, len(s), "bytes")


if __name__ == "__main__":
    main()

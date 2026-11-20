import os
import json
import urllib.request
from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session, Response

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "nekoplay_chave_secreta_9988")

SENHA_ADMIN = os.environ.get("SENHA_ADMIN", "253014")
JSONBIN_BIN_ID = os.environ.get("JSONBIN_BIN_ID", "6aff8d98ffd5d16053cfd037")
JSONBIN_API_KEY = os.environ.get("JSONBIN_API_KEY", "$2a$10$atMn20HWWrMzR2V28efpzO0udonspSMVibkF9Bj23Howd60eQQkNi")
ARQUIVO_LOCAL = "catalogo_local.json"

def carregar_catalogo():
    if JSONBIN_BIN_ID and JSONBIN_API_KEY:
        try:
            url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest"
            req = urllib.request.Request(url, headers={
                "X-Master-Key": JSONBIN_API_KEY,
                "User-Agent": "NekoPlay-Server/1.0"
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                dados = json.loads(resp.read().decode("utf-8"))
                record = dados.get("record", {})
                if "_vazio" in record:
                    record.pop("_vazio")
                return record
        except Exception as e:
            print("Erro ao ler JSONBin:", e)
    if os.path.exists(ARQUIVO_LOCAL):
        with open(ARQUIVO_LOCAL, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_catalogo(dados):
    if JSONBIN_BIN_ID and JSONBIN_API_KEY:
        try:
            url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
            payload = dados if dados else {"_vazio": True}
            corpo = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(url, data=corpo, method="PUT", headers={
                "Content-Type": "application/json",
                "X-Master-Key": JSONBIN_API_KEY,
                "User-Agent": "NekoPlay-Server/1.0"
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                return True
        except Exception as e:
            print("Erro ao salvar no JSONBin:", e)
    with open(ARQUIVO_LOCAL, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    return True

# ================= ROTAS DA API E PWA =================

@app.route("/api/catalogo")
def api_catalogo():
    return jsonify(carregar_catalogo())

@app.route("/manifest.json")
def manifest():
    return jsonify({
        "name": "nekoplay",
        "short_name": "nekoplay",
        "start_url": "/app",
        "display": "standalone",
        "background_color": "#000000",
        "theme_color": "#9d4edd",
        "orientation": "any",
        "icons": [
            {
                "src": "/icon.svg",
                "sizes": "512x512",
                "type": "image/svg+xml",
                "purpose": "any maskable"
            }
        ]
    })

@app.route("/icon.svg")
def icon_svg():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
      <rect width="512" height="512" rx="110" fill="#141519"/>
      <path d="M120 210 L135 95 L220 165 Q256 155 292 165 L377 95 L392 210 Q425 255 415 315 Q395 405 256 410 Q117 405 97 315 Q87 255 120 210 Z" fill="#9d4edd"/>
      <ellipse cx="205" cy="285" rx="18" ry="26" fill="#ffffff"/>
      <ellipse cx="307" cy="285" rx="18" ry="26" fill="#ffffff"/>
    </svg>"""
    return Response(svg, mimetype="image/svg+xml")

# ================= TELA MOBILE / ANDROID (/app) =================

HTML_APP_MOBILE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <meta name="theme-color" content="#9d4edd">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <link rel="manifest" href="/manifest.json">
  <link rel="icon" href="/icon.svg" type="image/svg+xml">
  <title>nekoplay</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Roboto, sans-serif; -webkit-tap-highlight-color: transparent; }
    body { background: #000000; color: #ffffff; padding-bottom: 40px; overflow-x: hidden; }
    header {
      position: sticky; top: 0; z-index: 50; background: #141519;
      padding: 12px 16px; display: flex; align-items: center; justify-content: space-between;
      border-bottom: 1px solid #23252b;
    }
    .brand { display: flex; align-items: center; gap: 10px; cursor: pointer; }
    .brand img { width: 32px; height: 32px; }
    .brand span { font-size: 22px; font-weight: 800; color: #9d4edd; letter-spacing: -0.5px; }
    .search-box {
      background: #23252b; border: none; color: #fff; padding: 8px 12px;
      border-radius: 6px; width: 145px; font-size: 14px; outline: none;
    }
    .search-box:focus { width: 180px; border: 1px solid #9d4edd; }
    .container { padding: 16px; max-width: 900px; margin: 0 auto; }
    .section-title { font-size: 18px; font-weight: 700; margin: 12px 0 14px; display: flex; align-items: center; gap: 8px; }
    .section-title::before { content: ""; width: 4px; height: 18px; background: #9d4edd; border-radius: 2px; }
    
    /* Continuar Assistindo */
    .continue-row { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 10px; scrollbar-width: none; }
    .continue-row::-webkit-scrollbar { display: none; }
    .continue-card {
      min-width: 170px; max-width: 170px; background: #141519; border-radius: 6px; overflow: hidden;
      border: 1px solid #23252b; cursor: pointer; position: relative;
    }
    .continue-card img { width: 100%; height: 96px; object-fit: cover; display: block; background: #1c1d22; }
    .continue-info { padding: 8px; }
    .continue-info h4 { font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .continue-info p { font-size: 11px; color: #a0a0a0; margin-top: 2px; }
    .progress-bar-bg { height: 3px; background: #2c2e36; width: 100%; }
    .progress-bar-fill { height: 100%; background: #9d4edd; }

    /* Grade de Animes */
    .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
    @media (min-width: 600px) { .grid { grid-template-columns: repeat(4, 1fr); } }
    .poster-card { cursor: pointer; transition: transform 0.15s; }
    .poster-card:active { transform: scale(0.97); }
    .poster-wrap {
      width: 100%; aspect-ratio: 2 / 3; background: #141519; border-radius: 6px;
      overflow: hidden; border: 1px solid #23252b;
    }
    .poster-wrap img { width: 100%; height: 100%; object-fit: cover; display: block; }
    .poster-title { font-size: 14px; font-weight: 700; margin-top: 6px; line-height: 1.2; }
    .poster-sub { font-size: 12px; color: #8c8c8c; margin-top: 2px; }

    /* Tela de Detalhes (Hero Banner Degrade) */
    #view-detalhes { display: none; }
    .hero { position: relative; width: 100%; height: 320px; overflow: hidden; }
    .hero img { width: 100%; height: 100%; object-fit: cover; object-position: center top; }
    .hero-gradient {
      position: absolute; inset: 0;
      background: linear-gradient(to top, #000000 8%, rgba(0,0,0,0.65) 55%, rgba(0,0,0,0.2) 100%);
    }
    .btn-voltar {
      position: absolute; top: 14px; left: 14px; z-index: 10;
      background: rgba(20, 21, 25, 0.85); color: #fff; border: 1px solid #333;
      padding: 8px 14px; border-radius: 20px; font-size: 13px; font-weight: 700; cursor: pointer;
    }
    .hero-content { position: absolute; bottom: 16px; left: 16px; right: 16px; }
    .hero-content h1 { font-size: 24px; font-weight: 800; text-shadow: 0 2px 8px #000; }
    .hero-content p { font-size: 13px; color: #c77dff; font-weight: 600; margin-top: 4px; }
    .btn-play-hero {
      margin-top: 12px; width: 100%; background: #9d4edd; color: #fff; border: none;
      padding: 13px; border-radius: 6px; font-size: 15px; font-weight: 800; cursor: pointer;
    }

    /* Lista de Episodios */
    .ep-list { padding: 10px 16px; display: flex; flex-direction: column; gap: 10px; }
    .ep-item {
      background: #141519; border: 1px solid #23252b; border-radius: 8px;
      padding: 14px; display: flex; align-items: center; justify-content: space-between; cursor: pointer;
    }
    .ep-item:active { border-color: #9d4edd; background: #1d1a26; }
    .ep-item-title { font-size: 14px; font-weight: 700; }
    .ep-item-status { font-size: 12px; color: #9d4edd; font-weight: 600; }

    /* Player Customizado com Auto-Hide em 5s */
    #view-player {
      display: none; position: fixed; inset: 0; background: #000; z-index: 100;
      align-items: center; justify-content: center; user-select: none;
    }
    video { width: 100%; height: 100%; object-fit: contain; background: #000; }

    .overlay-controles {
      position: absolute; inset: 0; display: flex; flex-direction: column;
      justify-content: space-between; z-index: 10;
      transition: opacity 0.35s ease; opacity: 1; pointer-events: none;
    }
    .overlay-controles.oculto { opacity: 0; }
    .overlay-controles:not(.oculto) .player-top,
    .overlay-controles:not(.oculto) .player-center,
    .overlay-controles:not(.oculto) .player-bottom { pointer-events: auto; }

    .player-top {
      padding: 16px; background: linear-gradient(to bottom, rgba(0,0,0,0.88), transparent);
      display: flex; align-items: center; justify-content: space-between;
    }
    .player-top span { font-size: 15px; font-weight: 700; max-width: 72%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .btn-fechar-player { background: rgba(35, 37, 43, 0.9); color: #fff; border: 1px solid #3c3f4a; padding: 8px 14px; border-radius: 6px; font-weight: 700; font-size: 13px; }

    .player-center {
      display: flex; align-items: center; justify-content: center; gap: 36px;
    }
    .btn-circle {
      width: 52px; height: 52px; border-radius: 50%; background: rgba(20, 21, 25, 0.75);
      border: 1px solid rgba(255,255,255,0.2); color: #fff; font-size: 15px; font-weight: 700;
      display: flex; align-items: center; justify-content: center;
    }
    .btn-play-center {
      width: 66px; height: 66px; border-radius: 50%; background: #9d4edd;
      border: none; color: #fff; font-size: 26px; display: flex; align-items: center; justify-content: center;
      box-shadow: 0 0 20px rgba(157, 78, 221, 0.5);
    }

    .player-bottom {
      padding: 16px; background: linear-gradient(to top, rgba(0,0,0,0.92), transparent);
      display: flex; flex-direction: column; gap: 10px;
    }
    .seek-row { display: flex; align-items: center; gap: 10px; }
    .time-txt { font-size: 12px; color: #ddd; font-variant-numeric: tabular-nums; min-width: 40px; }
    input[type="range"].seek-bar {
      flex: 1; -webkit-appearance: none; height: 4px; background: rgba(255,255,255,0.25);
      border-radius: 2px; outline: none;
    }
    input[type="range"].seek-bar::-webkit-slider-thumb {
      -webkit-appearance: none; width: 15px; height: 15px; border-radius: 50%;
      background: #9d4edd; cursor: pointer;
    }
    .actions-row { display: flex; align-items: center; justify-content: space-between; }
    .btn-action {
      background: rgba(35, 37, 43, 0.9); color: #fff; border: 1px solid #3c3f4a;
      padding: 8px 13px; border-radius: 6px; font-weight: 700; font-size: 13px;
    }
    .btn-next {
      background: #9d4edd; color: #fff; border: none;
      padding: 8px 14px; border-radius: 6px; font-weight: 700; font-size: 13px;
    }
    .loading { text-align: center; padding: 50px 20px; color: #a0a0a0; }
  </style>
</head>
<body>

  <header id="topo">
    <div class="brand" onclick="voltarCatalogo()">
      <img src="/icon.svg" alt="logo">
      <span>nekoplay</span>
    </div>
    <input type="text" id="busca" class="search-box" placeholder="Buscar anime..." oninput="filtrarAnimes()">
  </header>

  <div id="view-catalogo" class="container">
    <div id="sec-continuar" style="display:none;">
      <div class="section-title">Continuar Assistindo</div>
      <div id="lista-continuar" class="continue-row"></div>
    </div>

    <div class="section-title">Animes Disponíveis</div>
    <div id="loading" class="loading">Carregando catálogo...</div>
    <div id="grade-animes" class="grid"></div>
  </div>

  <div id="view-detalhes">
    <div class="hero">
      <button class="btn-voltar" onclick="voltarCatalogo()">← Voltar</button>
      <img id="det-banner" src="" alt="">
      <div class="hero-gradient"></div>
      <div class="hero-content">
        <h1 id="det-titulo"></h1>
        <p id="det-qtd"></p>
        <button id="det-btn-play" class="btn-play-hero">▶ Assistir</button>
      </div>
    </div>
    <div id="det-episodios" class="ep-list"></div>
  </div>

  <div id="view-player">
    <video id="video-el" playsinline webkit-playsinline></video>
    
    <div id="overlay-controles" class="overlay-controles">
      <div class="player-top">
        <span id="player-titulo"></span>
        <button class="btn-fechar-player" onclick="fecharPlayer()">✕ Fechar</button>
      </div>

      <div class="player-center">
        <button class="btn-circle" onclick="pularTempo(-10)">-10s</button>
        <button id="btn-play-pause" class="btn-play-center" onclick="alternarPlay()">⏸</button>
        <button class="btn-circle" onclick="pularTempo(10)">+10s</button>
      </div>

      <div class="player-bottom">
        <div class="seek-row">
          <span id="txt-atual" class="time-txt">00:00</span>
          <input type="range" id="seek-bar" class="seek-bar" min="0" max="1000" value="0">
          <span id="txt-total" class="time-txt" style="text-align:right;">00:00</span>
        </div>
        <div class="actions-row">
          <button class="btn-action" onclick="alternarTelaCheia()">⛶ Tela Cheia</button>
          <button id="btn-proximo" class="btn-next" onclick="tocarProximo()">Próximo Ep ⏭</button>
        </div>
      </div>
    </div>
  </div>

  <script>
    let catalogo = {};
    let animeAtual = "";
    let epIndexAtual = 0;
    let timerOcultar = null;
    let arrastandoSeek = false;

    const viewPlayer = document.getElementById("view-player");
    const videoEl = document.getElementById("video-el");
    const overlay = document.getElementById("overlay-controles");
    const seekBar = document.getElementById("seek-bar");
    const btnPlayPause = document.getElementById("btn-play-pause");

    // --- AUTO-HIDE DOS CONTROLES APOS 5 SEGUNDOS ---
    function mostrarControlesTemporariamente() {
      overlay.classList.remove("oculto");
      clearTimeout(timerOcultar);
      if (!videoEl.paused) {
        timerOcultar = setTimeout(() => {
          if (!arrastandoSeek && !videoEl.paused) {
            overlay.classList.add("oculto");
          }
        }, 5000);
      }
    }

    // Tocar na area do video alterna entre mostrar e esconder imediatamente
    videoEl.addEventListener("click", () => {
      if (overlay.classList.contains("oculto")) {
        mostrarControlesTemporariamente();
      } else {
        clearTimeout(timerOcultar);
        overlay.classList.add("oculto");
      }
    });

    // Qualquer interacao nos botoes ou barra reinicia os 5 segundos
    overlay.addEventListener("touchstart", mostrarControlesTemporariamente, { passive: true });
    overlay.addEventListener("mousemove", mostrarControlesTemporariamente);
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) {
        clearTimeout(timerOcultar);
        overlay.classList.add("oculto");
      } else {
        mostrarControlesTemporariamente();
      }
    });

    function alternarPlay() {
      if (videoEl.paused) {
        videoEl.play();
        btnPlayPause.innerText = "⏸";
        mostrarControlesTemporariamente();
      } else {
        videoEl.pause();
        btnPlayPause.innerText = "▶";
        clearTimeout(timerOcultar);
        overlay.classList.remove("oculto");
      }
    }

    function pularTempo(segundos) {
      videoEl.currentTime = Math.max(0, Math.min(videoEl.duration || 0, videoEl.currentTime + segundos));
      mostrarControlesTemporariamente();
    }

    function alternarTelaCheia() {
      if (!document.fullscreenElement) {
        if (viewPlayer.requestFullscreen) viewPlayer.requestFullscreen();
        else if (videoEl.webkitEnterFullscreen) videoEl.webkitEnterFullscreen();
      } else {
        if (document.exitFullscreen) document.exitFullscreen();
      }
      mostrarControlesTemporariamente();
    }

    seekBar.addEventListener("input", () => {
      arrastandoSeek = true;
      mostrarControlesTemporariamente();
      if (videoEl.duration) {
        document.getElementById("txt-atual").innerText = formatarTempo((seekBar.value / 1000) * videoEl.duration);
      }
    });

    seekBar.addEventListener("change", () => {
      if (videoEl.duration) {
        videoEl.currentTime = (seekBar.value / 1000) * videoEl.duration;
      }
      arrastandoSeek = false;
      mostrarControlesTemporariamente();
    });

    // --- PROGRESSO E CATALOGO ---
    function getProgresso() {
      try { return JSON.parse(localStorage.getItem("nekoplay_prog") || "{}"); }
      catch { return {}; }
    }

    function salvarProgresso(anime, idx, tempo, duracao) {
      if (!duracao || duracao < 10) return;
      const prog = getProgresso();
      const pct = tempo / duracao;
      prog[anime] = { idx, tempo, duracao, concluido: pct >= 0.9 };
      localStorage.setItem("nekoplay_prog", JSON.stringify(prog));
    }

    function formatarTempo(seg) {
      if (!seg || seg <= 0 || isNaN(seg)) return "00:00";
      const m = Math.floor(seg / 60);
      const s = Math.floor(seg % 60);
      return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
    }

    async function iniciar() {
      try {
        const res = await fetch("/api/catalogo");
        catalogo = await res.json();
        document.getElementById("loading").style.display = "none";
        renderizarCatalogo();
      } catch (e) {
        document.getElementById("loading").innerText = "Erro ao conectar ao servidor.";
      }
    }

    function renderizarCatalogo(filtro = "") {
      const grade = document.getElementById("grade-animes");
      grade.innerHTML = "";
      const prog = getProgresso();

      const rowCont = document.getElementById("lista-continuar");
      rowCont.innerHTML = "";
      let temCont = false;

      Object.keys(prog).forEach(nome => {
        const item = prog[nome];
        if (!item.concluido && item.tempo > 5 && catalogo[nome]) {
          temCont = true;
          const anime = catalogo[nome];
          const ep = anime.episodios[item.idx] || anime.episodios[0];
          const pct = Math.min(100, Math.round((item.tempo / item.duracao) * 100));
          const card = document.createElement("div");
          card.className = "continue-card";
          card.onclick = () => abrirPlayer(nome, item.idx);
          card.innerHTML = `
            <img src="${anime.capa || '/icon.svg'}" onerror="this.src='/icon.svg'">
            <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:${pct}%"></div></div>
            <div class="continue-info">
              <h4>${nome}</h4>
              <p>${ep ? ep.titulo : 'Ep'} • ${formatarTempo(item.tempo)}</p>
            </div>
          `;
          rowCont.appendChild(card);
        }
      });
      document.getElementById("sec-continuar").style.display = (temCont && !filtro) ? "block" : "none";

      Object.keys(catalogo).sort().forEach(nome => {
        if (filtro && !nome.toLowerCase().includes(filtro.toLowerCase())) return;
        const anime = catalogo[nome];
        const qtd = (anime.episodios || []).length;
        const card = document.createElement("div");
        card.className = "poster-card";
        card.onclick = () => abrirDetalhes(nome);
        card.innerHTML = `
          <div class="poster-wrap">
            <img src="${anime.capa || '/icon.svg'}" onerror="this.src='/icon.svg'">
          </div>
          <div class="poster-title">${nome}</div>
          <div class="poster-sub">${qtd} ${qtd === 1 ? 'Episódio' : 'Episódios'}</div>
        `;
        grade.appendChild(card);
      });
    }

    function filtrarAnimes() {
      renderizarCatalogo(document.getElementById("busca").value);
    }

    function abrirDetalhes(nome) {
      animeAtual = nome;
      const anime = catalogo[nome];
      const eps = anime.episodios || [];
      const prog = getProgresso()[nome];

      document.getElementById("view-catalogo").style.display = "none";
      document.getElementById("topo").style.display = "none";
      document.getElementById("view-detalhes").style.display = "block";

      document.getElementById("det-banner").src = anime.capa || "/icon.svg";
      document.getElementById("det-titulo").innerText = nome;
      document.getElementById("det-qtd").innerText = `${eps.length} ${eps.length === 1 ? 'Episódio' : 'Episódios'}`;

      let idxInicial = 0;
      if (prog) {
        idxInicial = prog.concluido ? Math.min(prog.idx + 1, eps.length - 1) : prog.idx;
      }
      const btnHero = document.getElementById("det-btn-play");
      if (eps.length > 0) {
        btnHero.style.display = "block";
        btnHero.innerText = prog ? `▶ Continuar: ${eps[idxInicial].titulo}` : `▶ Assistir: ${eps[0].titulo}`;
        btnHero.onclick = () => abrirPlayer(nome, idxInicial);
      } else {
        btnHero.style.display = "none";
      }

      const lista = document.getElementById("det-episodios");
      lista.innerHTML = "";
      eps.forEach((ep, i) => {
        const div = document.createElement("div");
        div.className = "ep-item";
        div.onclick = () => abrirPlayer(nome, i);
        let status = "Assistir";
        if (prog && prog.idx === i) {
          status = prog.concluido ? "✔ Assistido" : `⏯ ${formatarTempo(prog.tempo)}`;
        }
        div.innerHTML = `<span class="ep-item-title">${ep.titulo}</span><span class="ep-item-status">${status}</span>`;
        lista.appendChild(div);
      });
      window.scrollTo(0, 0);
    }

    function voltarCatalogo() {
      document.getElementById("view-detalhes").style.display = "none";
      document.getElementById("topo").style.display = "flex";
      document.getElementById("view-catalogo").style.display = "block";
      renderizarCatalogo();
    }

    function abrirPlayer(nome, idx) {
      animeAtual = nome;
      epIndexAtual = idx;
      const anime = catalogo[nome];
      const ep = anime.episodios[idx];
      if (!ep) return;

      viewPlayer.style.display = "flex";
      document.getElementById("player-titulo").innerText = `${nome} • ${ep.titulo}`;
      document.getElementById("btn-proximo").style.display = (idx + 1 < anime.episodios.length) ? "block" : "none";
      seekBar.value = 0;
      document.getElementById("txt-atual").innerText = "00:00";
      document.getElementById("txt-total").innerText = "00:00";

      videoEl.src = ep.url;
      const prog = getProgresso()[nome];
      videoEl.onloadedmetadata = () => {
        document.getElementById("txt-total").innerText = formatarTempo(videoEl.duration);
        if (prog && prog.idx === idx && !prog.concluido && prog.tempo > 5) {
          videoEl.currentTime = prog.tempo;
        }
        videoEl.play().then(() => {
          btnPlayPause.innerText = "⏸";
          mostrarControlesTemporariamente();
        }).catch(() => {
          btnPlayPause.innerText = "▶";
          overlay.classList.remove("oculto");
        });
      };
    }

    videoEl.ontimeupdate = () => {
      if (!arrastandoSeek && videoEl.duration) {
        seekBar.value = Math.floor((videoEl.currentTime / videoEl.duration) * 1000);
        document.getElementById("txt-atual").innerText = formatarTempo(videoEl.currentTime);
      }
      salvarProgresso(animeAtual, epIndexAtual, videoEl.currentTime, videoEl.duration);
    };

    videoEl.onended = () => {
      const anime = catalogo[animeAtual];
      if (anime && epIndexAtual + 1 < anime.episodios.length) {
        abrirPlayer(animeAtual, epIndexAtual + 1);
      } else {
        btnPlayPause.innerText = "▶";
        overlay.classList.remove("oculto");
      }
    };

    function tocarProximo() {
      const anime = catalogo[animeAtual];
      if (anime && epIndexAtual + 1 < anime.episodios.length) {
        abrirPlayer(animeAtual, epIndexAtual + 1);
      }
    }

    function fecharPlayer() {
      clearTimeout(timerOcultar);
      if (document.fullscreenElement && document.exitFullscreen) {
        document.exitFullscreen();
      }
      videoEl.pause();
      videoEl.src = "";
      viewPlayer.style.display = "none";
      if (document.getElementById("view-detalhes").style.display === "block") {
        abrirDetalhes(animeAtual);
      } else {
        renderizarCatalogo();
      }
    }

    iniciar();
  </script>
</body>
</html>"""

@app.route("/app")
def app_mobile():
    return render_template_string(HTML_APP_MOBILE)

# ================= PAINEL ADMIN (/) =================

HTML_ADMIN = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>nekoplay • Painel Admin</title>
  <style>
    * { box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }
    body { background: #0d0914; color: #fff; margin: 0; padding: 20px; }
    .box { max-width: 750px; margin: 0 auto; background: #141519; padding: 25px; border-radius: 10px; border: 1px solid #23252b; }
    h1 { color: #9d4edd; margin-top: 0; }
    label { display: block; margin: 12px 0 5px; font-weight: 600; color: #ccc; }
    input, textarea { width: 100%; padding: 10px; background: #23252b; border: 1px solid #333; color: #fff; border-radius: 6px; }
    button { background: #9d4edd; color: #fff; border: none; padding: 12px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 15px; }
    button:hover { background: #b16cea; }
    .btn-del { background: #e5383b; padding: 6px 12px; font-size: 12px; margin: 0; }
    .anime-card { background: #1c1d22; padding: 15px; border-radius: 8px; margin-top: 15px; }
    .ep-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid #2a2b32; }
    .top-links { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
    .badge-app { background: #23252b; color: #c77dff; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-weight: bold; }
  </style>
</head>
<body>
  <div class="box">
    {% if not logado %}
      <h1>nekoplay • Login Admin</h1>
      <form method="POST" action="/login">
        <label>Senha de Administrador:</label>
        <input type="password" name="senha" required>
        <button type="submit">Entrar</button>
      </form>
    {% else %}
      <div class="top-links">
        <h1>nekoplay • Painel Admin</h1>
        <a href="/app" target="_blank" class="badge-app">📱 Abrir Versão Celular (/app)</a>
      </div>

      <form method="POST" action="/publicar">
        <label>Nome do Anime:</label>
        <input type="text" name="anime" placeholder="Ex: Assassination Classroom" required>

        <label>Link Direto da Capa (opcional se o anime já existir):</label>
        <input type="url" name="capa" placeholder="https://github.com/.../capa.jpg">

        <label>Título do Episódio (para adicionar 1 episódio):</label>
        <input type="text" name="titulo_ep" placeholder="Ex: Episódio 1">

        <label>Link Direto do Vídeo (.mp4 ou .mkv):</label>
        <input type="url" name="url_ep" placeholder="https://github.com/.../Episodio.1.mp4">

        <label>OU Importar Vários Episódios de Uma Vez (1 link por linha):</label>
        <textarea name="lote_urls" rows="4" placeholder="Cole vários links aqui (1 por linha). O sistema numera automaticamente como Episódio 1, Episódio 2..."></textarea>

        <button type="submit">Publicar no Catálogo</button>
      </form>

      <h2 style="margin-top:30px; color:#c77dff;">Animes Publicados</h2>
      {% for nome, dados in catalogo.items() %}
        <div class="anime-card">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong>{{ nome }} ({{ dados.episodios|length }} eps)</strong>
            <form method="POST" action="/remover_anime" style="margin:0;">
              <input type="hidden" name="anime" value="{{ nome }}">
              <button type="submit" class="btn-del">Excluir Anime</button>
            </form>
          </div>
          {% for ep in dados.episodios %}
            <div class="ep-row">
              <span>{{ ep.titulo }}</span>
              <form method="POST" action="/remover_ep" style="margin:0;">
                <input type="hidden" name="anime" value="{{ nome }}">
                <input type="hidden" name="index" value="{{ loop.index0 }}">
                <button type="submit" class="btn-del">X</button>
              </form>
            </div>
          {% endfor %}
        </div>
      {% endfor %}
    {% endif %}
  </div>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML_ADMIN, logado=session.get("logado", False), catalogo=carregar_catalogo())

@app.route("/login", methods=["POST"])
def login():
    if request.form.get("senha") == SENHA_ADMIN:
        session["logado"] = True
    return redirect(url_for("index"))

@app.route("/publicar", methods=["POST"])
def publicar():
    if not session.get("logado"):
        return redirect(url_for("index"))
    catalogo = carregar_catalogo()
    anime = request.form.get("anime", "").strip()
    capa = request.form.get("capa", "").strip()
    titulo_ep = request.form.get("titulo_ep", "").strip()
    url_ep = request.form.get("url_ep", "").strip()
    lote_urls = request.form.get("lote_urls", "").strip()

    if anime:
        if anime not in catalogo:
            catalogo[anime] = {"capa": capa, "episodios": []}
        elif capa:
            catalogo[anime]["capa"] = capa

        if titulo_ep and url_ep:
            catalogo[anime]["episodios"].append({"titulo": titulo_ep, "url": url_ep})

        if lote_urls:
            linhas = [l.strip() for l in lote_urls.splitlines() if l.strip()]
            inicio = len(catalogo[anime]["episodios"]) + 1
            for i, link in enumerate(linhas):
                catalogo[anime]["episodios"].append({
                    "titulo": f"Episódio {inicio + i}",
                    "url": link
                })

        salvar_catalogo(catalogo)
    return redirect(url_for("index"))

@app.route("/remover_anime", methods=["POST"])
def remover_anime():
    if session.get("logado"):
        catalogo = carregar_catalogo()
        anime = request.form.get("anime")
        if anime in catalogo:
            del catalogo[anime]
            salvar_catalogo(catalogo)
    return redirect(url_for("index"))

@app.route("/remover_ep", methods=["POST"])
def remover_ep():
    if session.get("logado"):
        catalogo = carregar_catalogo()
        anime = request.form.get("anime")
        idx = int(request.form.get("index", -1))
        if anime in catalogo and 0 <= idx < len(catalogo[anime]["episodios"]):
            catalogo[anime]["episodios"].pop(idx)
            salvar_catalogo(catalogo)
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

from flask import Flask, render_template_string, request, redirect, url_for, jsonify, send_from_directory
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- CONFIGURAÇÕES DO SERVIDOR ---
SENHA_ADMIN = "253014"  # Troque para a sua senha secreta!
PASTA_BASE = os.path.dirname(os.path.abspath(__file__))
PASTA_UPLOADS = os.path.join(PASTA_BASE, "uploads")
ARQUIVO_BANCO = os.path.join(PASTA_BASE, "catalogo.json")

os.makedirs(PASTA_UPLOADS, exist_ok=True)

def carregar_catalogo():
    if os.path.exists(ARQUIVO_BANCO):
        try:
            with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def salvar_catalogo(dados):
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- ROTA PÚBLICA PARA O APLICATIVO NEKOPLAY LER OS ANIMES ---
@app.route("/api/catalogo", methods=["GET"])
def api_catalogo():
    dados = carregar_catalogo()
    url_base = request.host_url.rstrip("/")
    
    # Converte caminhos locais em links completos para o app tocar via internet
    catalogo_completo = {}
    for anime, info in dados.items():
        capa = info.get("capa", "")
        if capa and not capa.startswith("http"):
            capa = f"{url_base}/arquivos/{capa}"
            
        eps_formatados = []
        for ep in info.get("episodios", []):
            url_video = ep["url"]
            if not url_video.startswith("http"):
                url_video = f"{url_base}/arquivos/{url_video}"
            eps_formatados.append({
                "titulo": ep["titulo"],
                "url": url_video
            })
            
        catalogo_completo[anime] = {
            "capa": capa,
            "episodios": eps_formatados
        }
    return jsonify(catalogo_completo)

# --- ROTA QUE ENTREGA OS VÍDEOS E CAPAS PARA O VLC ---
@app.route("/arquivos/<path:nome_arquivo>")
def servir_arquivo(nome_arquivo):
    return send_from_directory(PASTA_UPLOADS, nome_arquivo)

# --- PAINEL WEB ADMIN (SEU SITE PARA IMPORTAR ANIMES) ---
HTML_PAINEL = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>nekoplay • Painel Admin</title>
    <style>
        body { background: #000000; color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; }
        header { background: #23252b; padding: 18px 40px; display: flex; align-items: center; justify-content: space-between; }
        .logo { color: #9d4edd; font-size: 26px; font-weight: bold; }
        .container { max-width: 900px; margin: 35px auto; padding: 0 20px; }
        .card { background: #141519; padding: 25px; border-radius: 8px; margin-bottom: 25px; border: 1px solid #2c2f36; }
        h2 { margin-top: 0; color: #9d4edd; }
        label { display: block; margin: 12px 0 6px; color: #a0a0a0; font-size: 14px; }
        input[type="text"], input[type="password"], input[type="file"] {
            width: 100%; padding: 10px; background: #0b0c0e; border: 1px solid #2c2f36;
            color: #fff; border-radius: 5px; box-sizing: border-box;
        }
        button {
            background: #9d4edd; color: #fff; border: none; padding: 12px 24px;
            font-size: 15px; font-weight: bold; border-radius: 5px; cursor: pointer; margin-top: 18px;
        }
        button:hover { background: #b565f2; }
        .anime-item { background: #0b0c0e; padding: 15px; border-radius: 6px; margin-top: 12px; border-left: 4px solid #9d4edd; }
        .btn-del { background: #dc2626; padding: 6px 12px; font-size: 12px; margin-top: 8px; }
        .erro { background: #7f1d1d; padding: 12px; border-radius: 5px; margin-bottom: 15px; }
        .sucesso { background: #065f46; padding: 12px; border-radius: 5px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <header>
        <div class="logo">nekoplay <span style="color:#fff; font-size:14px; font-weight:normal;">• Painel de Publicação</span></div>
        <div style="color:#a0a0a0; font-size:13px;">API ativa em: <b>/api/catalogo</b></div>
    </header>
    <div class="container">
        {% if msg %}<div class="{{ tipo }}">{{ msg }}</div>{% endif %}

        <div class="card">
            <h2>1. Criar ou Atualizar Anime (Capa)</h2>
            <form method="POST" action="/admin/anime" enctype="multipart/form-data">
                <label>Senha de Administrador:</label>
                <input type="password" name="senha" required placeholder="Digite sua senha admin">
                
                <label>Nome do Anime:</label>
                <input type="text" name="nome_anime" required placeholder="Ex: Assassination Classroom">
                
                <label>Imagem de Capa (envie um arquivo ou cole um link https://):</label>
                <input type="file" name="arquivo_capa" accept="image/*">
                <input type="text" name="link_capa" placeholder="Ou cole o link direto da capa (opcional)" style="margin-top:8px;">
                
                <button type="submit">Salvar Anime</button>
            </form>
        </div>

        <div class="card">
            <h2>2. Adicionar Episódio</h2>
            <form method="POST" action="/admin/episodio" enctype="multipart/form-data">
                <label>Senha de Administrador:</label>
                <input type="password" name="senha" required placeholder="Digite sua senha admin">
                
                <label>Nome exato do Anime:</label>
                <input type="text" name="nome_anime" required placeholder="Ex: Assassination Classroom">
                
                <label>Título do Episódio:</label>
                <input type="text" name="titulo_ep" required placeholder="Ex: Episódio 1">
                
                <label>Vídeo (.mkv ou .mp4) — Envie o arquivo OU cole um link direto na nuvem:</label>
                <input type="file" name="arquivo_video" accept="video/*,.mkv">
                <input type="text" name="link_video" placeholder="Ou cole o link direto do vídeo (https://...)" style="margin-top:8px;">
                
                <button type="submit">Publicar Episódio</button>
            </form>
        </div>

        <div class="card">
            <h2>Catálogo Publicado ({{ catalogo|length }} animes)</h2>
            {% for nome, info in catalogo.items() %}
                <div class="anime-item">
                    <strong>{{ nome }}</strong> — {{ info.episodios|length }} episódio(s)
                    <ul style="color:#a0a0a0; font-size:13px;">
                        {% for ep in info.episodios %}
                            <li>{{ ep.titulo }}</li>
                        {% endfor %}
                    </ul>
                    <form method="POST" action="/admin/deletar" style="display:inline;">
                        <input type="password" name="senha" placeholder="Senha para excluir" required style="width:160px; padding:6px;">
                        <input type="hidden" name="nome_anime" value="{{ nome }}">
                        <button type="submit" class="btn-del">Excluir Anime</button>
                    </form>
                </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAINEL, catalogo=carregar_catalogo(), msg=None, tipo="")

@app.route("/admin/anime", methods=["POST"])
def salvar_anime():
    if request.form.get("senha") != SENHA_ADMIN:
        return render_template_string(HTML_PAINEL, catalogo=carregar_catalogo(), msg="Senha incorreta!", tipo="erro")

    nome = request.form.get("nome_anime").strip()
    dados = carregar_catalogo()
    if nome not in dados:
        dados[nome] = {"capa": "", "episodios": []}

    arq_capa = request.files.get("arquivo_capa")
    link_capa = request.form.get("link_capa", "").strip()

    if arq_capa and arq_capa.filename:
        nome_seguro = secure_filename(f"capa_{nome}_{arq_capa.filename}")
        arq_capa.save(os.path.join(PASTA_UPLOADS, nome_seguro))
        dados[nome]["capa"] = nome_seguro
    elif link_capa:
        dados[nome]["capa"] = link_capa

    salvar_catalogo(dados)
    return render_template_string(HTML_PAINEL, catalogo=dados, msg=f"Anime '{nome}' salvo com sucesso!", tipo="sucesso")

@app.route("/admin/episodio", methods=["POST"])
def adicionar_episodio():
    if request.form.get("senha") != SENHA_ADMIN:
        return render_template_string(HTML_PAINEL, catalogo=carregar_catalogo(), msg="Senha incorreta!", tipo="erro")

    nome = request.form.get("nome_anime").strip()
    titulo_ep = request.form.get("titulo_ep").strip()
    dados = carregar_catalogo()

    if nome not in dados:
        dados[nome] = {"capa": "", "episodios": []}

    arq_video = request.files.get("arquivo_video")
    link_video = request.form.get("link_video", "").strip()
    url_final = ""

    if arq_video and arq_video.filename:
        nome_seguro = secure_filename(f"{nome}_{arq_video.filename}")
        arq_video.save(os.path.join(PASTA_UPLOADS, nome_seguro))
        url_final = nome_seguro
    elif link_video:
        url_final = link_video

    if url_final:
        dados[nome]["episodios"].append({"titulo": titulo_ep, "url": url_final})
        salvar_catalogo(dados)
        return render_template_string(HTML_PAINEL, catalogo=dados, msg=f"'{titulo_ep}' publicado em {nome}!", tipo="sucesso")

    return render_template_string(HTML_PAINEL, catalogo=dados, msg="Envie um vídeo ou cole um link!", tipo="erro")

@app.route("/admin/deletar", methods=["POST"])
def deletar_anime():
    if request.form.get("senha") != SENHA_ADMIN:
        return render_template_string(HTML_PAINEL, catalogo=carregar_catalogo(), msg="Senha incorreta!", tipo="erro")
    nome = request.form.get("nome_anime")
    dados = carregar_catalogo()
    if nome in dados:
        del dados[nome]
        salvar_catalogo(dados)
    return render_template_string(HTML_PAINEL, catalogo=dados, msg=f"Anime '{nome}' removido.", tipo="sucesso")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

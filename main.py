import os
import webbrowser
from threading import Thread
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)
client = genai.Client(api_key="AIzaSyD7C8MQnxUiHa7ucCiRxvXXyDnpYsDH4hU")

HTML = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8" />
<title>Bugün Ne Yiyeceğiz</title>
<style>
  html, body {
    margin: 0; padding: 0;
    width: 100%; height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #000;
    font-family: Arial, sans-serif;
    flex-direction: column;
    color: #eee;
    padding: 40px;
  }

  h1 {
    margin-bottom: 40px;
    transition: font-family 1s ease;
  }

  h1 span {
    color: #eee;
    margin-left: 6px;
    font-weight: italic;
  }

  input {
    width: 300px;
    padding: 12px;
    font-size: 16px;
    border-radius: 10px;
    border: none;
    outline: none;
    margin-bottom: 25px;
    transition: none;
  }

  input.focused {
    box-shadow: none !important;
    animation: none !important;
  }

  .glow-on-hover {
    width: 220px;
    height: 50px;
    border: none;
    outline: none;
    color: #fff;
    background: #111;
    cursor: pointer;
    position: relative;
    z-index: 0;
    border-radius: 10px;
    font-size: 18px;
    font-weight: bold;
    transition: background-color 0.3s ease;
  }

  .glow-on-hover:before {
    content: '';
    background: linear-gradient(
      45deg,
      #ff0000,
      #ff7300,
      #fffb00,
      #48ff00,
      #00ffd5,
      #002bff,
      #7a00ff,
      #ff00c8,
      #ff0000
    );
    position: absolute;
    top: -2px;
    left: -2px;
    background-size: 400%;
    z-index: -1;
    filter: blur(5px);
    width: calc(100% + 4px);
    height: calc(100% + 4px);
    animation: glowing 20s linear infinite;
    opacity: 1;
    transition: opacity 0.3s ease-in-out, filter 0.3s ease-in-out;
    border-radius: 10px;
  }

  .glow-on-hover:hover:before {
    filter: blur(7px) brightness(1.3);
    opacity: 1;
  }

  .glow-on-hover:active {
    color: #000;
  }

  .glow-on-hover:active:after {
    background: transparent;
  }

  .glow-on-hover:after {
    z-index: -1;
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    background: #111;
    left: 0;
    top: 0;
    border-radius: 10px;
  }

  #sonuc {
    margin-top: 25px;
    white-space: pre-wrap;
    background: #111;
    padding: 15px;
    border-radius: 10px;
    width: 320px;
    min-height: 120px;
    color: #ff4444;
    font-size: 16px;
    box-shadow: 0 0 15px 4px #ff0000cc;
    transition: box-shadow 0.5s ease, color 0.3s ease;
  }

  #sonuc.waiting {
    box-shadow: 0 0 15px 4px #ff0000cc;
    color: #ff4444;
    animation: glowingRed 10s linear infinite;
  }

  #sonuc.success {
    box-shadow: 0 0 20px 4px #00ff00cc;
    animation: glowingGreen 15s linear infinite;
    color: #eee;
  }

  @keyframes glowing {
    0% { background-position: 0 0; }
    50% { background-position: 400% 0; }
    100% { background-position: 0 0; }
  }
  @keyframes glowingRed {
    0%, 100% { box-shadow: 0 0 12px 3px #ff0000cc; }
    50% { box-shadow: 0 0 20px 5px #ff4444cc; }
  }
  @keyframes glowingGreen {
    0%, 100% { box-shadow: 0 0 20px 4px #00ff00cc; }
    50% { box-shadow: 0 0 30px 6px #44ff44cc; }
  }
</style>
</head>
<body>
<h1 id="baslik">Bugün Ne Yiyeceğiz<span>?</span></h1>
<input
  type="text"
  id="malzemeler"
  placeholder="Malzemeleri buraya yaz, örn: patates, soğan, tavuk"
/>
<button class="glow-on-hover" id="btn">
  Tarifleri Göster
</button>

<pre id="sonuc"></pre>

<script>
  const input = document.getElementById("malzemeler");
  const sonuc = document.getElementById("sonuc");
  const btn = document.getElementById("btn");
  const baslik = document.getElementById("baslik");

  const fonts = [
    "'Arial Black', Gadget, sans-serif",
    "'Courier New', Courier, monospace",
    "'Georgia', serif",
    "'Tahoma', Geneva, sans-serif",
    "'Comic Sans MS', cursive, sans-serif",
    "'Lucida Handwriting', cursive, sans-serif"
  ];
  let fontIndex = 0;

  setInterval(() => {
    fontIndex = (fontIndex + 1) % fonts.length;
    baslik.style.fontFamily = fonts[fontIndex];
  }, 2000);

  btn.addEventListener("click", async () => {
    const malzemeler = input.value.trim();

    if (!malzemeler) {
      alert("Lütfen malzemeleri gir!");
      return;
    }

    sonuc.classList.remove("success");
    sonuc.classList.add("waiting");
    sonuc.textContent = "Tarifler hazırlanıyor...";
    btn.disabled = true;
    btn.textContent = "Bekleyin...";

    try {
      const res = await fetch("/tarifler", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ malzemeler }),
      });

      if (!res.ok) throw new Error("Sunucu hatası");

      const data = await res.json();
      sonuc.textContent = data.tarifler || "Tarif bulunamadı.";
      sonuc.classList.remove("waiting");
      sonuc.classList.add("success");
    } catch (e) {
      sonuc.textContent = "Bir hata oluştu: " + e.message;
      sonuc.classList.remove("waiting");
      sonuc.classList.remove("success");
    } finally {
      btn.disabled = false;
      btn.textContent = "Tarifleri Göster";
    }
  });
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/tarifler", methods=["POST"])
def tarifler():
    data = request.json
    malzemeler = data.get("malzemeler")
    if not malzemeler:
        return jsonify({"error": "Malzemeler boş olamaz"}), 400

    system_prompt = (
        "Sen bir yemek tarifleri uzmanısın. "
        "Kullanıcının verdiği malzemelerle evde kolayca yapabileceği 3 farklı evde kolay yapılabilecek yemek söyle. "
        "sadece yemekleri söyle ve başka bir şey yazma"
    )

    user_prompt = f"Malzemeler: {malzemeler}. Bana 3 yemek tarifi ver."
    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt
    )

    return jsonify({"tarifler": response.text})


def run_flask():
    app.run()

if __name__ == "__main__":
    # Flask’i ayrı thread’de başlat
    Thread(target=run_flask).start()

    # Tarayıcıda localhost sayfasını aç
    webbrowser.open("http://127.0.0.1:5000")
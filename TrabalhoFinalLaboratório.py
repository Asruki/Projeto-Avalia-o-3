import os
import sys
import requests
from PIL import Image, ImageFilter, ImageOps
import numpy as np
import cv2
from io import BytesIO

# -------------------- Classe Imagem --------------------


class Imagem:
    def __init__(self, caminho=None, pil_img=None):
        self.caminho = caminho
        self.imagem = pil_img
        if caminho and not pil_img:
            self.carregar()

    def carregar(self):
        try:
            self.imagem = Image.open(self.caminho).convert("RGB")
            print(f"[✔] Imagem carregada: {self.caminho}")
        except Exception as e:
            print(f"[✘] Erro ao carregar imagem: {e}")
            self.imagem = None

    def salvar(self, nome):
        try:
            self.imagem.save(nome)
            print(f"[✔] Imagem salva como: {nome}")
        except Exception as e:
            print(f"[✘] Erro ao salvar imagem: {e}")

# -------------------- Classe Download --------------------


class Download:
    @staticmethod
    def baixar_imagem(url):
        try:
            resposta = requests.get(url)
            resposta.raise_for_status()
            img = Image.open(BytesIO(resposta.content)).convert("RGB")

            nome_base = input(
                "Digite o nome para salvar a imagem baixada (sem extensão): ").strip()
            if not nome_base:
                nome_base = "imagem_baixada"

            os.makedirs("imagens/baixadas", exist_ok=True)
            nome_arquivo = os.path.join(
                "imagens", "baixadas", f"{nome_base}.jpg")
            img.save(nome_arquivo)

            print(f"[✔] Imagem baixada e salva como '{nome_arquivo}'")
            return nome_arquivo
        except Exception as e:
            print(f"[✘] Erro ao baixar imagem: {e}")
            return None

# -------------------- Filtros --------------------


class FiltroEscalaCinza:
    @staticmethod
    def aplicar(imagem: Imagem):
        return imagem.imagem.convert("L").convert("RGB")


class FiltroPretoBranco:
    @staticmethod
    def aplicar(imagem: Imagem, limiar=128):
        img_gray = imagem.imagem.convert("L")
        img_bw = img_gray.point(
            lambda x: 0 if x < limiar else 255, '1').convert("RGB")
        return img_bw


class FiltroCartoon:
    @staticmethod
    def aplicar(imagem: Imagem):
        img_cv = cv2.cvtColor(np.array(imagem.imagem), cv2.COLOR_RGB2BGR)
        img_color = cv2.bilateralFilter(img_cv, 9, 75, 75)
        img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.medianBlur(img_gray, 7)
        edges = cv2.adaptiveThreshold(img_blur, 255,
                                      cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY,
                                      9, 2)
        edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        cartoon = cv2.bitwise_and(img_color, edges_color)
        cartoon_rgb = cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB)
        return Image.fromarray(cartoon_rgb)


class FiltroNegativo:
    @staticmethod
    def aplicar(imagem: Imagem):
        return ImageOps.invert(imagem.imagem.convert("RGB"))


class FiltroContorno:
    @staticmethod
    def aplicar(imagem: Imagem):
        return imagem.imagem.convert("L").filter(ImageFilter.FIND_EDGES).convert("RGB")


class FiltroBlur:
    @staticmethod
    def aplicar(imagem: Imagem, raio=5):
        return imagem.imagem.filter(ImageFilter.GaussianBlur(raio))

# -------------------- Classe Principal --------------------


class Principal:
    def __init__(self):
        self.imagem_atual = None
        self.menu()

    def menu(self):
        while True:
            print("\n--- MENU ---")
            print("1. Informar caminho da imagem (local ou URL)")
            print("2. Escolher filtro a ser aplicado")
            print("3. Listar arquivos de imagens do diretório")
            print("4. Sair")

            opcao = input("Escolha uma opção: ")

            if opcao == '1':
                self.carregar_imagem()
            elif opcao == '2':
                self.aplicar_filtro()
            elif opcao == '3':
                self.listar_imagens()
            elif opcao == '4':
                print("Encerrando o programa.")
                break
            else:
                print("[✘] Opção inválida.")

    def carregar_imagem(self):
        caminho = input("Informe o caminho da imagem ou URL: ").strip()
        if caminho.startswith("http"):
            arquivo_baixado = Download.baixar_imagem(caminho)
            if arquivo_baixado:
                self.imagem_atual = Imagem(caminho=arquivo_baixado)
        else:
            if os.path.exists(caminho):
                self.imagem_atual = Imagem(caminho=caminho)
            else:
                print("[✘] Caminho inválido.")

    def aplicar_filtro(self):
        print("\n--- Escolha uma imagem para aplicar o filtro ---")
        pastas = ["imagens/baixadas", "imagens/filtradas"]
        imagens_disponiveis = []

        contador = 1

        for pasta in pastas:
            if os.path.exists(pasta):
                arquivos = [f for f in os.listdir(
                    pasta) if f.lower().endswith(('.png', '.jpg'))]
                if arquivos:
                    print(f"\n📁 Pasta: {pasta}")
                    for arq in arquivos:
                        caminho_completo = os.path.join(pasta, arq)
                        imagens_disponiveis.append(caminho_completo)
                        print(f"  {contador}. 🖼 {arq}")
                        contador += 1
            else:
                print(f"[!] Pasta não encontrada: {pasta}")

        if not imagens_disponiveis:
            print("[✘] Nenhuma imagem encontrada.")
            return
        try:
            escolha = int(input("Digite o número da imagem desejada: "))
            caminho_escolhido = imagens_disponiveis[escolha - 1]
            imagem_para_filtrar = Imagem(caminho=caminho_escolhido)
        except (ValueError, IndexError):
            print("[✘] Escolha inválida.")
            return

        # Escolher filtro
        print("\n--- Filtros Disponíveis ---")
        filtros = {
            '1': ('Escala de Cinza', FiltroEscalaCinza),
            '2': ('Preto e Branco', FiltroPretoBranco),
            '3': ('Cartoon', FiltroCartoon),
            '4': ('Foto Negativa', FiltroNegativo),
            '5': ('Contorno', FiltroContorno),
            '6': ('Blurred', FiltroBlur)
        }

        for k, v in filtros.items():
            print(f"{k}. {v[0]}")

        escolha_filtro = input("Escolha o filtro: ")

        if escolha_filtro not in filtros:
            print("[✘] Filtro inválido.")
            return

        nome_filtro, classe_filtro = filtros[escolha_filtro]

        if nome_filtro == "Preto e Branco":
            try:
                limiar = int(input("Digite o limiar (0-255): "))
            except:
                limiar = 128
            imagem_filtrada = classe_filtro.aplicar(
                imagem_para_filtrar, limiar)
        elif nome_filtro == "Blurred":
            try:
                raio = int(input("Digite o raio do desfoque (1-10): "))
            except:
                raio = 5
            imagem_filtrada = classe_filtro.aplicar(imagem_para_filtrar, raio)
        else:
            imagem_filtrada = classe_filtro.aplicar(imagem_para_filtrar)

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_sugerido = f"{nome_filtro.replace(' ', '_').lower()}_{timestamp}.png"
        nome_usuario = input(
            f"Digite o nome do arquivo para salvar (ou pressione Enter para usar '{nome_sugerido}'): ").strip()

        if not nome_usuario:
            nome_usuario = nome_sugerido
        elif not nome_usuario.lower().endswith(('.png', '.jpg')):
            nome_usuario += '.png'

        os.makedirs("imagens/filtradas", exist_ok=True)
        caminho_completo = os.path.join("imagens", "filtradas", nome_usuario)

        imagem_resultado = Imagem(pil_img=imagem_filtrada)
        imagem_resultado.salvar(caminho_completo)

        self.imagem_atual = imagem_resultado

    def listar_imagens(self):
        print("\n--- Arquivos de imagem nas pastas 'imagens/filtradas' e 'imagens/baixadas' ---")

        pastas = ["imagens/filtradas", "imagens/baixadas"]
        imagens_encontradas = False

        for pasta in pastas:
            if os.path.exists(pasta):
                arquivos = [f for f in os.listdir(
                    pasta) if f.endswith(('.png', '.jpg'))]
                if arquivos:
                    print(f"\n📁 Pasta: {pasta}")
                    for arq in arquivos:
                        print(f"   🖼  {arq}")
                    imagens_encontradas = True
            else:
                print(f"[!] Pasta não encontrada: {pasta}")

        if not imagens_encontradas:
            print("[!] Nenhuma imagem encontrada.")


# -------------------- Execução do programa --------------------
if __name__ == "__main__":
    Principal()

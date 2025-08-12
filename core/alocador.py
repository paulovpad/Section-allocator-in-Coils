from models import Camada
from core.calculadora import CalculadoraHexagonal
from core.validador import ValidadorAlocacao
import math

class AlocadorBobinas:
    """
    Aloca linhas em bobinas com padrão colmeia (hexagonal):
    - Preenche cada camada da lateral (esquerda/direita) para o centro;
    - Alterna o offset entre camadas (1ª alinhada, 2ª deslocada d/2, 3ª alinhada, ...);
    - Escolhe dinamicamente o melhor lado para iniciar cada camada
      (útil quando as próximas linhas têm diâmetros diferentes).
    """

    def __init__(self):
        self.calculadora = CalculadoraHexagonal()
        self.validador = ValidadorAlocacao()

    # ---------- Helpers geométricos ----------
    def _pitch(self, d):
        """Passo vertical entre camadas em padrão hexagonal: (√3/2)·d."""
        return (math.sqrt(3.0) / 2.0) * d

    def _offset_colmeia(self, camada_index, d_ref):
        """
        Offset horizontal para padrão colmeia:
        - camadas ímpares (1,3,5...): alinhadas (offset = 0)
        - camadas pares   (2,4,6...): deslocadas (offset = d/2)
        """
        return 0.0 if (camada_index % 2 == 1) else (d_ref / 2.0)

    def _seq_horizontal(self, lado, x_ini, largura, passo):
        """
        Gera centros x caminhando na horizontal a partir da lateral escolhida.
        - lado: 'esquerda' (incrementa x) ou 'direita' (decrementa x)
        - x_ini: primeiro centro considerando offset e borda útil
        - passo: distância horizontal entre centros (já com folga)
        """
        half = largura / 2.0
        x = x_ini
        if lado == 'esquerda':
            while x + passo / 2.0 <= half + 1e-12:
                yield x
                x += passo
        else:
            while x - passo / 2.0 >= -half - 1e-12:
                yield x
                x -= passo

    # ---------- Simulação para escolher o lado ----------
    def _simular_lado(self, lado, bobina, camada_index, linhas_pendentes, k_lookahead=10):
        if not linhas_pendentes:
            return 0, bobina.largura

        d_ref = linhas_pendentes[0].diametro_efetivo / 1000.0
        pos_y = (camada_index - 1) * self._pitch(d_ref)
        offset = self._offset_colmeia(camada_index, d_ref)

        margem = d_ref * self.calculadora.MARGEM_FRAC
        passo = d_ref + 2.0 * margem

        half = bobina.largura / 2.0
        x_cursor = (-half + offset + d_ref / 2.0) if lado == 'esquerda' else (half - offset - d_ref / 2.0)

        colocadas = 0
        usados = 0
        while usados < min(k_lookahead, len(linhas_pendentes)):
            L = linhas_pendentes[usados]
            d = L.diametro_efetivo / 1000.0
            margem_local = d * self.calculadora.MARGEM_FRAC
            passo_local = d + 2.0 * margem_local

            # largura
            if not self.validador.validar_largura(x_cursor, d, bobina):
                break
            # colisão vs camadas existentes
            if self.calculadora.verificar_colisao((x_cursor, pos_y), d, bobina, camada_atual=None):
                break
            # raio mínimo
            if not self.validador.validar_raio_minimo(self.calculadora.calcular_raio_efetivo(x_cursor, pos_y), L):
                break
            # volume (global): se não cabe em volume, nem adianta seguir
            if not self.validador.validar_volume(bobina, L):
                break

            colocadas += 1
            usados += 1
            x_cursor = x_cursor + (passo_local if lado == 'esquerda' else -passo_local)

        if colocadas == 0:
            sobra = bobina.largura
        else:
            d_last = linhas_pendentes[colocadas - 1].diametro_efetivo / 1000.0
            if lado == 'esquerda':
                sobra = (half) - (x_cursor - (d_last / 2.0))
            else:
                sobra = (x_cursor + (d_last / 2.0)) - (-half)
        return colocadas, max(0.0, sobra)

    def _escolher_lado(self, bobina, camada_index, linhas_pendentes):
        c_esq, s_esq = self._simular_lado('esquerda', bobina, camada_index, linhas_pendentes)
        c_dir, s_dir = self._simular_lado('direita',  bobina, camada_index, linhas_pendentes)
        if c_esq > c_dir:
            return 'esquerda'
        if c_dir > c_esq:
            return 'direita'
        return 'esquerda' if s_esq <= s_dir else 'direita'

    # ---------- Alocação efetiva ----------
    def _tentar_adicionar_linha_na_camada(self, linha, camada, bobina):
        """Tenta adicionar uma linha na camada informada, respeitando também a capacidade de volume."""
        # guarda de volume global: se não cabe em volume, nem tenta posições
        if not self.validador.validar_volume(bobina, linha):
            return False

        d = linha.diametro_efetivo / 1000.0  # mm -> m (para geometria/colisão)
        camada_index = bobina.camadas.index(camada) + 1

        lado = self._escolher_lado(bobina, camada_index, [linha])

        pos_y = (camada_index - 1) * self._pitch(d)
        offset = self._offset_colmeia(camada_index, d)

        half = bobina.largura / 2.0
        x_ini = (-half + offset + d / 2.0) if lado == 'esquerda' else (half - offset - d / 2.0)

        margem = d * self.calculadora.MARGEM_FRAC
        passo = d + 2.0 * margem

        for pos_x in self._seq_horizontal(lado, x_ini, bobina.largura, passo):
            if not self.validador.validar_largura(pos_x, d, bobina):
                continue
            if self.calculadora.verificar_colisao((pos_x, pos_y), d, bobina, camada):
                continue
            raio_atual = self.calculadora.calcular_raio_efetivo(pos_x, pos_y)
            if not self.validador.validar_raio_minimo(raio_atual, linha):
                continue

            # passou: adiciona
            camada.adicionar_linha(linha, pos_x, pos_y)
            # atualiza peso e volume por linha adicionada em camada existente
            bobina.peso_atual_ton += linha.peso_ton
            bobina.adicionar_volume_linha(linha)
            return True

        return False

    def _tentar_criar_nova_camada(self, linha, bobina):
        """Cria nova camada e coloca a primeira linha, respeitando também a capacidade de volume."""
        # guarda de volume global
        if not self.validador.validar_volume(bobina, linha):
            return False

        d = linha.diametro_efetivo / 1000.0
        camada_index = len(bobina.camadas) + 1
        pos_y = (camada_index - 1) * self._pitch(d)

        # Verificação de limite vertical (DI/DE)
        diametro_final = bobina.diametro_interno + 2.0 * (pos_y + d / 2.0)
        if diametro_final > bobina.diametro_externo:
            return False

        lado = self._escolher_lado(bobina, camada_index, [linha])
        offset = self._offset_colmeia(camada_index, d)

        nova = Camada(
            diametro_base=bobina.diametro_interno + 2.0 * ((camada_index - 1) * self._pitch(d)),
            tipo='hexagonal'
        )

        half = bobina.largura / 2.0
        x_ini = (-half + offset + d / 2.0) if lado == 'esquerda' else (half - offset - d / 2.0)

        margem = d * self.calculadora.MARGEM_FRAC
        passo = d + 2.0 * margem

        for pos_x in self._seq_horizontal(lado, x_ini, bobina.largura, passo):
            if not self.validador.validar_largura(pos_x, d, bobina):
                continue
            if self.calculadora.verificar_colisao((pos_x, pos_y), d, bobina, nova):
                continue
            raio_atual = self.calculadora.calcular_raio_efetivo(pos_x, pos_y)
            if not self.validador.validar_raio_minimo(raio_atual, linha):
                continue

            nova.adicionar_linha(linha, pos_x, pos_y)
            # aqui NÃO somamos manualmente peso/volume; bobina.adicionar_camada cuidará disso
            bobina.adicionar_camada(nova)
            return True

        return False

# services/relatorio.py
import math

def _volume_parcial_m3(linha, comprimento_m):
    d_real_m = linha.diametro / 1000.0
    return math.pi * (d_real_m / 2.0) ** 2 * comprimento_m

class Relatorio:
    """Gera relatórios de alocação (bobinagem real)."""

    def gerar(self, resultado):
        print("\n=== RESULTADO DA ALOCAÇÃO ===")
        self._mostrar_bobinas(resultado['bobinas_utilizadas'])
        self._mostrar_linhas_nao_alocadas(resultado['linhas_nao_alocadas'])
        self._mostrar_resumo(resultado)

    def _mostrar_bobinas(self, bobinas):
        if not bobinas:
            print("\nNenhuma bobina foi utilizada.")
            return

        print("\n=== BOBINAS UTILIZADAS ===")
        for i, bobina in enumerate(bobinas, 1):
            print(f"\nBobina {i}:")
            print(f"DE={bobina.diametro_externo}m, DI={bobina.diametro_interno}m, Largura={bobina.largura}m")
            print(f"Peso máximo: {bobina.peso_maximo_ton:.2f} ton | Peso usado: {bobina.peso_atual_ton:.2f} ton")

            # Volumes globais (já acumulados na Bobina)
            v_linhas = getattr(bobina, "volume_usado_m3", 0.0)
            v_total  = getattr(bobina, "volume_total_m3", 0.0)
            v_cap    = getattr(bobina, "volume_cap_m3", 0.0)
            ocup = min(1.0, max(0.0, (v_linhas / v_cap) if v_cap > 0 else 0.0))

            print(f"Ocupação volumétrica (efetiva): {ocup*100:.1f}%")
            print(f"Volume útil: {v_total:.3f} m³ | Capacidade (× fator): {v_cap:.3f} m³ | Linhas: {v_linhas:.3f} m³")

            # Detalhe por camada: largura usada por voltas e percentuais
            for j, camada in enumerate(bobina.camadas, 1):
                linhas_cam = list(camada.linhas)
                if not linhas_cam:
                    print(f"\n  Camada {j} (vazia)")
                    continue

                Ltot = bobina.largura
                largura_usada = 0.0
                for reg in linhas_cam:
                    passo = reg.get('passo', None)
                    v_us  = reg.get('voltas_usadas', None)
                    v_cap = reg.get('voltas_capacidade', None)
                    if passo is not None and v_us is not None and v_cap is not None:
                        largura_usada += min(v_us, v_cap) * passo
                    else:
                        # fallback improvável no modo real
                        d_eff = reg['objeto'].diametro_efetivo / 1000.0
                        margem = 0.05 * d_eff
                        largura_usada += d_eff + 2.0 * margem

                pct_usada = min(100.0, (largura_usada / max(1e-12, Ltot)) * 100.0)
                pct_nao = max(0.0, 100.0 - pct_usada)

                print(f"\n  Camada {j} (Diâm. de base: {camada.diametro_base:.3f} m) — "
                      f"Largura usada: {largura_usada:.3f} m de {Ltot:.3f} m ({pct_usada:.1f}%)")

                # Ordena por ordem de alocação, se houver
                def key_ord(reg):
                    return reg.get('ordem') if reg.get('ordem') is not None else float('inf')
                linhas_ordenadas = sorted(linhas_cam, key=key_ord)

                for reg in linhas_ordenadas:
                    Lobj = reg['objeto']
                    x, y = reg['posicao']
                    ordem = reg.get('ordem')
                    comp = reg.get('comprimento_alocado', Lobj.comprimento)
                    passo = reg.get('passo', None)
                    v_us  = reg.get('voltas_usadas', None)
                    v_cap = reg.get('voltas_capacidade', None)
                    lado  = reg.get('lado', None)

                    # % da largura da camada para este reg
                    if passo is not None and v_us is not None and v_cap is not None:
                        largura_item = min(v_us, v_cap) * passo
                    else:
                        d_eff = Lobj.diametro_efetivo / 1000.0
                        margem = 0.05 * d_eff
                        largura_item = d_eff + 2.0 * margem
                    pct_item = min(100.0, (largura_item / max(1e-12, Ltot)) * 100.0)

                    print(f"    Flexível {Lobj.codigo}")
                    if ordem is not None:
                        print(f"      Ordem de alocação: {ordem}")
                    if lado:
                        print(f"      Lado de início: {lado}")
                    print(f"      Diâmetro: {Lobj.diametro:.1f}mm × {comp:.1f}m (nesta camada)")
                    print(f"      Posição (representativa): X={x:.3f}m, Y={y:.3f}m")
                    if v_us is not None and v_cap is not None:
                        print(f"      Voltas: {v_us:.3f} de {v_cap}")
                    print(f"      % da camada (largura): {pct_item:.1f}%")
                    print(f"      Peso (nesta camada): {(Lobj.peso_por_metro_kg * comp) * 0.001:.3f} ton")

                print(f"    → % não utilizada da camada (largura): {pct_nao:.1f}%")

    def _mostrar_linhas_nao_alocadas(self, linhas):
        if not linhas:
            print("\nTodos os flexíveis foram alocados com sucesso!")
            return

        print("\n=== FLEXÍVEIS NÃO ALOCADOS ===")
        print(f"Total: {len(linhas)} linha(s) não alocadas completamente")
        for i, L in enumerate(linhas[:5], 1):
            print(f"\nFlexível {L.codigo}")
            print(f"Diâmetro: {L.diametro}mm")
            print(f"Comprimento (total): {L.comprimento}m")
            print(f"Peso (total): {L.peso_ton:.3f} ton")
            print(f"Flexibilidade: {L.flexibilidade}")
            print(f"Raio mínimo: {L.raio_minimo_m}m")
        if len(linhas) > 5:
            print(f"\n... e mais {len(linhas) - 5} flexíveis não alocados")

    def _mostrar_resumo(self, resultado):
        bobinas_utilizadas = len(resultado['bobinas_utilizadas'])
        linhas_nao_alocadas = len(resultado['linhas_nao_alocadas'])
        linhas_alocadas = sum(len(camada.linhas) for bobina in resultado['bobinas_utilizadas'] for camada in bobina.camadas)
        print("\n=== RESUMO FINAL ===")
        print(f"Bobinas utilizadas: {bobinas_utilizadas}")
        print(f"Alocações (linha em camada): {linhas_alocadas}")
        print(f"Linhas sinalizadas como não alocadas (ou parciais): {linhas_nao_alocadas}")

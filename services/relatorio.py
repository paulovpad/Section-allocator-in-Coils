# services/relatorio.py
import math

class Relatorio:
    """Gera relatórios de alocação."""

    def gerar(self, resultado):
        """Gera o relatório completo."""
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
            # 2 casas para não arredondar 0.46 para 0.5
            print(f"Peso máximo: {bobina.peso_maximo_ton:.2f} ton | Peso usado: {bobina.peso_atual_ton:.2f} ton")

            # ---- Cálculo físico correto de volume ----
            v_total = (math.pi / 4.0) * (bobina.diametro_externo**2 - bobina.diametro_interno**2) * bobina.largura
            v_cap = v_total * getattr(bobina, "fator_empacotamento", 1.0)

            # Soma do volume real dos cabos (cilindros): pi*(d/2)^2 * comprimento
            v_linhas = 0.0
            vistos = set()
            for camada in bobina.camadas:
                for reg in camada.linhas:
                    L = reg['objeto']
                    key = getattr(L, "codigo", id(L))
                    if key in vistos:
                        continue
                    vistos.add(key)
                    d_real_m = L.diametro / 1000.0  # mm -> m (diâmetro físico)
                    v_linhas += math.pi * (d_real_m / 2.0) ** 2 * L.comprimento

            ocup = (v_linhas / v_cap) if v_cap > 0 else 0.0
            ocup = min(1.0, max(0.0, ocup))

            print(f"Ocupação volumétrica (efetiva): {ocup*100:.1f}%")
            print(f"Volume útil: {v_total:.3f} m³ | Capacidade (× fator): {v_cap:.3f} m³ | Linhas: {v_linhas:.3f} m³")

            # Detalhe por camada/linha
            for j, camada in enumerate(bobina.camadas, 1):
                print(f"\n  Camada {j} (Base: {camada.diametro_base:.3f}m):")
                for k, reg in enumerate(camada.linhas, 1):
                    L = reg['objeto']
                    x, y = reg['posicao']
                    print(f"    Flexível {k}: Cód. {L.codigo}")
                    print(f"      Diâmetro: {L.diametro:.1f}mm × {L.comprimento:.1f}m")
                    print(f"      Posição: X={x:.3f}m, Y={y:.3f}m")
                    print(f"      Peso: {L.peso_ton:.3f} ton | Flexibilidade: {L.flexibilidade}")

    def _mostrar_linhas_nao_alocadas(self, linhas):
        if not linhas:
            print("\nTodos os flexíveis foram alocados com sucesso!")
            return

        print("\n=== FLEXÍVEIS NÃO ALOCADOS ===")
        print(f"Total: {len(linhas)} flexíveis não puderam ser alocados")
        for i, L in enumerate(linhas[:5], 1):
            print(f"\nFlexível {i}:")
            print(f"Código: {L.codigo}")
            print(f"Diâmetro: {L.diametro}mm")
            print(f"Comprimento: {L.comprimento}m")
            print(f"Peso: {L.peso_ton:.3f} ton")
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
        print(f"Flexíveis alocados: {linhas_alocadas}")
        print(f"Flexíveis não alocados: {linhas_nao_alocadas}")

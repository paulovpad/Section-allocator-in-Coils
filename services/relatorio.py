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
            print(f"Peso máximo: {bobina.peso_maximo_ton:.1f} ton | Peso usado: {bobina.peso_atual_ton:.1f} ton")
            print(f"Ocupação volumétrica: {self._calcular_ocupacao(bobina)*100:.1f}%")
            
            for j, camada in enumerate(bobina.camadas, 1):
                print(f"\n  Camada {j} (Base: {camada.diametro_base:.3f}m):")
                for k, linha in enumerate(camada.linhas, 1):
                    print(f"    Linha {k}: {linha['objeto'].diametro}mm × {linha['objeto'].comprimento}m")
                    print(f"      Posição: X={linha['posicao'][0]:.3f}m, Y={linha['posicao'][1]:.3f}m")
                    print(f"      Peso: {linha['objeto'].peso_ton:.3f} ton | Flexibilidade: {linha['objeto'].flexibilidade}")
    
    def _calcular_ocupacao(self, bobina):
        volume_total = (math.pi/4) * (bobina.diametro_externo**2 - bobina.diametro_interno**2) * bobina.largura
        volume_ocupado = sum(
            (math.pi/4) * ((camada.diametro_base + camada.altura_camada)**2 - camada.diametro_base**2) * 
            camada.largura_ocupada * (math.sqrt(3)/2)
            for camada in bobina.camadas
        )
        return volume_ocupado / volume_total if volume_total > 0 else 0
    
    def _mostrar_linhas_nao_alocadas(self, linhas):
        if not linhas:
            print("\nTodas as linhas foram alocadas com sucesso!")
            return
            
        print("\n=== LINHAS NÃO ALOCADAS ===")
        print(f"Total: {len(linhas)} linhas não puderam ser alocadas")
        for i, linha in enumerate(linhas[:5], 1):
            print(f"\nLinha {i}:")
            print(f"Diâmetro: {linha.diametro}mm")
            print(f"Comprimento: {linha.comprimento}m")
            print(f"Peso: {linha.peso_ton:.3f} ton")
            print(f"Flexibilidade: {linha.flexibilidade}")
            print(f"Raio mínimo: {linha.raio_minimo_m}m")
        
        if len(linhas) > 5:
            print(f"\n... e mais {len(linhas) - 5} linhas não alocadas")
    
    def _mostrar_resumo(self, resultado):
        bobinas_utilizadas = len(resultado['bobinas_utilizadas'])
        linhas_nao_alocadas = len(resultado['linhas_nao_alocadas'])
        linhas_alocadas = sum(len(camada.linhas) for bobina in resultado['bobinas_utilizadas'] for camada in bobina.camadas)
        
        print("\n=== RESUMO FINAL ===")
        print(f"Bobinas utilizadas: {bobinas_utilizadas}")
        print(f"Linhas alocadas: {linhas_alocadas}")
        print(f"Linhas não alocadas: {linhas_nao_alocadas}")
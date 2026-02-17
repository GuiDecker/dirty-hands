"""
Filters - Filtros de suavização (para próximos incrementos)
"""


class ExponentialMovingAverage:
    """
    Filtro EMA para suavizar movimentos
    Será usado no próximo incremento
    """
    
    def __init__(self, alpha=0.3):
        """
        Args:
            alpha: Fator de suavização [0-1]. Menor = mais suave
        """
        self.alpha = alpha
        self.value = None
    
    def update(self, new_value):
        """Atualiza o filtro com novo valor"""
        if self.value is None:
            self.value = new_value
        else:
            self.value = (
                self.alpha * new_value[0] + (1 - self.alpha) * self.value[0],
                self.alpha * new_value[1] + (1 - self.alpha) * self.value[1]
            )
        return self.value
    
    def reset(self):
        """Reseta o filtro"""
        self.value = None


# Dirty Hands 🖐️

Controle de computador por gestos de mão - navegue e clique sem tocar no mouse. Perfeito para ler HQs ou usar o PC com as mãos ocupadas!

## 🎯 Objetivo do MVP

Criar um sistema funcional que:

- ✅ Controla cursor pela mão
- ✅ Clique por gesto (pinça)
- ✅ Swipe → próxima/anterior página
- ✅ Sistema estável (sem tremer/clicar louco)
- ✅ Base 100% reutilizável na Opção 3

## 🏗️ Estrutura do Projeto

```
dirty-hands/
├── main.py                 # Loop principal
├── vision/
│   └── hand_tracker.py    # Detecção de mãos (MediaPipe)
├── gestures/
│   └── gesture_engine.py  # Reconhecimento de gestos
├── actions/
│   └── dispatcher.py      # Dispatcher de ações
├── input/
│   └── os_controller.py   # Controle do SO (mouse/teclado)
├── utils/
│   ├── filters.py         # Filtros (para próximos incrementos)
│   └── config.py          # Configurações
├── requirements.txt        # Dependências
└── README.md              # Esta documentação
```

## 🚀 Instalação Rápida

### 1. Criar ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Executar

```bash
python main.py
```

## 🎮 Gestos Disponíveis (MVP)

| Gesto               | Como fazer                                    | Ação                                                                                                           |
| ------------------- | --------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **Movimento**       | Mova o dedo indicador                         | Move o cursor                                                                                                  |
| **Clique**          | Junte polegar + indicador (pinça)             | Clique esquerdo                                                                                                |
| **Swipe Direita**   | Movimento horizontal rápido para direita      | Próxima página (→)                                                                                             |
| **Swipe Esquerda**  | Movimento horizontal rápido para esquerda     | Página anterior (←)                                                                                            |
| **Scroll Infinito** | Estenda indicador + médio juntos (dois dedos) | Scroll contínuo na direção do movimento da mão (cima/baixo). Velocidade proporcional à velocidade do movimento |

## ⌨️ Controles

- **ESC**: Sair do programa

## 🧪 Testes Iniciais

Após executar, teste:

1. ✅ **Mexa a mão** → cursor mexe
2. ✅ **Junte polegar + indicador** → clique
3. ✅ **Faça swipe horizontal** → navega páginas
4. ✅ **Estenda indicador + médio juntos** → scroll infinito ativado (mova a mão para cima/baixo para controlar direção e velocidade)
5. ✅ **Verifique estabilidade** → não deve tremer muito

### Se tremer:

- Reduzir sensibilidade (ajustar thresholds em `gestures/gesture_engine.py`)
- Adicionar filtro EMA (próximo incremento)

## 📊 Arquitetura

```
┌─────────────────┐
│   main.py       │  ← Loop principal
└────────┬────────┘
         ↓
┌─────────────────┐
│ hand_tracker.py │  ← Detecta mão (MediaPipe)
└────────┬────────┘
         ↓
┌─────────────────┐
│ gesture_engine  │  ← Interpreta gestos (emite ações abstratas)
└────────┬────────┘
         ↓
┌─────────────────┐
│  dispatcher.py  │  ← Traduz ações em comandos
└────────┬────────┘
         ↓
┌─────────────────┐
│ os_controller   │  ← Controla mouse/teclado (PyAutoGUI)
└─────────────────┘
```

## 🔧 Configuração

Edite `utils/config.py` para ajustar:

- Thresholds de detecção
- Cooldowns
- Configurações da câmera
- Velocidade e quantidade de scroll (`SCROLL_AMOUNT`, `SCROLL_MAX_AMOUNT`, `SCROLL_INTERVAL`, `SCROLL_MIN_INTERVAL`)
- Sensibilidade de velocidade (`SCROLL_MAX_VELOCITY_THRESHOLD`)
- Configurações específicas para scroll para cima (`SCROLL_UP_*`) - otimizado para compensar limitação da câmera

## 🧠 Próximos Incrementos (ordem sugerida)

1. ✅ **Suavização de movimento** (EMA filter) - Implementado
2. ✅ **Dead zone** (ignorar pequenos movimentos) - Implementado
3. ✅ **Scroll infinito** (dois dedos) - Implementado
4. **Estados** (IDLE / ACTIVE)
5. **Drag** (manter pinça)
6. **Scroll direcional** (controlar direção do scroll)

## 📝 Código Limpo

- ✅ **Nenhuma chamada de mouse no Gesture Engine** (ações abstratas)
- ✅ **Módulos independentes** (fácil migração para Opção 3)
- ✅ **Código simples e direto** (MVP)

## ⚠️ Requisitos

- Python 3.10+
- Webcam funcional
- Windows/Linux/Mac

## 🐛 Troubleshooting

### Câmera não abre

- Verifique se não está sendo usada por outro programa
- Tente alterar `CAMERA_DEVICE_ID` em `utils/config.py`

### Gestos não funcionam

- Certifique-se de ter boa iluminação
- Mantenha a mão visível na câmera
- Ajuste thresholds em `gestures/gesture_engine.py`

### Muito instável

- Aumente `PINCH_THRESHOLD` para reduzir cliques acidentais
- Aumente `CLICK_COOLDOWN` para evitar múltiplos cliques
- Implemente filtro EMA (próximo incremento)

## 🏁 Status

✅ **MVP Completo** - Pronto para testes e próximos incrementos

---

**Próximo passo**: Escolher incremento 1 (Filtros e suavização) ou testar o MVP atual.

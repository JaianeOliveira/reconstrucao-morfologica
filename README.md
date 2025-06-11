# Reconstrução Morfológica em Níveis de Cinza

## 1. Introdução

Este trabalho explora a **reconstrução morfológica** em imagens de níveis de cinza, implementada manualmente em Python usando apenas NumPy e Pillow, sem funções prontas de OpenCV ou scikit-image. O objetivo é demonstrar:

- Conceitos teóricos de morfologia matemática em níveis de cinza.
- Operações de dilatação e erosão condicionais (geodésicas).
- Algoritmo de reconstrução por dilatação geodésica.
- Exemplos práticos de:
  1. Eliminação de pequenos objetos.
  2. Separação de objetos conectados.

## 2. Conceitos Teóricos

### 2.1 Reconstrução Morfológica

A reconstrução morfológica envolve duas imagens:

- **Marcador**: imagem inicial com sementes ou regiões de interesse.
- **Máscara**: imagem que limita a propagação do marcador.

O processo itera uma operação de **dilatação geodésica**:

```none
H_{k+1} = (H_k ⊕ B) ∩ Mask
```

até que `H_{k+1} = H_k`, onde `B` é o elemento estruturante (aqui, 3×3). O resultado preserva as formas da máscara guiadas pelas sementes do marcador.

### 2.2 Dilatação e Erosão Condicionais

- **Dilatação Condicional**: dilata o marcador e, em seguida, faz mínimo ponto a ponto com a máscara, restringindo a expansão.
- **Erosão Condicional**: erosiona o marcador e faz máximo ponto a ponto com a máscara, impedindo redução além de certos limites.

## 3. Estrutura do Código

- **main.py**: script único com:
  - Implementações manuais de `dilate()`, `erode()`, `geodesic_dilation()` e `morphological_reconstruction()`.
  - Geração de imagens sintéticas para os dois casos.
  - Rotinas de processamento e salvamento de resultados.

## 4. Exemplos Práticos

### 4.1 Eliminação de Pequenos Objetos

- Gera uma imagem com dois blocos grandes e pontos isolados (ruídos).
- Aplica **abertura por reconstrução** (erosão seguida de reconstrução).
- **Input**: `outputs/ex1_original.png`  
  ![ex1_original](outputs/ex1_original.png)
- **Output**: `outputs/ex1_result.png`  
  ![ex1_result](outputs/ex1_result.png)

### 4.2 Separação de Objetos Conectados

- Gera dois círculos sobrepostos.
- Marca manualmente um pixel em cada círculo e aplica reconstrução para separar as regiões.
- **Input**: `outputs/ex2_original.png`  
  ![ex2_original](outputs/ex2_original.png)
- **Output**: `outputs/ex2_separated.png`  
  ![ex2_separated](outputs/ex2_separated.png)

## 5. Instruções de Execução

1. **Pré-requisitos**:

   - Python 3.x
   - NumPy
   - Pillow

   ```bash
   pip install numpy pillow
   ```

2. **Executar**:

   ```bash
   python main.py
   ```

3. **Saída**:
   - `outputs/ex1_original.png`, `outputs/ex1_result.png`
   - `outputs/ex2_original.png`, `outputs/ex2_separated.png`

## 6. Vantagens e Limitações

- **Vantagens**:

  - Implementação didática, sem dependências externas de visão computacional.
  - Controle total sobre cada etapa morfológica.
  - Preservação exata de estruturas definidas pela máscara.

- **Limitações**:
  - Looping puro em Python: performance limitada para imagens maiores.
  - Marcadores manuais em separação: não há detecção automática de sementes.

## 7. Conclusão

Este trabalho demonstrou, na prática, como a reconstrução morfológica em níveis de cinza pode ser implementada “na unha”, reforçando a compreensão dos operadores condicionais e sua aplicação em casos típicos de remoção de ruído e segmentação de regiões conectadas.

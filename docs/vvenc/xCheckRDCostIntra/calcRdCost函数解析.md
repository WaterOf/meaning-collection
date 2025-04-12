# `calcRdCost` 函数解析

`calcRdCost` 是 VVENC 中计算率失真代价(RD Cost)的核心函数，用于在编码决策中平衡编码比特数和失真度。

## 函数功能

该函数实现了经典的率失真优化公式：
```
RD Cost = λ × Distortion + Bits
```
其中：
- λ (lambda) 是权衡失真和码率的拉格朗日乘子
- Distortion 表示失真度（如SSE、SAD等）
- Bits 表示编码所需的比特数

## 参数说明

| 参数 | 类型 | 描述 |
|------|------|------|
| `fracBits` | `uint64_t` | 编码所需的分数比特数 |
| `distortion` | `Distortion` | 计算得到的失真值 |
| `useUnadjustedLambda` | `bool` | 是否使用未调整的λ值（默认为true） |

## 关键实现

1. **λ值选择**：
   ```cpp
   useUnadjustedLambda ? m_DistScaleUnadjusted : m_DistScale
   ```
   - 根据`useUnadjustedLambda`标志选择使用调整前或调整后的λ值

2. **率失真计算**：
   ```cpp
   λ × distortion + bits
   ```
   - 将失真值乘以λ系数后加上实际比特数

## 技术特点

1. **双精度计算**：
   - 使用`double`类型确保计算精度
   - 避免整数运算可能导致的精度损失

2. **λ值调整**：
   - 提供调整前后的λ值选择
   - 适应不同编码场景的需求

3. **高效实现**：
   - 简单的线性公式
   - 无分支判断（除λ值选择外）

## 应用场景

该函数广泛应用于编码决策过程中，包括：
- 模式选择（帧内/帧间）
- 运动估计
- 变换量化决策
- 码率控制等

这个函数是率失真优化理论在实际编码器中的直接体现，通过量化地权衡编码效率和重建质量，指导编码器做出最优决策。
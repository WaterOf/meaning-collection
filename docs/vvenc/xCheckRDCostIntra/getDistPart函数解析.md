
`getDistPart` 是 VVENC 中计算图像块失真（Distortion）的核心函数，用于评估原始块与重建块之间的差异。

## 函数核心功能

1. **失真计算**：计算原始块与重建块之间的差异
2. **多失真度量支持**：支持多种失真计算方式（SSE、SAD等）
3. **加权处理**：对色度分量应用失真权重
4. **优化加速**：针对不同块大小使用优化的计算函数

## 函数执行流程

### 1. 初始化失真参数

```cpp
DistParam dp(org, cur, nullptr, bitDepth, 0, compId);  // 初始化失真计算参数
```

### 2. 加权SSE计算（当提供亮度参考时）

```cpp
if(orgLuma) {
    CHECKD(eDFunc != DF_SSE_WTD, "mismatch func and parameter");
    dp.orgLuma = orgLuma;
    dist = RdCost::xGetSSE_WTD(dp);  // 加权SSE计算
}
```

### 3. 常规失真计算

```cpp
else {
    if((org.width == 1)) {  // 1像素宽度的特殊处理
        dist = xGetSSE(dp);
    } else {
        const int base = (bitDepth > 10) ? 1 : 0;  // 10bit以上精度的处理
        dist = m_afpDistortFunc[base][eDFunc + Log2(org.width)](dp);  // 查表选择优化函数
    }
}
```

### 4. 色度失真加权

```cpp
if(isChroma(compId)) {  // 色度分量应用权重
    return ((Distortion)(m_distortionWeight[compId] * dist));
} else {
    return dist;  // 亮度直接返回
}
```

## 关键技术点

### 1. 失真计算方式

- **DF_SSE_WTD**：加权平方误差和（需要亮度参考）
- **常规失真函数**：通过`m_afpDistortFunc`函数指针数组调用优化实现

### 2. 性能优化

- **函数指针表**：`m_afpDistortFunc`存储不同块大小和失真度量的优化函数
- **位深优化**：10bit以上和以下使用不同函数实现
- **特殊尺寸处理**：1像素宽度使用专用函数

### 3. 色度加权

- 色度失真乘以权重系数`m_distortionWeight`
- 亮度失真不加权直接返回

### 4. 调试支持

```cpp
#if ENABLE_MEASURE_SEARCH_SPACE
g_searchSpaceAcc.addPrediction(...);  // 搜索空间统计
#endif
```

## 数据结构交互

该函数与VVENC中多个关键数据结构交互：

1. **DistParam**：失真计算参数封装
2. **CPelBuf**：像素缓冲区（原始和重建）
3. **m_afpDistortFunc**：失真计算函数指针表
4. **m_distortionWeight**：色度失真权重数组

这个函数是VVENC率失真优化的核心环节，通过高效精确的失真计算，为编码决策提供关键的质量评估指标。
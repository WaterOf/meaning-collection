
`predIntraAng` 是 VVENC 中帧内角度预测的核心函数，负责根据预测模式生成预测信号。

## 函数功能

该函数根据给定的预测模式，为当前块生成帧内预测信号，支持以下几种预测模式：
1. **Planar模式**（平面预测）
2. **DC模式**（直流预测）
3. **BDPCM模式**（块差分脉冲编码调制）
4. **角度模式**（33种方向性预测）

## 函数执行流程

### 1. 参数初始化

```cpp
const ComponentID compID = compId;  // 分量ID (Y/Cb/Cr)
const ChannelType channelType = toChannelType(compID);  // 通道类型
const uint32_t uiDirMode = cu.bdpcmM[channelType] ? BDPCM_IDX : CU::getFinalIntraMode(cu, channelType);  // 获取预测模式
```

### 2. 参考像素准备

```cpp
const int srcStride = m_refBufferStride[compID];  // 参考像素行跨度
const int srcHStride = 2;  // 水平跨度
const CPelBuf& srcBuf = CPelBuf(getPredictorPtr(compID), srcStride, srcHStride);  // 参考像素缓冲区
const ClpRng& clpRng(cu.cs->slice->clpRngs[compID]);  // 裁剪范围
```

### 3. 预测模式分发

根据预测模式调用不同的预测函数：

```cpp
switch (uiDirMode) {
    case(PLANAR_IDX): xPredIntraPlanar(piPred, srcBuf); break;  // 平面预测
    case(DC_IDX):     xPredIntraDc(piPred, srcBuf); break;     // DC预测
    case(BDPCM_IDX):  xPredIntraBDPCM(piPred, srcBuf, cu.bdpcmM[channelType], clpRng); break;  // BDPCM预测
    default:          xPredIntraAng(piPred, srcBuf, channelType, clpRng); break;  // 角度预测
}
```

### 4. 后处理 - PDPC应用

```cpp
if (m_ipaParam.applyPDPC) {  // 如果启用PDPC
    if (uiDirMode == PLANAR_IDX || uiDirMode == DC_IDX) {  // 仅对Planar和DC模式应用
        IntraPredSampleFilter(piPred, srcBuf);  // 应用PDPC滤波
    }
}
```

## 关键技术点

### 1. 预测模式支持

- **Planar模式**：通过水平和垂直方向的线性插值生成平滑预测
- **DC模式**：使用参考像素的平均值生成平坦预测
- **BDPCM模式**：特殊的预测+残差编码方式
- **角度模式**：33种方向性预测（2-34）

### 2. 参考像素处理

- 使用重构的相邻块像素作为参考
- 支持不同分量的参考像素获取
- 考虑裁剪范围(clpRng)确保像素值合法

### 3. PDPC (Position Dependent Intra Prediction Combination)

- 仅应用于Planar和DC模式
- 通过滤波改善预测质量
- 考虑像素位置调整预测值

### 4. 性能优化

- 分支预测优化：使用switch-case分发不同预测模式
- 内存访问优化：通过stride参数控制参考像素访问
- 并行化友好：各模式独立处理

## 数据结构交互

该函数与VVENC中多个关键数据结构交互：

1. **PelBuf**：预测信号存储缓冲区
2. **CodingUnit**：当前编码单元信息
3. **CPelBuf**：参考像素缓冲区
4. **ClpRng**：像素值裁剪范围控制

这个函数是VVENC帧内预测流水线的核心环节，通过高效的预测模式分发和处理，为后续的残差计算和变换量化提供高质量的预测信号。
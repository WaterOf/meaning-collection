函数声明：
```C++
void xCheckRDCostIntra( CodingStructure*& tempCS, CodingStructure*& bestCS, Partitioner& pm, const EncTestMode& encTestMode );
```

见[[DataStructure#CodingStructure]], [[DataStructure#Partitioner]], [[DataStructure#EncTestMode]]

# xCheckRDCostIntra函数解析

这个函数是VVENC编码器中处理帧内预测模式RD代价计算的核心函数，下面我将详细解释其主要流程和关键操作。

## 函数主要流程

### 1. 初始化阶段
```cpp
tempCS->initStructData(encTestMode.qp, false); // 清空临时编码结构数据
CodingUnit &cu = tempCS->addCU(...); // 添加新的CU到临时编码结构
partitioner.setCUData(cu); // 设置分区器中的CU数据
```

初始化阶段会：
- 清空临时编码结构(tempCS)的数据
- 创建新的编码单元(CU)
- 设置CU的基本属性(predMode为MODE_INTRA、qp值等)

### 2. 帧内预测参数准备
```cpp
cu.initPuData(); // 初始化预测单元数据
m_cIntraSearch.m_ispTestedModes[0].init(0, 0, 1); // 初始化ISP测试模式
```

这部分准备帧内预测所需的各种参数，包括：
- 初始化预测单元(PU)数据
- 设置ISP(Intra Sub-Partitions)测试模式
- 处理快速帧内工具相关配置

### 3. 亮度分量帧内预测
```cpp
m_cIntraSearch.estIntraPredLumaQT(cu, partitioner, bestCS->cost);
```

核心操作：
- 调用亮度分量帧内预测函数
- 计算所有可能的帧内预测模式的RD代价
- 考虑ISP(子分区)和MTS(多变换选择)等高级工具

### 4. 色度分量帧内预测
```cpp
m_cIntraSearch.estIntraPredChromaQT(cu, partitioner, maxCostAllowedForChroma);
```

核心操作：
- 调用色度分量帧内预测函数
- 计算色度分量的预测RD代价
- 处理色度QP调整等特殊逻辑

### 5. 残差编码处理
```cpp
cu.rootCbf = false;
for (uint32_t t = 0; t < getNumberValidTBlocks(*cu.cs->pcv); t++) {
    cu.rootCbf |= cu.firstTU->cbf[t] != 0; // 检查是否有非零系数
}
```

确定是否需要编码残差系数(CBF标志)

### 6. CABAC熵编码
```cpp
m_CABACEstimator->resetBits();
m_CABACEstimator->cu_skip_flag(cu); // 编码skip标志
m_CABACEstimator->pred_mode(cu); // 编码预测模式
m_CABACEstimator->cu_pred_data(cu); // 编码预测数据
m_CABACEstimator->cu_residual(cu, partitioner, cuCtx); // 编码残差
```

计算编码当前模式所需的比特数

### 7. RD代价计算与比较
```cpp
tempCS->cost = m_cRdCost.calcRdCost(tempCS->fracBits, tempCS->dist);
xCheckBestMode(tempCS, bestCS, partitioner, encTestMode, m_EDO);
```

最终步骤：
- 计算总RD代价(失真+码率)
- 与当前最优模式比较
- 更新最优编码结构(bestCS)

## 关键设计特点

1. **分层处理**：先亮度后色度的处理顺序
2. **快速算法**：通过maxCostAllowedForChroma等参数实现早期终止
3. **高级工具支持**：完整支持ISP、MTS等VVC新特性
4. **精确码率估计**：使用CABAC熵编码器进行真实码率估计
5. **统计计数**：维护各种模式选择的统计信息

## 性能优化点

1. **快速帧内决策**：通过m_pcEncCfg->m_FastIntraTools等配置启用快速算法
2. **ISP优化**：根据相邻CU信息优化ISP测试顺序
3. **色度QP调整**：考虑色度QP偏移对RD代价的影响
4. **残差编码优化**：根据CBF标志决定是否跳过残差编码

这个函数体现了VVENC在帧内编码方面的核心优化技术，通过精细的RD优化和多种快速算法，在保证编码效率的同时尽可能降低计算复杂度。
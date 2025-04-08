vvenc 是 Fraunhofer HHI 开发的高效视频编码器，基于 VVC (Versatile Video Coding) 标准。以下是 vvenc 中 CU (Coding Unit) 编码的详细流程，包括关键函数调用。

## 1. 主编码流程入口

CU 编码的入口函数是 `EncCu::compressCtu()`，位于 `source/Lib/EncoderLib/EncCu.cpp`:

```cpp
void EncCu::compressCtu( CodingStructure& cs, const UnitArea& area, const unsigned ctuRsAddr, const int prevQP[], const int currQP[] )
{
    // 1. 初始化当前CTU的编码结构
    // 2. 调用xCompressCU()进行CU划分和编码
    xCompressCU( cs, area, ctuRsAddr, prevQP, currQP );
}
```

## 2. CU 递归划分与编码

核心函数 `xCompressCU()` 实现 CU 的递归划分和编码:

```cpp
void EncCu::xCompressCU( CodingStructure* tempCS, CodingStructure* bestCS, Partitioner& partitioner )
{
    // 1. 初始化QP和分区信息
    xCheckRDCostIntra( tempCS, bestCS, partitioner ); // 检查帧内模式
    xCheckRDCostInter( tempCS, bestCS, partitioner ); // 检查帧间模式
    
    // 递归处理子CU
    if( partitioner.canSplit( CU_QUAD_SPLIT, *tempCS ) )
    {
        // 尝试QT划分
        partitioner.splitCurrArea( CU_QUAD_SPLIT, *tempCS );
        do {
            xCompressCU( tempCS, bestCS, partitioner ); // 递归处理子CU
        } while( partitioner.nextPart( *tempCS ) );
        partitioner.exitCurrSplit();
    }
    
    // 类似处理BT、TT等划分
    // ...
    
    // 最终选择最佳模式
    xCheckBestMode( tempCS, bestCS, partitioner );
}
```

## 3. 帧内预测处理

帧内预测在 `xCheckRDCostIntra()` 中实现:

```cpp
void EncCu::xCheckRDCostIntra( CodingStructure*& tempCS, CodingStructure*& bestCS, Partitioner& partitioner )
{
    // 1. 初始化帧内预测
    xRecurIntraCodingLumaQT( tempCS, bestCS, partitioner ); // 亮度分量
    
    // 2. 色度分量处理
    if( CS::isDualITree( *tempCS ) )
    {
        xRecurIntraCodingChromaQT( tempCS, bestCS, partitioner );
    }
    
    // 3. 计算RD cost
    xCheckDQP( tempCS, partitioner );
}
```

亮度分量帧内预测的核心函数:

```cpp
void EncCu::xRecurIntraCodingLumaQT( CodingStructure*& tempCS, CodingStructure*& bestCS, Partitioner& partitioner )
{
    // 1. 初始化帧内预测器
    IntraSearch::estIntraPredLumaQT( *tempCS, partitioner );
    
    // 2. 遍历所有帧内预测模式
    for( int modeIdx = 0; modeIdx < NUM_LUMA_MODE; modeIdx++ )
    {
        // 3. 应用当前预测模式
        IntraSearch::predIntraAng( *tempCS, partitioner, modeIdx );
        
        // 4. 变换量化
        TrQuant::transformNxN( *tempCS, partitioner );
        Quant::quant( *tempCS, partitioner );
        
        // 5. 反量化反变换
        Quant::dequant( *tempCS, partitioner );
        TrQuant::invTransformNxN( *tempCS, partitioner );
        
        // 6. 计算失真和比特率
        Distortion distortion = xCalcDistortion( *tempCS );
        uint64_t bits = xCalcBits( *tempCS );
        double cost = m_pcRdCost->calcRdCost( distortion, bits );
        
        // 7. 更新最佳模式
        if( cost < bestCost )
        {
            bestCost = cost;
            // 保存最佳模式信息
        }
    }
}
```

## 4. 帧间预测处理

帧间预测在 `xCheckRDCostInter()` 中实现:

```cpp
void EncCu::xCheckRDCostInter( CodingStructure*& tempCS, CodingStructure*& bestCS, Partitioner& partitioner )
{
    // 1. 运动估计
    InterSearch::searchInter( *tempCS, partitioner );
    
    // 2. 运动补偿
    InterSearch::motionCompensation( *tempCS, partitioner );
    
    // 3. 变换量化
    TrQuant::transformNxN( *tempCS, partitioner );
    Quant::quant( *tempCS, partitioner );
    
    // 4. 计算RD cost
    xCheckDQP( tempCS, partitioner );
}
```

运动估计的核心函数:

```cpp
void InterSearch::searchInter( CodingStructure& cs, Partitioner& partitioner )
{
    // 1. AMVP模式处理
    xEstimateMvPredAMVP( cs, partitioner );
    
    // 2. 整数像素运动估计
    xPatternSearch( cs, partitioner );
    
    // 3. 分数像素运动估计
    xPatternSearchFracDIF( cs, partitioner );
    
    // 4. 双向预测处理
    if( cs.slice->getSliceType() == B_SLICE )
    {
        xEstimateMvBiPred( cs, partitioner );
    }
}
```

## 5. 变换量化处理

变换量化的核心函数在 `TrQuant.cpp` 和 `Quant.cpp` 中:

```cpp
// 变换
void TrQuant::transformNxN( CodingStructure& cs, const Partitioner& partitioner )
{
    // 1. 获取残差数据
    const CPelBuf resiLuma = cs.getResiBuf( partitioner.currArea() );
    
    // 2. 应用DCT/DST变换
    if( cs.sps->getUseMTS() )
    {
        xTrMTS( resiLuma, cs, partitioner ); // 多变换选择
    }
    else
    {
        xTr( resiLuma, cs, partitioner ); // 常规变换
    }
}

// 量化
void Quant::quant( CodingStructure& cs, const Partitioner& partitioner )
{
    // 1. 获取变换系数
    const TCoeff* coeff = cs.getCoeffs( partitioner.currArea() );
    
    // 2. 应用标量量化
    xQuant( coeff, cs, partitioner );
    
    // 3. 率失真优化量化
    if( cs.pps->getUseDQP() )
    {
        xRateDistOptQuant( coeff, cs, partitioner );
    }
}
```

## 6. 模式决策与CU划分

最终模式决策在 `xCheckBestMode()` 中完成:

```cpp
void EncCu::xCheckBestMode( CodingStructure* tempCS, CodingStructure* bestCS, Partitioner& partitioner )
{
    // 1. 比较当前CU的RD cost
    if( tempCS->cost < bestCS->cost )
    {
        // 2. 更新最佳编码结构
        bestCS->copyFrom( *tempCS );
        
        // 3. 更新划分信息
        m_modeCtrl->setBestCost( bestCS->cost );
        m_modeCtrl->setBestSplit( partitioner.getSplit() );
    }
}
```

## 7. CU划分决策流程

CU划分决策主要在 `Partitioner.cpp` 中实现:

```cpp
bool Partitioner::canSplit( const SplitType splitType, const CodingStructure& cs )
{
    // 检查是否允许当前划分类型
    switch( splitType )
    {
        case CU_QUAD_SPLIT:
            return cs.sps->getQTBTEnabled() && ...;
        case CU_HORZ_SPLIT:
            return cs.sps->getBTEnabled() && ...;
        case CU_VERT_SPLIT:
            return cs.sps->getBTEnabled() && ...;
        case CU_TRIH_SPLIT:
        case CU_TRIV_SPLIT:
            return cs.sps->getTTEnabled() && ...;
        default:
            return false;
    }
}
```

## 8. 熵编码准备

在CU编码完成后，准备熵编码信息:

```cpp
void EncCu::xEncodeCU( CodingStructure* cs, Partitioner& partitioner )
{
    // 1. 编码CU头信息
    CABACWriter::coding_tree_unit( *cs, partitioner );
    
    // 2. 编码预测信息
    if( cs->getPredMode() == MODE_INTRA )
    {
        CABACWriter::intra_luma_pred_mode( *cs, partitioner );
        CABACWriter::intra_chroma_pred_mode( *cs, partitioner );
    }
    else
    {
        CABACWriter::prediction_unit( *cs, partitioner );
    }
    
    // 3. 编码残差信息
    CABACWriter::residual_coding( *cs, partitioner );
}
```

以上是 vvenc 中 CU 编码的主要流程和关键函数。实际实现中还包含许多优化细节和条件判断，但核心流程遵循上述框架。
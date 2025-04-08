这些buffer函数提供了访问视频编码过程中各种中间数据的接口，下面我将按照编码流程的不同环节进行分类解释。
# 编码阶段
## 1. 原始图像相关Buffer

### (1) 原始图像Buffer
```cpp
getOrigBuf() // 原始未处理图像
getTrueOrigBuf() // 真实原始图像（可能未经预处理）
```
- **产生环节**：编码前输入阶段
- **用途**：存储编码器输入的原始YUV数据
- **区别**：`TrueOrig`可能绕过某些预处理步骤

### (2) 滤波后原始图像Buffer
```cpp
getFilteredOrigBuf() // 滤波后的原始图像
```
- **产生环节**：预处理阶段
- **用途**：存储经过ALF(自适应环路滤波)等预处理后的图像数据

## 2. 预测相关Buffer

### (1) 常规预测Buffer
```cpp
getPredBuf() // 预测信号
```
- **产生环节**：帧内/帧间预测阶段
- **用途**：
  - 帧内预测：存储根据邻近像素生成的预测块
  - 帧间预测：存储运动补偿后的预测块

### (2) 自定义预测Buffer
```cpp
getPredBufCustom() // 自定义预测信号
```
- **产生环节**：特殊预测模式阶段
- **用途**：存储神经网络预测等非传统预测方法的结果

### (3) 预测模式Buffer
```cpp
getBlockPredModeBuf() // 块预测模式信息
```
- **产生环节**：预测决策阶段
- **用途**：记录每个块使用的预测模式(帧内/帧间/特殊模式)

## 3. 残差相关Buffer

### (1) 残差Buffer
```cpp
getResiBuf() // 残差信号
```
- **产生环节**：预测后阶段
- **用途**：存储原始块与预测块的差值
- **PLT模式处理**：对于调色板模式(PredMode == MODE_PLT)，残差会被置零

## 4. 重建图像相关Buffer

### (1) 重建图像Buffer
```cpp
getRecoBuf() // 重建图像
```
- **产生环节**：重建阶段
- **用途**：存储经过变换、量化、反量化、反变换后的重建图像
- **GDR处理**：`JVET_Z0118_GDR`标志下区分了两种重建buffer用于渐进式刷新

### (2) 去块滤波前后Buffer
```cpp
getRecBeforeDbfBuf() // 去块滤波前的重建图像
getRecAfterDbfBuf() // 去块滤波后的重建图像
```
- **产生环节**：环路滤波阶段
- **用途**：
  - `BeforeDbf`：存储去块滤波前的重建图像
  - `AfterDbf`：存储去块滤波后的重建图像

## 5. 特殊功能Buffer

### (1) CU平均Buffer
```cpp
getCuAverageBuf() // CU平均值
```
- **产生环节**：分析阶段
- **用途**：存储CU的平均值信息，可能用于快速决策

### (2) 边界强度Buffer
```cpp
getBsMapBuf() // 边界强度图
```
- **产生环节**：去块滤波准备阶段
- **用途**：记录块边界的滤波强度

### (3) QP Buffer
```cpp
getBlockQpBuf() // 块QP值
```
- **产生环节**：量化阶段
- **用途**：存储每个块的量化参数

### (4) LC-NN滤波Buffer
```cpp
getLCnnlfBuf() // LC-NN滤波结果
```
- **产生环节**：神经网络滤波阶段
- **用途**：存储基于神经网络的环路滤波结果

## 编码流程与Buffer关系图

```
原始图像
├─ 预处理 → getFilteredOrigBuf()
│
├─ 预测阶段
│   ├─ 帧内预测 → getPredBuf()
│   ├─ 帧间预测 → getPredBuf()
│   └─ 特殊预测 → getPredBufCustom()
│
├─ 残差计算 → getResiBuf()
│
├─ 变换量化 → 
│
├─ 重建阶段 → getRecoBuf()
│   ├─ 去块滤波前 → getRecBeforeDbfBuf()
│   └─ 去块滤波后 → getRecAfterDbfBuf()
│
└─ 环路滤波
    ├─ ALF → 
    └─ LC-NN → getLCnnlfBuf()
```

## 关键设计特点

1. **多版本支持**：大多数buffer都有const和非const版本，支持读写控制
2. **多粒度访问**：支持从单个分量(ComponentID)、区域(CompArea)到整个单元(UnitArea)的访问
3. **条件编译**：通过宏定义(JVET_xxx)控制不同特性的buffer可用性
4. **线程安全**：通过scheduler.getSplitPicId()支持多线程处理不同图像区域

这些buffer构成了视频编码器内部数据处理的基础设施，使得各个编码模块能够高效地访问和交换中间结果，同时保持清晰的职责分离。
# 解码阶段

在解码端，这些Buffer同样扮演着重要角色，但功能和产生环节与编码端有所差异。以下是解码端各Buffer的对应解释：

---

## 解码端Buffer功能映射

### 1. 原始图像相关Buffer（解码端通常不存在）
- 解码器不处理原始YUV输入，因此`getOrigBuf()`等通常无效或用于调试

### 2. 预测相关Buffer
```cpp
getPredBuf() // 预测信号
getPredBufCustom() // 自定义预测信号
```
- **产生环节**：帧内/帧间预测重建阶段
- **用途**：
  - 存储从码流解析出的预测模式生成的预测块
  - 帧间预测时存储运动补偿结果
  - 自定义预测可能用于屏幕内容解码等特殊模式

### 3. 残差相关Buffer
```cpp
getResiBuf() // 残差信号
```
- **产生环节**：熵解码后
- **用途**：
  - 存储从码流中解析出的变换系数经反量化、反变换后的残差
  - PLT模式时可能被置零（直接使用预测值）

### 4. 重建图像相关Buffer（核心）
```cpp
getRecoBuf() // 最终重建图像
getRecBeforeDbfBuf() // 去块滤波前图像
getRecAfterDbfBuf() // 去块滤波后图像
```
- **关键作用**：
  - `RecBeforeDbf`：存储预测+残差后的初始重建图像
  - `RecAfterDbf`：经去块滤波后的图像（可能作为后续帧的参考帧）
  - `RecoBuf`：通常指向最终输出图像（可能等同于`RecAfterDbf`或含附加滤波）

### 5. 特殊功能Buffer
```cpp
getBsMapBuf() // 边界强度（从码流解析）
getBlockQpBuf() // 块QP值（从码流解析）
getLCnnlfBuf() // NN滤波结果（若使用神经网络环路滤波）
```
- **数据来源**：
  - 全部信息从码流中解析获得（非计算生成）
  - 例如边界强度值直接来自码流中的`deblocking_filter_override`标志

---

## 解码流程与Buffer关系图

```
码流输入
├─ 熵解码 → 获取预测模式/QP/残差系数等
│
├─ 预测重建
│   ├─ 帧内预测 → getPredBuf()
│   └─ 帧间预测（运动补偿） → getPredBuf()
│
├─ 残差相加 → getResiBuf() + getPredBuf() → getRecBeforeDbfBuf()
│
├─ 去块滤波 → getRecAfterDbfBuf()
│
└─ 环路滤波
    ├─ SAO/ALF（若有）→ 
    └─ NN滤波（若有）→ getLCnnlfBuf() → 最终getRecoBuf()
```

---

## 与编码端的关键差异

1. **数据流向相反**：
   - 编码端：原始数据 → 压缩数据 + 中间结果
   - 解码端：压缩数据 → 重建数据（无原始数据参与）

2. **信息获取方式**：
   - 编码端：通过计算生成预测模式/QP等
   - 解码端：从码流直接解析这些参数

3. **Buffer用途变化**：
   | Buffer类型        | 编码端用途               | 解码端用途               |
   |------------------|--------------------------|--------------------------|
   | `PredBuf`        | 试算多种预测模式         | 执行码流指定的预测模式   |
   | `ResiBuf`        | 计算原始与预测的差值     | 存储解析出的残差数据     |
   | `RecBeforeDbf`   | 记录变换量化后的中间结果 | 存储预测+残差的初始重建  |

4. **可选功能处理**：
   - 解码器必须根据码流中的标志（如`sps_alf_enabled_flag`）决定是否启用特定Buffer

---

## 典型解码场景示例

**帧内块解码过程**：
1. 从码流解析：预测模式 + QP + 残差系数
2. 用`getPredBuf()`生成帧内预测块
3. 残差系数 → 反量化 → 反变换 → 存入`getResiBuf()`
4. `RecBeforeDbfBuf` = `PredBuf` + `ResiBuf`
5. 应用去块滤波 → `RecAfterDbfBuf`
6. 最终输出`RecoBuf`

**帧间块解码过程**：
1. 从码流解析：运动向量 + 参考帧索引 + 残差系数
2. 从DPB获取参考帧数据，运动补偿生成`getPredBuf()`
3. 后续步骤与帧内解码相同

---

## 设计特点保留

1. **多版本访问**：与编码端相同的API设计（如`const`/非`const`版本）
2. **线程安全**：通过分块处理支持波前并行解码等特性
3. **条件编译**：根据标准版本（VVC/AV1等）启用不同的Buffer功能

解码端的这些Buffer构成了从压缩码流到可视图像的关键数据通路，其高效实现直接影响解码性能和输出质量。
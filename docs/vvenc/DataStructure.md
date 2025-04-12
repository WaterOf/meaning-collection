# Partitioner
## Partitioner类在VVENC中的作用与使用场景分析

Partitioner类是VVENC视频编码器中负责管理编码单元(CU)分区过程的核心组件。下面我将详细解释它的作用和典型使用场景。

### 主要作用

1. **分区树管理**：跟踪当前处理的分区区域(currArea)以及导致该区域被处理的所有分区决策(存储在m_partStack中)

2. **分区类型支持**：通过PartSplit枚举定义了多种分区类型，包括：
   - 四叉树分割(CU_QUAD_SPLIT)
   - 二叉树水平/垂直分割(CU_HORZ_SPLIT/CU_VERT_SPLIT)
   - 三叉树水平/垂直分割(CU_TRIH_SPLIT/CU_TRIV_SPLIT)
   - 变换单元分割(TU_1D_HORZ_SPLIT等)
   - SBT(Sub-block transform)相关分割

3. **分区状态维护**：记录当前分区的深度信息(currDepth, currQtDepth等)和类型信息(treeType, modeType等)

### 关键数据结构

1. **PartLevel**：表示分区树中的一个层级，包含：
   - 当前使用的分割类型(split)
   - 分区后的子区域(parts)
   - 分区数量(numParts)
   - 当前处理的分区索引(idx)
   - 分区相关标志位(isImplicit, canQtSplit等)

2. **PartitioningStack**：使用静态向量存储分区层级栈，最大深度为2*MAX_CU_DEPTH+1

### 典型使用场景

1. **CTU初始化**：
```cpp
void initCtu(const UnitArea& ctuArea, const ChannelType _chType, const Slice& slice);
```
在编码开始时初始化CTU级别的分区器

2. **分区操作**：
```cpp
void splitCurrArea(const PartSplit split, const CodingStructure &cs);
```
将当前区域按照指定分割类型进行分区

3. **分区遍历**：
```cpp
bool nextPart(const CodingStructure &cs, bool autoPop = false);
```
移动到下一个待处理的分区

4. **分区能力查询**：
```cpp
void canSplit(const CodingStructure &cs, bool& canNo, bool& canQt, bool& canBh, bool& canBv, bool& canTh, bool& canTv);
```
检查当前区域支持哪些类型的分割

### 实际编码流程中的应用

在VVENC的编码过程中，Partitioner类通常这样使用：

1. 从CTU开始，初始化Partitioner
2. 递归地对当前CU尝试各种可能的分割方式
3. 对于每种分割方式：
   - 调用splitCurrArea进行实际分割
   - 对子分区递归处理
   - 处理完成后调用exitCurrSplit退出当前分割
4. 在RD代价计算过程中，使用Partitioner维护当前的分区状态

### 设计特点

1. **轻量级设计**：使用预分配的缓冲区(m_partBuf)来存储分区区域，避免频繁内存分配

2. **状态完整性检查**：在调试模式下(_DEBUG)会验证当前区域的一致性

3. **多类型树支持**：通过CU_MT_SPLIT等标志支持VVC中引入的多类型树分割

4. **隐式分割处理**：提供isSplitImplicit和getImplicitSplit方法处理VVC中的隐式分割情况

Partitioner类是VVENC实现高效灵活的分区决策机制的关键组件，它封装了VVC标准中复杂的分区逻辑，为上层的编码算法提供了清晰的分区管理接口。
## 分区树管理机制详解

在VVENC的编码过程中，分区树管理是理解CU级编码的核心概念。让我通过一个更直观的方式来解释这个机制。

### 分区树的基本概念

想象你在处理一张大拼图(CTU)，为了高效完成，你会：
1. 先把大拼图分成几个中等大小的块(CU)
2. 对每个中等块，再判断是否需要进一步分割成更小的块
3. 这个过程会形成一个树状结构，我们称之为"分区树"

### currArea和m_partStack的作用

#### currArea - 当前处理区域
- 相当于你当前正在拼的那一块拼图
- 随着编码过程进行，currArea会不断变化，指向当前正在处理的CU

#### m_partStack - 分区决策栈
- 这是一个堆栈结构，记录了你如何从CTU一步步分割到当前CU的所有决策
- 每个栈元素(PartLevel)保存了某一层的分区信息

### 实际工作流程示例

假设有一个64×64的CTU，编码器这样处理：

1. 初始状态：
   - currArea = 整个64×64 CTU
   - m_partStack = [空]

2. 决定进行四叉树分割：
   - 调用splitCurrArea(CU_QUAD_SPLIT)
   - m_partStack新增一个PartLevel：
     - split = CU_QUAD_SPLIT
     - parts = [四个32×32的子CU]
     - idx = 0 (开始处理第一个子CU)
   - currArea = 第一个32×32 CU

3. 对第一个32×32 CU决定不分割：
   - 处理完这个CU后，调用nextPart()
   - idx变为1，currArea = 第二个32×32 CU

4. 对第二个32×32 CU决定水平二叉树分割：
   - 调用splitCurrArea(CU_HORZ_SPLIT)
   - m_partStack新增一个PartLevel：
     - split = CU_HORZ_SPLIT
     - parts = [两个32×16的子CU]
     - idx = 0
   - currArea = 第一个32×16 CU

5. 回溯过程：
   - 当处理完一个分支的所有子CU后，调用exitCurrSplit()
   - 弹出m_partStack的顶部元素，回到上一级分区

### 为什么需要这种机制？

1. **状态跟踪**：编码器需要知道当前CU是如何从CTU分割而来的
2. **决策回溯**：在RD优化过程中，需要比较不同分割方式的代价
3. **限制检查**：确保分区符合VVC标准规范(如最大/最小CU尺寸)

### 技术实现要点

- **堆栈结构**：m_partStack使用后进先出(LIFO)的堆栈，完美匹配递归的分区过程
- **轻量级设计**：通过预分配的m_partBuf避免频繁内存分配
- **深度信息**：通过currDepth等变量记录当前分区在树中的位置

这种设计使得VVENC能够高效地探索VVC标准中复杂的分区可能性，同时保持清晰的状态管理，是编码器实现高效压缩的关键机制之一。
# CodingStructure
## CodingStructure类在VVENC中的作用解析

CodingStructure是VVENC视频编码器中管理编码信息的核心类，它负责组织和维护编码过程中所有与图像分区相关的数据。下面我将详细解释它的主要作用和功能。

### 核心作用

CodingStructure本质上是一个**编码信息容器**，它：

1. 管理编码单元(CU)和变换单元(TU)的层次结构
2. 存储编码过程中产生的各种数据（预测、残差、重建等）
3. 提供对编码单元和变换单元的高效访问接口
4. 支持多层次的编码结构（从CTU到子区域）

### 关键组成部分

#### 1. 区域管理
- `area`：当前编码结构覆盖的区域
- `_maxArea`：最大允许的区域范围
- `unitScale`：不同颜色分量的缩放信息

#### 2. 编码单元管理
- `cus`：存储所有编码单元(CU)的向量
- `m_cuPtr`：CU指针数组，用于快速访问
- `addCU()`：添加新的CU到结构中
- `getCU()`：获取特定位置的CU

#### 3. 变换单元管理
- `tus`：存储所有变换单元(TU)的向量
- `addTU()`：添加新的TU到结构中
- `getTU()`：获取特定位置的TU

#### 4. 数据缓冲区
- `m_pred`：存储预测数据
- `m_resi`：存储残差数据
- `m_reco`：存储重建数据
- `m_org`：存储原始图像数据
- `m_coeffs`：存储变换系数

### 主要功能接口

#### 1. 编码单元访问
```cpp
CodingUnit* getCU(const Position& pos, const ChannelType _chType, const TreeType _treeType);
const CodingUnit* getCURestricted(...); // 带限制条件的访问
```

#### 2. 变换单元访问
```cpp
TransformUnit* getTU(const Position& pos, const ChannelType _chType, const int subTuIdx = -1);
```

#### 3. 数据缓冲区访问
```cpp
PelBuf getPredBuf(const CompArea& blk);  // 获取预测数据
PelBuf getResiBuf(const CompArea& blk);  // 获取残差数据
PelBuf getRecoBuf(const CompArea& blk);  // 获取重建数据
```

#### 4. 结构管理
```cpp
void initStructData(...);       // 初始化结构数据
void copyStructure(...);        // 复制编码结构
void createSubStructure(...);   // 创建子结构
```

### 典型使用场景

1. **编码过程**：
   - 编码器通过CodingStructure管理当前处理区域的所有编码信息
   - 在RD优化过程中比较不同编码模式的代价

2. **预测过程**：
   - 存储和访问运动估计得到的运动矢量
   - 管理帧内预测模式信息

3. **变换量化**：
   - 存储变换系数
   - 管理量化后的残差数据

4. **环路滤波**：
   - 提供对重建图像的访问
   - 存储滤波参数

### 设计特点

1. **层次化结构**：
   - 支持从CTU到子区域的多层次编码
   - 通过parent指针维护层次关系

2. **高效访问**：
   - 提供多种get方法快速定位CU/TU
   - 使用预分配缓冲区减少内存分配开销

3. **数据隔离**：
   - 不同类型数据（预测、残差、重建等）分开存储
   - 通过严格的接口访问保证数据一致性

4. **线程安全**：
   - 使用mutex保护关键数据
   - 支持并行编码处理

CodingStructure作为VVENC编码过程中的核心数据结构，有效地组织了VVC标准中复杂的编码信息，为编码算法的高效实现提供了基础支撑。
## 不同层级CodingStructure中CU与TU存储的差异示例

为了更好地理解不同层级CodingStructure中CU和TU的存储差异，我将通过一个具体的编码实例来说明。

### 示例场景
假设我们有一个64×64的CTU，经过以下分区过程：
1. 首先进行四叉树分割，分成4个32×32的CU
2. 其中一个32×32 CU继续水平二叉树分割，分成2个32×16 CU
3. 其中一个32×16 CU进行8×8的TU分割

### 不同层级的CodingStructure分析

#### 1. 顶层CodingStructure (对应整个CTU)
```cpp
// 属性
area = 64x64 (整个CTU区域)
parent = nullptr (没有父结构)

// 存储内容
cus = [64x64的根CU] // 只包含未分割前的原始CU
tus = [] // 顶层通常不直接包含TU
```

#### 2. 第一次分割后的CodingStructure (四叉树分割)
```cpp
// 属性
area = 64x64 (仍然是整个CTU区域)
parent = 指向顶层CS

// 存储内容
cus = [4个32x32的CU] // 四叉树分割产生的子CU
tus = [] // 这个层级还没有TU分割
```

#### 3. 第二次分割后的CodingStructure (二叉树分割)
```cpp
// 属性
area = 32x32 (其中一个四叉树子区域)
parent = 指向四叉树分割的CS

// 存储内容
cus = [2个32x16的CU] // 水平二叉分割产生的子CU
tus = [] // 还未进行TU分割
```

#### 4. TU分割后的CodingStructure
```cpp
// 属性
area = 32x16 (其中一个二叉树子区域)
parent = 指向二叉树分割的CS

// 存储内容
cus = [32x16的CU] // 这个CU不再分割
tus = [8个8x8的TU] // 进行TU分割后的结果
```

### 关键差异总结

| 层级 | 区域大小 | CU存储内容 | TU存储内容 | 特点 |
|------|---------|-----------|-----------|------|
| 顶层 | 64×64 | 原始CU | 通常为空 | 管理整个CTU |
| 四叉树级 | 64×64 | 分割后的4个子CU | 通常为空 | 记录QT分割结果 |
| 二叉树级 | 32×32 | 分割后的2个子CU | 通常为空 | 记录BT/TT分割结果 |
| TU级 | 32×16 | 最终不分割的CU | 多个TU | 记录变换单元信息 |

### 实际代码中的体现

在VVENC中，这种层级关系通过以下方式实现：
```cpp
// 创建子结构的典型代码
void EncCu::xCompressCU(CodingStructure*& tempCS, CodingStructure*& bestCS)
{
    // 创建临时子结构
    tempCS = m_pcInterSearch->getTempCS(area, partitioner);
    
    // 进行分割决策
    if(决定QT分割){
        partitioner.splitCurrArea(CU_QUAD_SPLIT, *tempCS);
        // 创建新的子CodingStructure
        for(每个子分区){
            xCompressCU(tempCS, bestCS); // 递归处理
        }
    }
    
    // TU处理
    if(需要TU分割){
        tempCS->addTU(...); // 添加TU到当前CS
    }
}
```

### 为什么这样设计？

1. **内存效率**：只在实际需要时才创建子结构
2. **信息隔离**：每个分区决策有独立的上下文
3. **递归处理**：天然匹配VVC的分区树结构
4. **状态管理**：每个层级维护自己的CU/TU集合

这种层级化的CodingStructure设计使得VVENC能够高效处理VVC标准中复杂的编码单元和变换单元分区策略。
# EncTestMode

主要包括如下类型：

```C++
enum EncTestModeType
{
  ETM_MERGE_SKIP,
  ETM_INTER_ME,
  ETM_INTER_IMV,
  ETM_INTRA,
  ETM_SPLIT_QT,
  ETM_SPLIT_BT_H,
  ETM_SPLIT_BT_V,
  ETM_SPLIT_TT_H,
  ETM_SPLIT_TT_V,
  ETM_RECO_CACHED,
  ETM_IBC,
  ETM_IBC_MERGE,
  ETM_INVALID
};
```
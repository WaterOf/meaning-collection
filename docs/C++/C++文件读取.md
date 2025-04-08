`ifstream` 是 C++ 标准库中用于文件输入（读取）的类，继承自 `istream`。以下是 `ifstream` 的详细用法说明，包括 `ios::` 模式标志的完整选项：

---

### **1. 基本构造函数**
```cpp
#include <fstream>
using namespace std;

// 用法1：先构造，后打开
ifstream file1;
file1.open("filename.ext", ios::binary);

// 用法2：直接构造并打开（推荐）
ifstream file2("filename.ext", ios::in | ios::binary);
```

---

### **2. `ios::` 模式标志（打开模式）**
这些标志定义在 `std::ios` 类中，可通过按位或 `|` 组合使用：

| 标志            | 作用                                                                 |
|-----------------|----------------------------------------------------------------------|
| `ios::in`       | 以读取方式打开（`ifstream` 默认包含此标志）                           |
| `ios::out`      | 以写入方式打开（`ofstream` 默认包含此标志）                           |
| `ios::binary`   | **二进制模式**（避免文本转换，如 `\n` → `\r\n`）                     |
| `ios::ate`      | 打开后定位到文件末尾（At The End）                                   |
| `ios::app`      | 追加模式（所有写入操作在文件末尾进行）                               |
| `ios::trunc`    | 若文件存在，先清空内容（`ofstream` 默认包含此标志）                  |
| `ios::nocreate` | （已弃用）若文件不存在则打开失败                                     |
| `ios::noreplace`| （已弃用）若文件存在则打开失败                                       |

#### **常用组合示例**
```cpp
// 读取二进制文件
ifstream binFile("data.bin", ios::in | ios::binary);

// 写入并追加文本
ofstream logFile("log.txt", ios::out | ios::app);

// 读写二进制文件（不截断）
fstream ioFile("data.dat", ios::in | ios::out | ios::binary);
```

---

### **3. 成员函数**
#### **文件操作**
| 函数               | 作用                                                                 |
|--------------------|----------------------------------------------------------------------|
| `open("路径", 模式)` | 打开文件                                                             |
| `is_open()`        | 检查文件是否成功打开                                                 |
| `close()`          | 关闭文件                                                             |

#### **数据读取**
| 函数                     | 作用                                                                 |
|--------------------------|----------------------------------------------------------------------|
| `read(char* buf, size)`  | 读取二进制数据（需配合 `reinterpret_cast<char*>`）                  |
| `get()`                  | 读取单个字符                                                         |
| `getline(char* buf, len)`| 读取一行文本（可指定分隔符）                                        |
| `>>`（流操作符）         | 格式化读取（如 `file >> intVar;`）                                  |

#### **文件定位**
| 函数                     | 作用                                                                 |
|--------------------------|----------------------------------------------------------------------|
| `seekg(offset, 起始位置)`| 移动读取指针（`ios::beg`/`ios::cur`/`ios::end`）                    |
| `tellg()`                | 返回当前读取位置                                                     |

---

### **4. 完整示例**
```cpp
#include <iostream>
#include <fstream>
using namespace std;

int main() {
    // 以二进制模式打开文件
    ifstream file("data.bin", ios::in | ios::binary);
    if (!file.is_open()) {
        cerr << "Failed to open file!" << endl;
        return 1;
    }

    // 读取文件头（假设是4字节的整数，大端序）
    uint32_t header;
    file.read(reinterpret_cast<char*>(&header), sizeof(header));
    if (file.gcount() != sizeof(header)) { // 检查实际读取的字节数
        cerr << "Incomplete read!" << endl;
        return 1;
    }

    // 处理字节序（假设需要大端转小端）
    header = (header << 24) | ((header << 8) & 0xFF0000) |
             ((header >> 8) & 0xFF00) | (header >> 24);

    // 移动到文件末尾并获取大小
    file.seekg(0, ios::end);
    streampos fileSize = file.tellg();
    cout << "File size: " << fileSize << " bytes" << endl;

    file.close();
    return 0;
}
```

---

### **5. 注意事项**
1. **二进制模式的重要性**  
   - 在 Windows 上，文本模式（默认）会将 `\n` 转换为 `\r\n`，破坏二进制数据。
   - 始终对非文本文件使用 `ios::binary`。

2. **错误处理**  
   - 检查 `is_open()` 和 `read()` 的返回值。
   - 使用 `file.gcount()` 确认实际读取的字节数。

3. **资源释放**  
   - 即使未显式调用 `close()`，析构时也会自动关闭文件。但显式关闭更安全。

4. **跨平台路径**  
   - 在 Windows 上使用 `\\` 或 `/` 作为路径分隔符（如 `C:/data/file.bin`）。

---

### **6. `ios::` 标志的底层原理**
这些标志实际上是 `std::ios_base::openmode` 类型的位掩码（Bitmask），通过按位或组合。例如：
```cpp
// 底层实现（简化）
constexpr openmode in =   0x01;
constexpr openmode out =  0x02;
constexpr openmode binary = 0x04;
// ...
```

---

通过正确使用这些选项和函数，可以灵活处理各种文件操作需求。
# 大端序与小端序
### **大端序（Big-Endian） vs 小端序（Little-Endian）的区别**
大端序和小端序是计算机存储多字节数据（如 `int`, `float`, `double`）的两种不同方式，主要区别在于 **字节的排列顺序**。

---

### **1. 定义**
#### **大端序（Big-Endian）**
- **高位字节在前，低位字节在后**（符合人类阅读习惯）。
- 例如，`0x12345678` 在内存中的存储顺序是 `12 34 56 78`。

#### **小端序（Little-Endian）**
- **低位字节在前，高位字节在后**（x86/ARM 等 CPU 常用）。
- 例如，`0x12345678` 在内存中的存储顺序是 `78 56 34 12`。

---

### **2. 示例对比**
假设有一个 **32 位整数 `0x12345678`**（十进制 `305419896`），它在内存中的存储方式如下：

| 字节地址 | 大端序存储 | 小端序存储 |
|----------|------------|------------|
| 0x0000   | `0x12`     | `0x78`     |
| 0x0001   | `0x34`     | `0x56`     |
| 0x0002   | `0x56`     | `0x34`     |
| 0x0003   | `0x78`     | `0x12`     |

#### **内存布局**
```
Big-Endian:    [0x12][0x34][0x56][0x78]  （从左到右，高位→低位）
Little-Endian: [0x78][0x56][0x34][0x12]  （从左到右，低位→高位）
```

---

### **3. 实际应用中的例子**
#### **（1）网络协议（大端序）**
- **TCP/IP 协议**（如 IP 地址、端口号）使用 **大端序**（网络字节序）。
- 例如，端口号 `8080`（十六进制 `0x1F90`）在网络传输中会被存储为 `1F 90`。

#### **（2）x86/ARM CPU（小端序）**
- 大多数现代 CPU（如 Intel/AMD x86、ARM）默认使用 **小端序**。
- 如果你在 C/C++ 中直接读取 `int`，得到的是小端序数据：
  ```cpp
  int num = 0x12345678;
  char* p = (char*)&num;
  // p[0] = 0x78, p[1] = 0x56, p[2] = 0x34, p[3] = 0x12（小端序）
  ```

#### **（3）文件格式（可能混合使用）**
- **Shapefile**：文件头部分用 **大端序**，数据部分用 **小端序**。
- **BMP 图像**：文件头用 **小端序**，像素数据可能是 **大端序** 或 **小端序**。

---

### **4. 如何判断当前系统的字节序？**
```cpp
#include <iostream>
using namespace std;

int main() {
    int num = 0x12345678;
    char* p = (char*)&num;

    if (p[0] == 0x78) {
        cout << "Little-Endian" << endl;
    } else {
        cout << "Big-Endian" << endl;
    }

    return 0;
}
```
- **x86/ARM 输出**：`Little-Endian`。
- **PowerPC/SPARC 输出**：`Big-Endian`（某些旧服务器）。

---

### **5. 为什么需要关心字节序？**
- **跨平台数据交换**（如网络通信、文件解析）时，必须统一字节序。
- **Shapefile 解析**：文件头是大端序，数据是小端序，必须正确处理。
- **二进制文件读写**：如果直接读取 `int`，可能会得到错误的值。

---

### **6. 如何转换字节序？**
#### **（1）手动转换（32位整数）**
```cpp
uint32_t swapEndian(uint32_t value) {
    return ((value >> 24) & 0xFF)        // 高位→低位
         | ((value >> 8)  & 0xFF00)
         | ((value << 8)  & 0xFF0000)
         | ((value << 24) & 0xFF000000);
}
```
#### **（2）使用系统函数（Linux/Windows）**
```cpp
#include <cstdint>
#ifdef _WIN32
#include <winsock2.h>  // ntohl, htonl
#else
#include <arpa/inet.h> // ntohl, htonl
#endif

uint32_t bigToLittleEndian(uint32_t value) {
    return ntohl(value); // 网络序（大端）→主机序（可能是小端）
}
```

---

### **总结**
| 特性         | 大端序（Big-Endian） | 小端序（Little-Endian） |
|--------------|----------------------|------------------------|
| **字节顺序** | 高位→低位（`12 34 56 78`） | 低位→高位（`78 56 34 12`） |
| **常见场景** | 网络协议、Java虚拟机 | x86/ARM CPU、Windows/Linux |
| **适用场景** | 跨平台数据交换 | 本地数据处理 |

在解析 **Shapefile** 时，必须正确处理字节序，否则读取的数据会是错误的！
# 类型转换
在 C++ 中，类型转换是处理不同数据类型之间操作的关键机制。C++ 提供了四种主要的类型转换操作符：`static_cast`、`dynamic_cast`、`const_cast` 和 `reinterpret_cast`，每种都有其特定的使用场景和限制。此外，C 风格的类型转换 `(type)value` 虽然仍然可用，但在现代 C++ 中不推荐使用，因为它缺乏类型安全检查，容易导致错误。

---

### **1. `static_cast`**
#### **用途**
- **基本类型之间的转换**（如 `int` 转 `double`）。
- **类层次结构中的向上转换**（派生类指针/引用 → 基类指针/引用）。
- **显式调用构造函数或转换运算符**。
- **无继承关系的指针类型转换**（不推荐，除非明确知道安全）。

#### **示例**
```cpp
double d = 3.14;
int i = static_cast<int>(d);  // 浮点数转整数（截断）

class Base {};
class Derived : public Base {};
Derived* derived = new Derived;
Base* base = static_cast<Base*>(derived);  // 向上转换（安全）

void* p = malloc(100);
int* buf = static_cast<int*>(p);  // void* → int*（需确保内存对齐）
```

#### **特点**
- **编译时完成**，无运行时开销。
- **不检查运行时类型安全**（如向下转换可能不安全）。

---

### **2. `dynamic_cast`**
#### **用途**
- **类层次结构中的向下转换**（基类指针/引用 → 派生类指针/引用）。
- **运行时类型检查（RTTI）**，失败时返回 `nullptr`（指针）或抛出异常（引用）。

#### **示例**
```cpp
class Base { virtual void foo() {} };  // 必须有虚函数
class Derived : public Base {};

Base* base = new Derived;
Derived* derived = dynamic_cast<Derived*>(base);  // 成功

Base* base2 = new Base;
Derived* derived2 = dynamic_cast<Derived*>(base2);  // 返回 nullptr
```

#### **特点**
- **运行时检查类型安全**，性能较低（需 RTTI 支持）。
- **仅适用于多态类型**（基类必须有虚函数）。

---

### **3. `const_cast`**
#### **用途**
- **移除或添加 `const`/`volatile` 修饰符**。
- **主要用于兼容旧代码或 API 设计**（如修改第三方库的 `const` 参数）。

#### **示例**
```cpp
const int x = 10;
int* y = const_cast<int*>(&x);  // 移除 const（未定义行为如果修改 x）

void print(char* str) { cout << str; }
const char* msg = "hello";
print(const_cast<char*>(msg));  // 安全，前提是函数不修改字符串
```

#### **特点**
- **不改变底层数据的二进制表示**。
- **滥用可能导致未定义行为**（如修改真正的常量数据）。

---

### **4. `reinterpret_cast`**
#### **用途**
- **低级别的指针类型重解释**（如 `int*` → `char*`）。
- **处理二进制数据、内存操作或硬件寄存器访问**。
- **无关联类型之间的强制转换**（高风险）。

#### **示例**
```cpp
int num = 0x12345678;
char* bytes = reinterpret_cast<char*>(&num);  // 按字节访问内存

// 将函数指针转为 void*（特定场景可能需要）
void (*func)() = [] { cout << "Hi"; };
void* p = reinterpret_cast<void*>(func);
```

#### **特点**
- **不进行任何类型检查**，完全依赖程序员保证安全。
- **跨平台兼容性问题**（如字节序、对齐）。

---

### **5. C 风格转换 `(type)value`**
#### **用途**
- 兼容 C 语言的强制转换，但在 C++ 中不推荐使用。
- 行为相当于依次尝试以下转换：
  1. `const_cast`
  2. `static_cast`（含 `static_cast` + `const_cast`）
  3. `reinterpret_cast`
  4. `reinterpret_cast` + `const_cast`

#### **风险**
```cpp
const int x = 10;
int* y = (int*)&x;  // 等同于 const_cast，可能引发未定义行为

Base* base = new Base;
Derived* derived = (Derived*)base;  // 危险！无运行时检查
```

---

### **6. 使用场景对比**
| 转换方式          | 典型场景                                                                 | 安全性          |
|-------------------|--------------------------------------------------------------------------|-----------------|
| `static_cast`     | 基本类型转换、向上转换、显式调用构造函数                                 | 高（编译时检查）|
| `dynamic_cast`    | 向下转换、运行时类型识别                                                 | 高（运行时检查）|
| `const_cast`      | 移除/添加 `const` 或 `volatile`                                         | 低（需谨慎）    |
| `reinterpret_cast`| 二进制数据操作、指针类型重解释                                           | 极低（高风险）  |
| C 风格转换        | 兼容旧代码（不推荐）                                                     | 最低            |

---

### **7. 最佳实践**
1. **优先使用 `static_cast`**：在明确的类型转换场景中。
2. **多态类型转换用 `dynamic_cast`**：确保向下转换安全。
3. **避免 `const_cast` 修改常量数据**：除非绝对必要。
4. **限制 `reinterpret_cast` 的使用**：仅在底层编程（如文件 I/O、网络协议）中使用。
5. **禁用 C 风格转换**：使用 `-Wold-style-cast` 编译选项（如 GCC/Clang）。

---

### **示例：综合应用**
```cpp
#include <iostream>
#include <vector>
using namespace std;

class Animal { public: virtual ~Animal() {} };
class Dog : public Animal { public: void bark() { cout << "Woof!\n"; } };

int main() {
    // 1. static_cast: 基本类型转换
    double pi = 3.14159;
    int approxPi = static_cast<int>(pi);

    // 2. dynamic_cast: 安全向下转换
    Animal* animal = new Dog;
    if (Dog* dog = dynamic_cast<Dog*>(animal)) {
        dog->bark();  // 输出: Woof!
    }

    // 3. const_cast: 移除 const（谨慎！）
    const string msg = "hello";
    string& mutableMsg = const_cast<string&>(msg);  // 风险：实际不应修改

    // 4. reinterpret_cast: 二进制处理
    int num = 0x12345678;
    char* bytes = reinterpret_cast<char*>(&num);
    cout << hex << (int)bytes[0] << endl;  // 输出第一个字节（依赖字节序）

    delete animal;
    return 0;
}
```

---

通过合理选择类型转换方式，可以显著提高代码的安全性和可维护性。始终优先选择限制最多、最明确的转换操作符。
# 父类与子类之方法调用
在 C++ 中，当父类指针指向子类对象时，能否调用子类专有方法以及同名函数的调用规则，取决于 **父类是否有多态性（虚函数）** 和 **转换方式**。以下是详细分析：

---

### **1. 能否调用子类专有方法？**
#### **直接通过父类指针调用：❌ 不能**
```cpp
class Parent { public: void foo() {} };
class Child : public Parent { public: void bar() {} };

Parent* p = new Child;
p->bar();  // 编译错误：Parent 类没有 bar() 方法
```
- **原因**：父类指针的静态类型是 `Parent*`，编译器只能看到 `Parent` 的成员。

#### **解决方案：向下转型（需谨慎）**
```cpp
if (Child* c = dynamic_cast<Child*>(p)) {  // 运行时检查
    c->bar();  // 安全调用子类方法
} else {
    // 处理转换失败
}
```
- **要求**：
  - 父类必须有虚函数（否则 `dynamic_cast` 无法使用）。
  - 使用 `dynamic_cast` 比 `static_cast` 更安全（避免未定义行为）。

---

### **2. 同名函数的调用规则**
#### **情况 1：非虚函数（静态绑定）**
```cpp
class Parent { public: void func() { cout << "Parent\n"; } };
class Child : public Parent { public: void func() { cout << "Child\n"; } };

Parent* p = new Child;
p->func();  // 输出: Parent（调用父类版本）
```
- **规则**：根据指针的静态类型（`Parent*`）决定调用哪个函数。

#### **情况 2：虚函数（动态绑定）**
```cpp
class Parent { public: virtual void func() { cout << "Parent\n"; } };
class Child : public Parent { public: void func() override { cout << "Child\n"; } };

Parent* p = new Child;
p->func();  // 输出: Child（调用子类覆盖版本）
```
- **规则**：通过虚函数表（vtable）在运行时动态绑定到实际对象的类型。

#### **特殊情况：子类隐藏父类函数**
```cpp
class Parent { public: void func(int) { cout << "Parent\n"; } };
class Child : public Parent { public: void func() { cout << "Child\n"; } };

Child c;
c.func(1);  // 编译错误：父类的 func(int) 被隐藏
```
- **解决方法**：
  - 使用 `using Parent::func;` 在子类中引入父类重载。
  - 显式指定作用域：`c.Parent::func(1);`

---

### **3. 关键总结**
| 场景                     | 调用规则                                                                 |
|--------------------------|--------------------------------------------------------------------------|
| **父类指针调用子类专有方法** | 必须通过向下转型（如 `dynamic_cast`），且父类需有虚函数。               |
| **同名非虚函数**           | 根据指针的静态类型决定（父类指针 → 父类版本）。                         |
| **同名虚函数**             | 根据对象的实际类型决定（父类指针指向子类 → 子类覆盖版本）。             |
| **函数隐藏**               | 子类同名函数会隐藏父类所有重载版本（除非用 `using` 显式引入）。        |

---

### **4. 代码示例（综合验证）**
```cpp
#include <iostream>
using namespace std;

class Parent {
public:
    virtual ~Parent() {}  // 虚析构函数（多态基类必备）
    void nonVirtual() { cout << "Parent::nonVirtual\n"; }
    virtual void isVirtual() { cout << "Parent::isVirtual\n"; }
};

class Child : public Parent {
public:
    void childOnly() { cout << "Child::childOnly\n"; }
    void nonVirtual() { cout << "Child::nonVirtual\n"; }
    void isVirtual() override { cout << "Child::isVirtual\n"; }
};

int main() {
    Parent* p = new Child;

    // 1. 无法直接调用子类专有方法
    // p->childOnly();  // 编译错误

    // 2. 向下转型后调用
    if (Child* c = dynamic_cast<Child*>(p)) {
        c->childOnly();  // 输出: Child::childOnly
    }

    // 3. 同名函数调用
    p->nonVirtual();    // 输出: Parent::nonVirtual（非虚函数，静态绑定）
    p->isVirtual();     // 输出: Child::isVirtual（虚函数，动态绑定）

    delete p;
    return 0;
}
```

---

### **5. 设计建议**
1. **优先使用虚函数**：实现运行时多态，避免手动类型转换。
2. **慎用向下转型**：`dynamic_cast` 有性能开销，可能表明设计缺陷。
3. **避免函数隐藏**：用 `override` 和 `using` 明确意图。
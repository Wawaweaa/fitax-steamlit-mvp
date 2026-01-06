# 电商数据处理系统

## 📋 项目简介

这是一个用于处理电商平台（小红书、抖音、视频号）结算数据的自动化系统，可以将原始数据转换为标准化的结算账单Excel文件。

**当前状态：**
- ✅ 小红书：已上线，功能完整
- 🚧 抖音：开发中，接口已预留
- 🚧 视频号：开发中，接口已预留

---

## 🏗️ 系统架构

### 设计理念

系统采用**可扩展的模块化架构**，每个平台的处理逻辑独立封装，便于后续添加新平台。

### 核心模块

```
app.py
├── 配置模块 (PLATFORM_CONFIG)
│   └── 定义各平台的启用状态、图标、处理器
│
├── 认证模块 (check_password)
│   └── 简单的密码保护
│
├── 平台处理模块
│   ├── 小红书模块 (已实现)
│   │   ├── identify_xiaohongshu_files()  # 文件识别
│   │   ├── process_xiaohongshu_data()    # 数据处理
│   │   └── write_xiaohongshu_to_excel()  # Excel生成
│   │
│   ├── 抖音模块 (预留接口)
│   │   ├── identify_douyin_files()       # TODO
│   │   ├── process_douyin_data()         # TODO
│   │   └── write_douyin_to_excel()       # TODO
│   │
│   └── 视频号模块 (预留接口)
│       ├── identify_shipinhao_files()    # TODO
│       ├── process_shipinhao_data()      # TODO
│       └── write_shipinhao_to_excel()    # TODO
│
├── 统一处理接口 (process_platform_data)
│   └── 根据平台名称调用对应的处理模块
│
└── UI界面 (Streamlit)
    ├── 侧边栏：平台选择、月份选择
    ├── 主界面：文件上传、处理、结果展示
    └── 下载：生成的Excel文件
```

---

## 🚀 部署到 Streamlit Cloud

### 前提条件

1. ✅ 已注册并登录 [Streamlit Cloud](https://streamlit.io/cloud)
2. ✅ 有一个 GitHub 账号

### 部署步骤

#### 步骤1：创建 GitHub 仓库

1. 登录 GitHub，创建一个新的仓库（例如：`ecommerce-data-processor`）
2. 可以设置为私有仓库（Private），只有团队成员可见

#### 步骤2：上传代码

将以下文件上传到 GitHub 仓库：

```
your-repo/
├── app.py              # 主应用文件
├── requirements.txt    # Python依赖
└── README.md          # 项目说明（可选）
```

**方法A：通过 GitHub 网页上传**
1. 在仓库页面点击 "Add file" → "Upload files"
2. 拖拽 `app.py` 和 `requirements.txt` 到页面
3. 点击 "Commit changes"

**方法B：通过 Git 命令行**
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
# 将 app.py 和 requirements.txt 复制到这个文件夹
git add .
git commit -m "Initial commit"
git push
```

#### 步骤3：在 Streamlit Cloud 部署

1. 访问 https://streamlit.io/cloud
2. 点击 "New app"
3. 填写信息：
   - **Repository**: 选择你刚创建的 GitHub 仓库
   - **Branch**: `main` 或 `master`
   - **Main file path**: `app.py`
4. 点击 "Deploy"
5. 等待 2-3 分钟，部署完成后会自动打开应用

#### 步骤4：获取访问链接

部署成功后，你会得到一个链接，例如：
```
https://your-app-name.streamlit.app
```

将这个链接分享给内部同事即可使用。

---

## 🔐 安全设置

### 修改默认密码

在 `app.py` 的第 22 行，修改默认密码：

```python
if password == "ecommerce2025":  # 修改这里的密码
```

**建议：** 使用强密码，例如：`YourCompany@2025!`

### 使用 Streamlit Secrets（推荐）

更安全的做法是使用 Streamlit Cloud 的 Secrets 功能：

1. 在 Streamlit Cloud 的应用设置中，找到 "Secrets"
2. 添加密码配置：
   ```toml
   [passwords]
   app_password = "your_strong_password"
   ```
3. 修改 `app.py` 中的密码验证：
   ```python
   import streamlit as st
   
   # 从 secrets 读取密码
   correct_password = st.secrets["passwords"]["app_password"]
   
   if password == correct_password:
       st.session_state.authenticated = True
   ```

---

## 🔧 添加新平台的步骤

当抖音或视频号的处理逻辑验证完成后，按以下步骤添加：

### 1. 启用平台

在 `app.py` 的 `PLATFORM_CONFIG` 中修改：

```python
PLATFORM_CONFIG = {
    '抖音': {
        'enabled': True,  # 改为 True
        'icon': '🎵',
        'status': '已上线',  # 改为"已上线"
        'processor': 'process_douyin'
    }
}
```

### 2. 实现处理函数

找到对应的 TODO 部分，实现三个函数：

```python
def identify_douyin_files(uploaded_files):
    """识别抖音数据文件"""
    # 实现文件识别逻辑
    # 参考 identify_xiaohongshu_files() 的实现
    pass

def process_douyin_data(files, year, month):
    """处理抖音数据"""
    # 实现数据处理逻辑
    # 参考 process_xiaohongshu_data() 的实现
    pass

def write_douyin_to_excel(df):
    """将抖音数据写入Excel"""
    # 实现Excel生成逻辑
    # 参考 write_xiaohongshu_to_excel() 的实现
    pass
```

### 3. 更新代码到 GitHub

```bash
git add app.py
git commit -m "Add Douyin platform support"
git push
```

### 4. 自动部署

Streamlit Cloud 会自动检测到代码更新，并重新部署应用（约1-2分钟）。

---

## 📊 使用说明

### 用户操作流程

1. **访问应用**：打开 Streamlit Cloud 提供的链接
2. **登录**：输入访问密码
3. **选择平台**：在侧边栏选择要处理的平台（目前只有小红书）
4. **选择月份**：设置要处理的年份和月份
5. **上传文件**：拖拽或点击上传数据文件
   - 小红书需要2个文件：结算明细 + 订单数据
6. **开始处理**：点击"开始处理数据"按钮
7. **查看结果**：查看统计信息和数据预览
8. **下载文件**：点击"下载Excel文件"获取结果

### 小红书数据要求

**文件1：结算明细**
- 必须包含字段：结算时间、商品实付/实退、佣金总额、售后单号
- 格式：.xlsx

**文件2：订单数据**
- 必须包含字段：商家编码、商品总价(元)、SKU件数、下单时间
- 格式：.xlsx

系统会自动识别文件类型，无需按特定顺序上传。

---

## 🐛 常见问题

### Q1: 部署失败怎么办？

**A:** 检查以下几点：
1. `requirements.txt` 文件是否存在且格式正确
2. GitHub 仓库是否设置为 Public（或者 Streamlit Cloud 有权限访问 Private 仓库）
3. 查看 Streamlit Cloud 的部署日志，找到具体错误信息

### Q2: 如何更新应用？

**A:** 只需将修改后的代码推送到 GitHub，Streamlit Cloud 会自动重新部署：
```bash
git add .
git commit -m "Update app"
git push
```

### Q3: 应用可以处理多大的文件？

**A:** Streamlit Cloud 免费版的限制：
- 单个文件：最大 200MB
- 总内存：1GB
- 如果文件过大，建议升级到付费版或部署到自己的服务器

### Q4: 如何限制只有内部同事可以访问？

**A:** 有几种方式：
1. **密码保护**（当前方案）：分享链接和密码给内部同事
2. **IP白名单**：需要部署到自己的服务器
3. **OAuth认证**：集成公司的SSO系统（需要自定义开发）

### Q5: 数据安全吗？

**A:** 
- ✅ 上传的文件只在处理时临时存储在内存中，不会保存到服务器
- ✅ 处理完成后，数据会自动清除
- ✅ Streamlit Cloud 使用 HTTPS 加密传输
- ⚠️ 如果对数据安全有更高要求，建议部署到公司内部服务器

---

## 📞 技术支持

如有问题，请联系系统管理员。

---

## 📝 更新日志

### v1.0 (2025-01-06)
- ✅ 实现小红书数据处理功能
- ✅ 设计可扩展的模块化架构
- ✅ 预留抖音和视频号接口
- ✅ 添加密码保护
- ✅ 部署到 Streamlit Cloud

### 计划中
- 🚧 抖音数据处理功能
- 🚧 视频号数据处理功能
- 🚧 批量处理多个月份
- 🚧 历史记录查询
- 🚧 数据可视化报表

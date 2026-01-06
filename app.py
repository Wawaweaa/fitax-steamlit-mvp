import streamlit as st
import pandas as pd
from io import BytesIO
import openpyxl
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="电商数据处理系统",
    page_icon="📊",
    layout="wide"
)

# ==================== 配置：平台状态 ====================
PLATFORM_CONFIG = {
    '小红书': {
        'enabled': True,
        'icon': '🔴',
        'status': '已上线',
        'processor': 'process_xiaohongshu'
    },
    '抖音': {
        'enabled': False,
        'icon': '🎵',
        'status': '开发中',
        'processor': 'process_douyin'
    },
    '视频号': {
        'enabled': False,
        'icon': '📹',
        'status': '开发中',
        'processor': 'process_shipinhao'
    }
}

# ==================== 密码保护 ====================
def check_password():
    """简单的密码保护"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 电商数据处理系统")
        st.markdown("### 请登录以继续")
        
        password = st.text_input("访问密码", type="password", key="password_input")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("登录", use_container_width=True):
                if password == "ecommerce2025":  # 默认密码，可以修改
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("密码错误，请重试")
        
        st.info("💡 提示：如果忘记密码，请联系系统管理员")
        return False
    
    return True

if not check_password():
    st.stop()

# ==================== 小红书处理函数 ====================

def identify_xiaohongshu_files(uploaded_files):
    """识别小红书的主数据源和辅助数据源"""
    settlement_markers = ['结算时间', '商品实付/实退', '佣金总额', '售后单号']
    orders_markers = ['商家编码', '商品总价(元)', 'SKU件数', '下单时间']
    
    result = {}
    
    for uploaded_file in uploaded_files:
        try:
            df = pd.read_excel(uploaded_file, nrows=0)
            columns = df.columns.tolist()
            
            settlement_match = sum(1 for marker in settlement_markers if marker in columns)
            orders_match = sum(1 for marker in orders_markers if marker in columns)
            
            if settlement_match >= 3:
                result['settlement'] = uploaded_file
                result['settlement_name'] = uploaded_file.name
            elif orders_match >= 3:
                result['orders'] = uploaded_file
                result['orders_name'] = uploaded_file.name
                
        except Exception as e:
            st.warning(f"⚠️ 无法读取文件 {uploaded_file.name}: {e}")
    
    return result

def process_xiaohongshu_data(settlement_file, orders_file, year, month):
    """处理小红书数据"""
    
    # 读取数据
    df_settlement = pd.read_excel(settlement_file)
    df_orders = pd.read_excel(orders_file)
    
    # 过滤指定月份的数据
    df_settlement['结算时间'] = pd.to_datetime(df_settlement['结算时间'])
    df_settlement = df_settlement[
        (df_settlement['结算时间'].dt.year == year) & 
        (df_settlement['结算时间'].dt.month == month)
    ].copy()
    
    # 创建订单数据的查找字典
    df_orders['lookup_key'] = df_orders['订单号'].astype(str) + '_' + df_orders['规格ID'].astype(str)
    orders_dict = df_orders.set_index('lookup_key')['商家编码'].to_dict()
    
    # 创建结果DataFrame
    result = pd.DataFrame()
    
    # A列：平台SKU编码（从订单数据查找）
    df_settlement['lookup_key'] = df_settlement['订单号'].astype(str) + '_' + df_settlement['规格ID'].astype(str)
    result['平台SKU编码'] = df_settlement['lookup_key'].map(orders_dict)
    
    # B列：销售数量（复杂逻辑，计算后填入值）
    sales_qty = []
    for _, row in df_settlement.iterrows():
        sku_count = row['SKU件数']
        paid_amount = row['商品实付/实退']
        
        if paid_amount < 0:
            if abs(paid_amount) <= 0.15:
                sales_qty.append(0)
            else:
                sales_qty.append(-abs(sku_count))
        else:
            import math
            sales_qty.append(math.ceil(sku_count))
    
    result['销售数量'] = sales_qty
    
    # C列：运费（复杂逻辑，计算后填入值）
    shipping_fees = []
    grouped = df_settlement.groupby('订单号')
    
    for order_num, group in grouped:
        order_shipping = group['运费'].iloc[0]
        paid_amounts = group['商品实付/实退'].values
        
        # 判断是否全部为负数（退货订单）
        if all(amt < 0 for amt in paid_amounts):
            for _ in range(len(group)):
                shipping_fees.append(order_shipping)
        else:
            positive_items = sum(1 for amt in paid_amounts if amt > 0)
            if positive_items > 0:
                fee_per_item = order_shipping / positive_items
                for amt in paid_amounts:
                    if amt > 0:
                        shipping_fees.append(fee_per_item)
                    else:
                        shipping_fees.append(0)
            else:
                for _ in range(len(group)):
                    shipping_fees.append(0)
    
    result['运费'] = shipping_fees
    
    # D-O列：使用Excel公式
    result['订单号'] = None  # 将填入公式
    result['订单计数'] = None  # 将填入公式
    result['订单序号'] = None  # 将填入公式
    result['应收客户'] = None  # 将填入公式
    result['应到账金额'] = None  # 将填入公式
    
    # P-Z列：原始数据字段
    result['订单号_值'] = df_settlement['订单号'].values
    result['结算时间'] = df_settlement['结算时间'].values
    result['商品名称'] = df_settlement['商品名称'].values
    result['规格名称'] = df_settlement['规格名称'].values
    result['规格ID'] = df_settlement['规格ID'].values
    result['SKU件数'] = df_settlement['SKU件数'].values
    result['商品实付/实退'] = df_settlement['商品实付/实退'].values
    result['运费_原始'] = df_settlement['运费'].values
    result['佣金总额'] = df_settlement['佣金总额'].values
    result['售后单号'] = df_settlement['售后单号'].values
    
    return result

def write_xiaohongshu_to_excel(df):
    """将小红书DataFrame写入Excel，并为特定列添加公式"""
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "小红书结算明细"
    
    # 写入表头
    headers = [
        '平台SKU编码', '销售数量', '运费', '订单号', '订单计数', '订单序号',
        '应收客户', '应到账金额', '订单号_原始', '结算时间', '商品名称',
        '规格名称', '规格ID', 'SKU件数', '商品实付/实退', '运费_原始',
        '佣金总额', '售后单号'
    ]
    ws.append(headers)
    
    # 写入数据和公式
    for idx, row in df.iterrows():
        row_num = idx + 2  # Excel行号（从2开始）
        
        # A-C列：直接值
        ws.cell(row=row_num, column=1, value=row['平台SKU编码'])
        ws.cell(row=row_num, column=2, value=row['销售数量'])
        ws.cell(row=row_num, column=3, value=row['运费'])
        
        # D列：订单号（公式：=I{row_num}）
        ws.cell(row=row_num, column=4, value=f"=I{row_num}")
        
        # E列：订单计数（公式：=COUNTIF($D$2:$D${last_row},D{row_num})）
        last_row = len(df) + 1
        ws.cell(row=row_num, column=5, value=f"=COUNTIF($D$2:$D${last_row},D{row_num})")
        
        # F列：订单序号（公式：=COUNTIF($D$2:$D{row_num},D{row_num})）
        ws.cell(row=row_num, column=6, value=f"=COUNTIF($D$2:$D{row_num},D{row_num})")
        
        # G列：应收客户（公式：=O{row_num}+P{row_num}+C{row_num}）
        ws.cell(row=row_num, column=7, value=f"=O{row_num}+P{row_num}+C{row_num}")
        
        # H列：应到账金额（公式：=G{row_num}-Q{row_num}）
        ws.cell(row=row_num, column=8, value=f"=G{row_num}-Q{row_num}")
        
        # I-R列：原始数据
        ws.cell(row=row_num, column=9, value=row['订单号_值'])
        ws.cell(row=row_num, column=10, value=row['结算时间'])
        ws.cell(row=row_num, column=11, value=row['商品名称'])
        ws.cell(row=row_num, column=12, value=row['规格名称'])
        ws.cell(row=row_num, column=13, value=row['规格ID'])
        ws.cell(row=row_num, column=14, value=row['SKU件数'])
        ws.cell(row=row_num, column=15, value=row['商品实付/实退'])
        ws.cell(row=row_num, column=16, value=row['运费_原始'])
        ws.cell(row=row_num, column=17, value=row['佣金总额'])
        ws.cell(row=row_num, column=18, value=row['售后单号'])
    
    # 保存到BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output

# ==================== 抖音处理函数（预留接口）====================

def identify_douyin_files(uploaded_files):
    """识别抖音数据文件（待实现）"""
    # TODO: 实现抖音文件识别逻辑
    st.warning("⚠️ 抖音数据处理功能正在开发中...")
    return {}

def process_douyin_data(files, year, month):
    """处理抖音数据（待实现）"""
    # TODO: 实现抖音数据处理逻辑
    raise NotImplementedError("抖音数据处理功能正在开发中")

def write_douyin_to_excel(df):
    """将抖音数据写入Excel（待实现）"""
    # TODO: 实现抖音Excel生成逻辑
    raise NotImplementedError("抖音Excel生成功能正在开发中")

# ==================== 视频号处理函数（预留接口）====================

def identify_shipinhao_files(uploaded_files):
    """识别视频号数据文件（待实现）"""
    # TODO: 实现视频号文件识别逻辑
    st.warning("⚠️ 视频号数据处理功能正在开发中...")
    return {}

def process_shipinhao_data(files, year, month):
    """处理视频号数据（待实现）"""
    # TODO: 实现视频号数据处理逻辑
    raise NotImplementedError("视频号数据处理功能正在开发中")

def write_shipinhao_to_excel(df):
    """将视频号数据写入Excel（待实现）"""
    # TODO: 实现视频号Excel生成逻辑
    raise NotImplementedError("视频号Excel生成功能正在开发中")

# ==================== 统一处理接口 ====================

def process_platform_data(platform, uploaded_files, year, month):
    """
    统一的平台数据处理接口
    
    Args:
        platform: 平台名称（'小红书', '抖音', '视频号'）
        uploaded_files: 上传的文件列表
        year: 处理年份
        month: 处理月份
    
    Returns:
        BytesIO: 生成的Excel文件
    """
    
    if platform == '小红书':
        # 识别文件
        files = identify_xiaohongshu_files(uploaded_files)
        
        if 'settlement' not in files or 'orders' not in files:
            raise ValueError("文件识别失败，请确保上传了结算明细和订单数据两个文件")
        
        # 处理数据
        result_df = process_xiaohongshu_data(files['settlement'], files['orders'], year, month)
        
        # 生成Excel
        output = write_xiaohongshu_to_excel(result_df)
        
        return output, result_df, files
    
    elif platform == '抖音':
        # 识别文件
        files = identify_douyin_files(uploaded_files)
        
        # 处理数据
        result_df = process_douyin_data(files, year, month)
        
        # 生成Excel
        output = write_douyin_to_excel(result_df)
        
        return output, result_df, files
    
    elif platform == '视频号':
        # 识别文件
        files = identify_shipinhao_files(uploaded_files)
        
        # 处理数据
        result_df = process_shipinhao_data(files, year, month)
        
        # 生成Excel
        output = write_shipinhao_to_excel(result_df)
        
        return output, result_df, files
    
    else:
        raise ValueError(f"不支持的平台: {platform}")

# ==================== Streamlit界面 ====================

st.title("📊 电商数据处理系统")
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 系统设置")
    
    # 显示平台状态
    st.subheader("支持的平台")
    for platform, config in PLATFORM_CONFIG.items():
        if config['enabled']:
            st.success(f"{config['icon']} {platform} - {config['status']}")
        else:
            st.info(f"{config['icon']} {platform} - {config['status']}")
    
    st.markdown("---")
    
    # 选择平台
    st.subheader("选择平台")
    enabled_platforms = [p for p, c in PLATFORM_CONFIG.items() if c['enabled']]
    selected_platform = st.selectbox(
        "当前处理平台",
        enabled_platforms,
        help="选择要处理的电商平台"
    )
    
    # 选择处理月份
    st.subheader("处理月份")
    year = st.number_input("年份", min_value=2020, max_value=2030, value=2025)
    month = st.number_input("月份", min_value=1, max_value=12, value=12)
    
    st.markdown("---")
    
    # 退出登录
    if st.button("🚪 退出登录"):
        st.session_state.authenticated = False
        st.rerun()

# 主界面
st.header(f"📁 步骤1：上传 {PLATFORM_CONFIG[selected_platform]['icon']} {selected_platform} 数据文件")

# 根据平台显示不同的提示
if selected_platform == '小红书':
    st.markdown("请上传小红书的**结算明细**和**订单数据**两个Excel文件")
elif selected_platform == '抖音':
    st.markdown("请上传抖音的**结算账单**和**订单数据**文件")
elif selected_platform == '视频号':
    st.markdown("请上传视频号的**订单流水**、**资金流水**和**订单数据**文件")

uploaded_files = st.file_uploader(
    "支持 .xlsx 和 .csv 格式",
    accept_multiple_files=True,
    type=['xlsx', 'csv'],
    help=f"上传{selected_platform}的数据文件"
)

if uploaded_files:
    st.success(f"✅ 已上传 {len(uploaded_files)} 个文件")
    
    # 显示文件列表
    for file in uploaded_files:
        st.text(f"  📄 {file.name}")
    
    st.markdown("---")
    st.header("🚀 步骤2：开始处理")
    
    if st.button("开始处理数据", type="primary", use_container_width=True):
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 处理数据
            status_text.text("⏳ 正在识别文件类型...")
            progress_bar.progress(10)
            
            status_text.text("⏳ 正在读取数据...")
            progress_bar.progress(30)
            
            output, result_df, files = process_platform_data(
                selected_platform,
                uploaded_files,
                year,
                month
            )
            
            status_text.text("⏳ 正在计算字段...")
            progress_bar.progress(70)
            
            status_text.text("⏳ 正在生成Excel文件...")
            progress_bar.progress(90)
            
            progress_bar.progress(100)
            status_text.text("✅ 处理完成！")
            
            st.success("🎉 数据处理成功！")
            
            st.markdown("---")
            st.header("📈 步骤3：查看结果")
            
            # 显示识别的文件信息
            if selected_platform == '小红书':
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📊 结算明细：{files['settlement_name']}")
                with col2:
                    st.info(f"📦 订单数据：{files['orders_name']}")
            
            # 统计信息
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("总记录数", f"{len(result_df):,}")
            
            with col2:
                unique_orders = result_df['订单号_值'].nunique()
                st.metric("订单数", f"{unique_orders:,}")
            
            with col3:
                total_amount = result_df['商品实付/实退'].sum() + result_df['运费'].sum()
                st.metric("应收客户总额", f"¥{total_amount:,.2f}")
            
            # 数据预览
            st.subheader("📋 数据预览（前20行）")
            preview_df = result_df[['平台SKU编码', '销售数量', '运费', '订单号_值', '商品名称', '商品实付/实退']].head(20)
            st.dataframe(preview_df, use_container_width=True)
            
            st.markdown("---")
            st.header("💾 步骤4：下载结果")
            
            # 下载按钮
            st.download_button(
                label="📥 下载Excel文件",
                data=output,
                file_name=f"{selected_platform}_{year}年{month}月结算账单.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            st.info("💡 提示：下载的Excel文件中包含公式，可以直接在Excel中查看和编辑")
            
        except NotImplementedError as e:
            st.warning(f"⚠️ {str(e)}")
            st.info("💡 该平台的处理功能正在开发中，敬请期待！")
            
        except Exception as e:
            st.error(f"❌ 处理失败：{str(e)}")
            with st.expander("查看详细错误信息"):
                st.exception(e)

else:
    st.info("👆 请上传数据文件开始处理")

# 页脚
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: gray; font-size: 12px;'>
    电商数据处理系统 v1.0 | 仅供内部使用 | 当前平台：{selected_platform}
    </div>
    """,
    unsafe_allow_html=True
)

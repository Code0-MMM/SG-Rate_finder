import hmac
import os
import shutil
from datetime import datetime
import streamlit as st
from config import DB_PATH, DATA, PUBLISHED_PATH
from excel_parser import parse_excel, ParseError
from database import replace_data
from publish_data import publish


def setting(name, default=''):
    value = os.environ.get(name)
    if value:
        return value
    try:
        return st.secrets.get(name, default)
    except FileNotFoundError:
        return default


st.set_page_config(page_title="SG Rate Finder Admin", layout="centered")
st.title("SG Rate Finder · 管理")
password = setting('ADMIN_PASSWORD')
if not password:
    st.error("请先配置 ADMIN_PASSWORD。")
    st.stop()
if not st.session_state.get('admin_authenticated', False):
    with st.form('admin_login'):
        entered = st.text_input("管理员密码", type="password")
        submitted = st.form_submit_button("登录")
    if submitted:
        if hmac.compare_digest(entered.encode('utf-8'), password.encode('utf-8')):
            st.session_state['admin_authenticated'] = True
            st.rerun()
        st.error("密码不正确。请使用启动此管理员程序时设置的 ADMIN_PASSWORD。")
    st.stop()

st.info("确认更新后，请将 data/published_rates.json 手动上传到 GitHub。")

uploaded = st.file_uploader("选择Excel", type=['xlsx', 'xlsm'])
if uploaded is None:
    st.stop()
payload = uploaded.getvalue()
if st.button("分析"):
    try:
        from io import BytesIO
        parsed = parse_excel(BytesIO(payload), uploaded.name)
        st.session_state['preview'] = (payload, uploaded.name, parsed)
    except ParseError as exc:
        st.session_state.pop('preview', None)
        st.error(f"更新失败。现有数据未发生变化。{exc}")
preview = st.session_state.get('preview')
if preview and preview[0] == payload and preview[1] == uploaded.name:
    _, filename, parsed = preview
    st.success("解析完成")
    st.write(f"文件：{filename}")
    st.write(f"Sheet：①SG点数表 · 一般点：{len(parsed.general_rates)}项 · 个别品牌：{len(parsed.brands)}项")
    st.write(f"Sheet：③S活动 · REF项目：{len(parsed.s_events)}项")
    st.write(f"最新适用日：{parsed.latest_effective_date} · 备注：{sum(bool(b['note']) for b in parsed.brands)}项")
    for warning in parsed.warnings[:20]:
        st.warning(warning)
    if st.button("确认更新", type="primary"):
        try:
            backup = None
            if DB_PATH.exists():
                backup_dir = DATA / 'backups'
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup = backup_dir / f"sg_rate_{datetime.now():%Y%m%d_%H%M%S}.db"
                shutil.copy2(DB_PATH, backup)
            replace_data(parsed, filename)
            if backup:
                for old in sorted(backup.parent.glob('sg_rate_*.db'), reverse=True)[5:]:
                    old.unlink()
            st.session_state.pop('preview', None)
        except Exception:
            st.error("更新失败。现有数据未发生变化。")
        else:
            try:
                publish(DB_PATH, PUBLISHED_PATH)
                st.success("本地数据已更新。请将 data/published_rates.json 手动上传到 GitHub。")
            except (OSError, ValueError):
                st.error("本地数据已更新，但公开용 JSON 생성에 실패했습니다. python publish_data.py 를 실행해 다시 생성하세요.")

import html
import streamlit as st
from database import load_data, load_master, load_s_events
from search_engine import normalize
from rate_engine import current_rate, general_for_category, format_rate

st.set_page_config(page_title="SG Rate Finder", page_icon="🔎", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""<style>.block-container{max-width:620px;padding:1rem 1rem 3rem}h1{font-size:1.65rem!important}.rate-card{background:#f7f9fc;border:1px solid #e4e8ef;border-radius:18px;padding:24px;margin-top:16px}.big-rate{font-size:5rem;font-weight:800;line-height:1.15;color:#18233c}.brand{font-size:1.5rem;font-weight:700}.meta{color:#586478;margin-top:12px}.note{background:#fff4db;border-radius:10px;padding:12px;margin-top:16px}</style>""", unsafe_allow_html=True)
st.title("SG RATE FINDER")
st.caption("品牌点数查询")
try:
    brands, general, meta = load_data()
    master = load_master()
    s_events = load_s_events()
except Exception:
    st.error("目前没有可查询的数据。")
    st.stop()
st.caption(f"更新：{meta.get('last_update', '-').replace('-', '.')}")
if not brands:
    st.info("目前尚未导入SG点数表。")
    st.stop()

by_id = {b['id']: b for b in brands}
selected_id = st.selectbox(
    "🔍 品牌搜索",
    options=[b['id'] for b in brands],
    index=None,
    placeholder="输入品牌英文 / 韩文，例如 CH",
    format_func=lambda brand_id: f"{by_id[brand_id]['brand_name']} · {by_id[brand_id]['category']}",
)
choice = by_id.get(selected_id)
with st.expander("品牌不在列表？查询一般点"):
    query = st.text_input("品牌名称", placeholder="输入未列出的品牌")

result = None
kind = ""
if choice:
    result = current_rate(choice['rates'])
    kind = "个别品牌点数"
    category = choice['category']
    payment = choice['payment_method']
    note = choice['note']
    name = choice['brand_name']
elif query.strip():
    st.info("未找到个别品牌点数。可选择一般点分类进行查询。")
    category = master.get(normalize(query))
    categories = list(dict.fromkeys(r['category'].replace(' 一般点', '').strip() for r in general))
    if category:
        st.caption(f"品牌分类主数据：{category}")
    else:
        category = st.selectbox("请选择品牌分类", ["请选择"] + categories)
    if category != "请选择":
        result = general_for_category(general, category)
        kind = "一般点"
        payment = next((r['payment_method'] for r in general if r['category'].replace(' 一般点', '').strip() == category), "")
        note = ""
        name = query.strip()

if kind:
    if result is None:
        st.warning("当前日期尚无适用点数。")
    else:
        esc = html.escape
        note_html = f'<div class="note">⚠ 备注<br>{esc(note)}</div>' if note else ''
        st.markdown(f'''<div class="rate-card"><div class="brand">{esc(name)}</div><div class="big-rate">{format_rate(result['rate'])}</div><strong>{kind}</strong><div class="meta">分类　{esc(category)}<br>支付方式　{esc(payment)}<br>适用日期　{result['effective_date'].replace('-', '.')}~</div>{note_html}</div>''', unsafe_allow_html=True)

st.divider()
st.subheader("S活动查询")
if not s_events:
    st.info("目前尚未导入S活动数据。请使用管理员程序重新导入含③S活动的Excel。")
else:
    s_brands = sorted({event['brand_name'] for event in s_events}, key=normalize)
    s_brand = st.selectbox("S活动品牌", s_brands, index=None, placeholder="输入品牌名称，例如 AMI")
    s_query = st.text_input("REF NO. / AGING 搜索", placeholder="输入型号或AGING，可单独搜索")
    if s_brand or s_query.strip():
        q = normalize(s_query)
        matched = [event for event in s_events
                   if (not s_brand or event['brand_name'] == s_brand)
                   and (not q or any(q in normalize(event[key]) for key in ('brand_name', 'aging', 'ref_no')))]
        st.caption(f"符合条件：{len(matched)}项")
        if not matched:
            st.info("没有符合条件的S活动项目。")
        for event in matched[:50]:
            s_rate = current_rate(event['rates'])
            rate_text = format_rate(s_rate['rate']) if s_rate else "暂无适用点数"
            effective = s_rate['effective_date'].replace('-', '.') + '~' if s_rate else '-'
            st.markdown(f'''<div class="rate-card"><div class="brand">{html.escape(event['brand_name'])}</div><div style="font-size:2rem;font-weight:800;color:#18233c">{rate_text}</div><div class="meta">REF NO.　{html.escape(event['ref_no'])}<br>AGING　{html.escape(event['aging'])}<br>适用日期　{effective}</div></div>''', unsafe_allow_html=True)
        if len(matched) > 50:
            st.caption("仅显示前50项。请输入 REF NO. 或 AGING 缩小范围。")
    else:
        st.caption("选择品牌，或输入 REF NO. / AGING 查询。")

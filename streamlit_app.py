import streamlit as st
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="🛡️ ماسح INCI الذكي", layout="wide")

st.title("🛡️ الماسح الضوئي الذكي للتركيبات")
st.write("أدخلي قائمة المكونات (INCI) وسأخبركِ إذا كانت آمنة أم لا.")

# قراءة ملف الإكسل
try:
    df = pd.read_excel('cosmetic_active_ingredients-1.xlsx', sheet_name='Ingredients', header=1)
    df_ref = df[['Scientific / INCI Name', 'Max Safe %']].copy()
    df_ref.columns = ['Ingredient', 'Max_Percentage']
    df_ref = df_ref.dropna(subset=['Ingredient'])
    st.sidebar.success(f"✅ قاعدة البيانات جاهزة ({len(df_ref)} مادة)")
except Exception as e:
    st.sidebar.error(f"⚠️ لم أجد ملف الإكسل. تأكدي من رفعه: {e}")
    st.stop()

# واجهة الإدخال
st.subheader("📋 أدخلي تركيبة العميلة")
input_text = st.text_area("اكتبي القائمة (مثال: Glycerin:15, Coconut Oil:10)")

if st.button("🔍 افحصي التركيبة"):
    if not input_text:
        st.warning("الرجاء إدخال قائمة.")
    else:
        results = []
        for line in input_text.split(','):
            if ':' not in line:
                continue
            name, perc_str = line.split(':')
            name = name.strip()
            try:
                client_perc = float(perc_str.strip())
            except:
                continue
            
            row = df_ref[df_ref['Ingredient'].str.lower() == name.lower()]
            if row.empty:
                results.append({'المادة': name, 'التركيز': client_perc, 'الحالة': '⚠️ غير موجودة'})
            else:
                max_val = row.iloc[0]['Max_Percentage']
                if client_perc <= max_val:
                    status = '✅ آمن'
                elif client_perc <= max_val * 1.15:
                    status = '⚠️ قريب من الحد'
                else:
                    status = '🚨 خطر! تجاوز الحد'
                results.append({'المادة': name, 'التركيز': client_perc, 'الحد الأقصى': max_val, 'الحالة': status})
        
        result_df = pd.DataFrame(results)
        st.subheader("📊 النتيجة")
        st.dataframe(result_df, use_container_width=True)
        
        if '🚨' in result_df['الحالة'].values:
            st.error("🚨 تنبيه: هناك مواد خطيرة!")
        else:
            st.success("🎉 جميع المواد آمنة!")

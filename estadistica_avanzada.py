import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import norm, chi2, f, t
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

try:
    plt.style.use('seaborn-v0_8-whitegrid')
except:
    plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (10, 6)

# Funciones auxiliares
def exportar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Resultados')
    return output.getvalue()

def exportar_pdf(texto):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    w, h = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, h - 50, "Analisis Estadistico")
    c.setFont("Helvetica", 12)
    y = h - 100
    for line in texto.split('\n'):
        if y < 50:
            c.showPage()
            y = h - 50
        c.drawString(50, y, line)
        y -= 20
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# Configuración
st.set_page_config(page_title="Analisis Avanzado", layout="wide", page_icon="📊")

with st.sidebar:
    st.title("📚 Estadistica Avanzada")
    st.markdown("""
    - ANOVA
    - Correlacion
    - Regresion
    - No Parametricas
    - Chi-cuadrado
    - Tamano Muestra
    - Diseno Experimental
    """)

st.title("🎓 Analisis Estadistico Avanzado")
st.markdown("Herramientas para analisis complejos y diseno experimental")

tabs = st.tabs(["📊 ANOVA", "🔗 Correlacion", "📈 Regresion", "📉 No Parametricas", 
                "✖️ Chi-cuadrado", "🔢 Tamano Muestra", "🌱 Diseno Experimental"])

# TAB 1: ANOVA
with tabs[0]:
    st.header("ANOVA")
    st.info("Funcionalidad básica de ANOVA - calcula F, p-value para comparar 3+ grupos")
    
    num_grupos = st.slider("Numero de grupos", 3, 6, 3)
    grupos = []
    for i in range(num_grupos):
        datos_str = st.text_input(f"Grupo {i+1} (separados por comas)", 
                                   ", ".join(map(str, np.random.normal(100+i*5, 10, 10).round(1))),
                                   key=f"g{i}")
        try:
            datos = [float(x.strip()) for x in datos_str.split(',')]
            grupos.append(datos)
        except:
            grupos.append([])
    
    if st.button("Calcular ANOVA"):
        if all(len(g) > 0 for g in grupos):
            f_stat, p_val = stats.f_oneway(*grupos)
            st.metric("Estadistico F", f"{f_stat:.4f}")
            st.metric("p-value", f"{p_val:.4f}")
            if p_val < 0.05:
                st.success("✅ Diferencias significativas")
            else:
                st.info("❌ No significativo")

# TAB 2: Correlación
with tabs[1]:
    st.header("Correlacion")
    n = st.slider("Numero de datos", 10, 200, 50)
    r_real = st.slider("Correlacion a simular", -1.0, 1.0, 0.7, 0.05)
    tipo = st.selectbox("Tipo", ["pearson", "spearman"])
    
    mean = [0, 0]
    cov = [[1, r_real], [r_real, 1]]
    x, y = np.random.multivariate_normal(mean, cov, n).T
    
    if tipo == "pearson":
        r, p = stats.pearsonr(x, y)
    else:
        r, p = stats.spearmanr(x, y)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Correlacion", f"{r:.4f}")
        st.metric("p-value", f"{p:.4f}")
        st.metric("R²", f"{r**2:.4f}")
    
    with col2:
        fig, ax = plt.subplots()
        ax.scatter(x, y, alpha=0.6)
        z = np.polyfit(x, y, 1)
        p_line = np.poly1d(z)
        ax.plot(x, p_line(x), "r--", linewidth=2)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(f'Correlacion {tipo}: r = {r:.3f}')
        ax.grid(True, alpha=0.3)
        plt.close()
        st.pyplot(fig)

# TAB 3: Regresión
with tabs[2]:
    st.header("Regresion Lineal Simple")
    n_reg = st.slider("Observaciones", 10, 200, 50, key="nr")
    beta0 = st.slider("Intercepto real", -50.0, 50.0, 10.0, 0.1)
    beta1 = st.slider("Pendiente real", -5.0, 5.0, 2.0, 0.1)
    ruido = st.slider("Ruido", 0.1, 20.0, 5.0, 0.1)
    
    x_reg = np.linspace(0, 10, n_reg)
    y_reg = beta0 + beta1 * x_reg + np.random.normal(0, ruido, n_reg)
    
    if st.button("Calcular Regresion"):
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_reg, y_reg)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Intercepto (β₀)", f"{intercept:.4f}")
            st.metric("Pendiente (β₁)", f"{slope:.4f}")
            st.metric("R²", f"{r_value**2:.4f}")
            st.metric("p-value", f"{p_value:.4f}")
        
        with col2:
            fig, ax = plt.subplots()
            ax.scatter(x_reg, y_reg, alpha=0.6)
            ax.plot(x_reg, intercept + slope*x_reg, 'r-', linewidth=2)
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_title(f'Y = {intercept:.2f} + {slope:.2f}X')
            ax.grid(True, alpha=0.3)
            plt.close()
            st.pyplot(fig)

# TAB 4: No Paramétricas
with tabs[3]:
    st.header("Pruebas No Parametricas")
    prueba = st.selectbox("Selecciona:", ["Mann-Whitney U", "Kruskal-Wallis", "Wilcoxon"])
    
    if prueba == "Mann-Whitney U":
        g1_str = st.text_input("Grupo 1", "23, 25, 27, 29, 31, 33")
        g2_str = st.text_input("Grupo 2", "18, 20, 22, 24, 26, 28")
        
        if st.button("Calcular"):
            try:
                g1 = [float(x.strip()) for x in g1_str.split(',')]
                g2 = [float(x.strip()) for x in g2_str.split(',')]
                u_stat, p = stats.mannwhitneyu(g1, g2)
                st.metric("U", f"{u_stat:.0f}")
                st.metric("p-value", f"{p:.4f}")
                if p < 0.05:
                    st.success("✅ Diferencia significativa")
            except:
                st.error("Error en formato")

# TAB 5: Chi-cuadrado
with tabs[4]:
    st.header("Chi-cuadrado de Independencia")
    filas = st.slider("Filas", 2, 5, 2, key="f")
    cols = st.slider("Columnas", 2, 5, 2, key="c")
    
    st.write("Ingresa frecuencias:")
    tabla = []
    for i in range(filas):
        fila = []
        cols_input = st.columns(cols)
        for j in range(cols):
            with cols_input[j]:
                val = st.number_input(f"F{i+1}C{j+1}", min_value=0, value=25, key=f"chi{i}{j}")
                fila.append(val)
        tabla.append(fila)
    
    if st.button("Calcular Chi²"):
        tabla_array = np.array(tabla)
        chi2_stat, p, dof, expected = stats.chi2_contingency(tabla_array)
        
        st.metric("Chi²", f"{chi2_stat:.4f}")
        st.metric("p-value", f"{p:.4f}")
        st.metric("gl", dof)
        
        if p < 0.05:
            st.success("✅ Variables asociadas")
        else:
            st.info("❌ Variables independientes")

# TAB 6: Tamaño de Muestra
with tabs[5]:
    st.header("Calculadora de Tamano de Muestra")
    tipo_calc = st.selectbox("Para:", ["Diferencia de Medias", "Diferencia de Proporciones"])
    
    if tipo_calc == "Diferencia de Medias":
        delta = st.number_input("Diferencia a detectar (δ)", min_value=0.1, value=5.0, step=0.1)
        sigma = st.number_input("Desviacion estandar (σ)", min_value=0.1, value=10.0, step=0.1)
        alpha = st.select_slider("α", [0.01, 0.05, 0.10], value=0.05)
        beta = st.select_slider("β", [0.05, 0.10, 0.20], value=0.20)
        
        z_alpha = norm.ppf(1 - alpha/2)
        z_beta = norm.ppf(1 - beta)
        n = int(np.ceil(((z_alpha + z_beta) * sigma / delta) ** 2 * 2))
        
        st.metric("n por grupo", n)
        st.metric("n total", 2*n)
        st.metric("Potencia", f"{1-beta:.0%}")
        
        d_cohen = delta / sigma
        st.info(f"Tamano del efecto (d) = {d_cohen:.3f}")

# TAB 7: Diseño Experimental
with tabs[6]:
    st.header("🌱 Diseno Experimental")
    
    with st.expander("ℹ️ Conexion Δ y d de Cohen"):
        st.markdown("""
        **Enfoque tradicional:** Δ (diferencia en unidades reales)
        
        **Enfoque moderno:** d = Δ / σ (estandarizado)
        
        **Ejemplo:** Si Δ = 15 kg/ha y σ = 10 kg/ha → d = 1.5 (efecto grande)
        """)
    
    diseno = st.selectbox("Tipo de diseno:", 
                         ["DCA - Completamente al Azar", 
                          "DBCA - Bloques Completos", 
                          "Factorial (AxB)"])
    
    if diseno == "DCA - Completamente al Azar":
        st.subheader("DCA")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            metodo = st.radio("Entrada:", ["Por Δ", "Por d"])
            k = st.number_input("Tratamientos (k)", 2, 20, 4)
            
            if metodo == "Por Δ":
                delta = st.number_input("Δ (diferencia minima)", 0.1, 100.0, 15.0, 0.5)
                sigma = st.number_input("σ (error exp.)", 0.1, 100.0, 10.0, 0.5)
                d = delta / sigma
                st.info(f"d = {d:.3f}")
            else:
                d = st.slider("d (tamano efecto)", 0.1, 3.0, 1.5, 0.1)
                sigma = st.number_input("σ (referencia)", 0.1, 100.0, 10.0, 0.5, key="s2")
                delta = d * sigma
                st.info(f"Δ = {delta:.2f}")
            
            alpha = st.select_slider("α", [0.01, 0.05, 0.10], value=0.05, key="a1")
            potencia = st.select_slider("Potencia", [0.70, 0.80, 0.90], value=0.80)
        
        with col2:
            beta = 1 - potencia
            z_a = norm.ppf(1 - alpha/2)
            z_b = norm.ppf(potencia)
            
            n_base = 2 * ((z_a + z_b) / d) ** 2
            if k > 2:
                ajuste = 1 + 0.15 * (k - 2)
                n = int(np.ceil(n_base * ajuste))
            else:
                n = int(np.ceil(n_base))
            n = max(n, 3)
            
            st.metric("Replicas (r)", n)
            st.metric("Total unidades", k * n)
            st.metric("gl error", (k-1)*(n-1))
            
            if d < 0.5:
                efecto = "Pequeño 🟡"
            elif d < 0.8:
                efecto = "Mediano 🔵"
            else:
                efecto = "Grande 🟢"
            
            st.success(f"""
            Tamano del efecto: {efecto}
            
            Con {n} replicas por tratamiento detectas 
            diferencia de {delta:.2f} unidades con 
            {potencia*100:.0f}% de potencia.
            """)
        
        # Croquis
        st.subheader("Croquis del DCA")
        fig, ax = plt.subplots(figsize=(min(12, k*1.2), max(4, n*0.5)))
        colores = plt.cm.Set3(np.linspace(0, 1, k))
        
        for i in range(k):
            for j in range(n):
                rect = plt.Rectangle((i, j), 0.9, 0.9, 
                                    facecolor=colores[i], edgecolor='black', linewidth=2)
                ax.add_patch(rect)
                ax.text(i+0.45, j+0.45, f'T{i+1}\nR{j+1}', 
                       ha='center', va='center', fontsize=10, fontweight='bold')
        
        ax.set_xlim(0, k)
        ax.set_ylim(0, n)
        ax.set_aspect('equal')
        ax.set_xlabel('Tratamientos')
        ax.set_ylabel('Replicas')
        ax.set_title(f'DCA: {k} tratamientos × {n} replicas = {k*n} unidades')
        ax.grid(False)
        plt.close()
        st.pyplot(fig)
        
        df = pd.DataFrame([{
            'Diseno': 'DCA',
            'Tratamientos': k,
            'Replicas': n,
            'Total': k*n,
            'Δ': f"{delta:.2f}",
            'σ': f"{sigma:.2f}",
            'd': f"{d:.3f}",
            'Potencia': f"{potencia:.0%}"
        }])
        st.dataframe(df)
        st.download_button("📥 Excel", exportar_excel(df), "dca.xlsx")
    
    elif diseno == "DBCA - Bloques Completos":
        st.subheader("DBCA")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            metodo = st.radio("Entrada:", ["Por Δ", "Por d"], key="m2")
            k = st.number_input("Tratamientos (k)", 2, 20, 4, key="k2")
            
            if metodo == "Por Δ":
                delta = st.number_input("Δ", 0.1, 100.0, 12.0, 0.5, key="d1")
                sigma = st.number_input("σ", 0.1, 100.0, 8.0, 0.5, key="s1")
                d = delta / sigma
            else:
                d = st.slider("d", 0.1, 3.0, 1.5, 0.1, key="d2")
                sigma = st.number_input("σ", 0.1, 100.0, 8.0, 0.5, key="s3")
                delta = d * sigma
            
            efic = st.slider("Eficiencia bloques (%)", 0, 50, 20, 5)
            alpha = st.select_slider("α", [0.01, 0.05, 0.10], value=0.05, key="a2")
            pot = st.select_slider("Potencia", [0.70, 0.80, 0.90], value=0.80, key="p2")
        
        with col2:
            factor_efic = 1 - (efic/100)
            d_efec = d / np.sqrt(factor_efic)
            
            z_a = norm.ppf(1 - alpha/2)
            z_b = norm.ppf(pot)
            n_base = 2 * ((z_a + z_b) / d_efec) ** 2
            
            if k > 2:
                n = int(np.ceil(n_base * (1 + 0.15 * (k-2))))
            else:
                n = int(np.ceil(n_base))
            n = max(n, 3)
            
            st.metric("Bloques (r)", n)
            st.metric("Parcelas/bloque", k)
            st.metric("Total", k*n)
            st.metric("gl error", (k-1)*(n-1))
            
            st.success(f"""
            Con {n} bloques detectas diferencia de 
            {delta:.2f} unidades con {pot*100:.0f}% potencia.
            
            Bloques reducen error en ~{efic}%.
            """)
        
        # Croquis
        fig, ax = plt.subplots(figsize=(max(10, k*1.2), max(6, n*0.8)))
        colores = plt.cm.Set3(np.linspace(0, 1, k))
        
        np.random.seed(42)
        for j in range(n):
            trat_orden = np.random.permutation(k)
            for i, trat in enumerate(trat_orden):
                rect = plt.Rectangle((i, j), 0.9, 0.9,
                                    facecolor=colores[trat], edgecolor='black', linewidth=2)
                ax.add_patch(rect)
                ax.text(i+0.45, j+0.45, f'T{trat+1}',
                       ha='center', va='center', fontsize=11, fontweight='bold')
            ax.text(-0.5, j+0.45, f'B{j+1}', ha='right', va='center', 
                   fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='lightgray'))
        
        ax.set_xlim(-1, k)
        ax.set_ylim(0, n)
        ax.set_aspect('equal')
        ax.set_xlabel('Posicion')
        ax.set_ylabel('Bloques')
        ax.set_title(f'DBCA: {k} tratamientos en {n} bloques')
        ax.grid(False)
        plt.close()
        st.pyplot(fig)
        
        df = pd.DataFrame([{
            'Diseno': 'DBCA',
            'Tratamientos': k,
            'Bloques': n,
            'Total': k*n,
            'Δ': f"{delta:.2f}",
            'd': f"{d:.3f}",
            'Eficiencia': f"{efic}%",
            'Potencia': f"{pot:.0%}"
        }])
        st.dataframe(df)
        st.download_button("📥 Excel", exportar_excel(df), "dbca.xlsx", key="db")
    
    else:  # Factorial
        st.subheader("Factorial A×B")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            a = st.number_input("Niveles Factor A", 2, 10, 3)
            b = st.number_input("Niveles Factor B", 2, 10, 4)
            total_trat = a * b
            st.info(f"Total tratamientos: {total_trat} ({a}×{b})")
            
            metodo = st.radio("Entrada:", ["Por Δ", "Por d"], key="m3")
            
            if metodo == "Por Δ":
                delta = st.number_input("Δ", 0.1, 100.0, 10.0, 0.5, key="d3")
                sigma = st.number_input("σ", 0.1, 100.0, 8.0, 0.5, key="s4")
                d = delta / sigma
            else:
                d = st.slider("d", 0.1, 3.0, 1.25, 0.1, key="d4")
                sigma = st.number_input("σ", 0.1, 100.0, 8.0, 0.5, key="s5")
                delta = d * sigma
            
            alpha = st.select_slider("α", [0.01, 0.05, 0.10], value=0.05, key="a3")
            pot = st.select_slider("Potencia", [0.70, 0.80, 0.90], value=0.80, key="p3")
        
        with col2:
            z_a = norm.ppf(1 - alpha/2)
            z_b = norm.ppf(pot)
            n_base = 2 * ((z_a + z_b) / d) ** 2
            ajuste = 1 + 0.20 * np.log(total_trat)
            n = max(int(np.ceil(n_base * ajuste)), 3)
            
            st.metric("Replicas (r)", n)
            st.metric("Combinaciones", total_trat)
            st.metric("Total", total_trat * n)
            
            gl_a = a - 1
            gl_b = b - 1
            gl_ab = gl_a * gl_b
            gl_e = total_trat * (n - 1)
            
            st.write("**Grados de libertad:**")
            df_gl = pd.DataFrame({
                'Fuente': ['A', 'B', 'A×B', 'Error'],
                'gl': [gl_a, gl_b, gl_ab, gl_e]
            })
            st.dataframe(df_gl)
            
            st.success(f"""
            Detecta efectos principales e interaccion 
            con {pot*100:.0f}% potencia.
            """)
        
        # Matriz
        fig, ax = plt.subplots(figsize=(max(8, b*1.5), max(6, a*1.2)))
        colores = plt.cm.viridis(np.linspace(0, 1, total_trat))
        
        idx = 0
        for i in range(a):
            for j in range(b):
                rect = plt.Rectangle((j, a-1-i), 0.9, 0.9,
                                    facecolor=colores[idx], edgecolor='black', linewidth=2)
                ax.add_patch(rect)
                ax.text(j+0.45, a-1-i+0.45, f'A{i+1}B{j+1}\n(n={n})',
                       ha='center', va='center', fontsize=10, 
                       fontweight='bold', color='white')
                idx += 1
        
        ax.set_xlim(0, b)
        ax.set_ylim(0, a)
        ax.set_aspect('equal')
        ax.set_xlabel('Factor B', fontsize=14, fontweight='bold')
        ax.set_ylabel('Factor A', fontsize=14, fontweight='bold')
        ax.set_title(f'Factorial {a}×{b} ({total_trat} trat., {n} rep. c/u)')
        ax.grid(False)
        plt.close()
        st.pyplot(fig)
        
        df = pd.DataFrame([{
            'Diseno': f'Factorial {a}×{b}',
            'Tratamientos': total_trat,
            'Replicas': n,
            'Total': total_trat*n,
            'd': f"{d:.3f}",
            'Potencia': f"{pot:.0%}"
        }])
        st.dataframe(df)
        st.download_button("📥 Excel", exportar_excel(df), "factorial.xlsx", key="fa")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
<p>📊 Analisis Estadistico Avanzado</p>
<p><small>Herramienta educativa - Version 1.0</small></p>
</div>
""", unsafe_allow_html=True)

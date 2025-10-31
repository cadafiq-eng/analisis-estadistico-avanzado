# ==================== TAB 7: DISEÑO EXPERIMENTAL ====================
with tabs[6]:
    st.header("🌱 Diseno Experimental - Calculo de Replicas")
    
    with st.expander("ℹ️ Informacion General"):
        st.markdown("""
        ### Concepto: Diferencia Minima Detectable (Δ) vs. Tamano del Efecto (d)
        
        **En Diseno Experimental tradicional usas:**
        - **Δ (Delta):** Diferencia minima que quieres detectar en unidades reales
        - **σ (Sigma):** Error experimental esperado
        
        **En Estadistica moderna se usa:**
        - **d de Cohen = Δ / σ** (estandarizado)
        
        **Son equivalentes:**
        - Si Δ = 15 kg/ha y σ = 10 kg/ha → d = 1.5 (efecto grande)
        - Si Δ = 5 kg/ha y σ = 10 kg/ha → d = 0.5 (efecto mediano)
        
        ---
        
        ### Tipos de Diseno Soportados:
        1. **DCA (Completamente al Azar):** Tratamientos asignados aleatoriamente
        2. **DBCA (Bloques Completos al Azar):** Control de heterogeneidad con bloques
        3. **Factorial:** Estudio de interaccion entre factores
        """)
    
    tipo_diseno = st.selectbox(
        "Selecciona el tipo de diseno:",
        ["DCA - Completamente al Azar", 
         "DBCA - Bloques Completos al Azar",
         "Factorial (AxB)"]
    )
    
    # ==================== DCA ====================
    if tipo_diseno == "DCA - Completamente al Azar":
        st.subheader("Diseno Completamente al Azar (DCA)")
        
        with st.expander("📖 Sobre el DCA"):
            st.markdown("""
            **Caracteristicas:**
            - Asignacion completamente aleatoria de tratamientos a unidades experimentales
            - Unidades experimentales homogeneas
            - Mas simple pero menos eficiente si hay heterogeneidad
            
            **Modelo:** Yij = μ + τi + εij
            
            **Cuando usarlo:**
            - Condiciones experimentales homogeneas (invernadero, laboratorio)
            - Material experimental uniforme
            - No hay fuentes identificables de variacion
            
            **Ejemplo:** Comparar 5 variedades de maiz en condiciones controladas
            """)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Parametros del Experimento")
            
            # Opcion de entrada
            metodo_entrada = st.radio(
                "Metodo de entrada:",
                ["Por Δ (diferencia absoluta)", "Por d (tamano del efecto)"],
                key="metodo_dca"
            )
            
            num_trat_dca = st.number_input(
                "Numero de tratamientos (k)",
                min_value=2,
                max_value=20,
                value=4,
                key="k_dca"
            )
            
            if metodo_entrada == "Por Δ (diferencia absoluta)":
                st.markdown("**Enfoque tradicional (unidades reales):**")
                delta_dca = st.number_input(
                    "Diferencia minima a detectar (Δ)",
                    min_value=0.1,
                    value=15.0,
                    step=0.5,
                    help="Diferencia entre medias extremas en unidades de tu variable",
                    key="delta_dca"
                )
                sigma_dca = st.number_input(
                    "Error experimental esperado (σ)",
                    min_value=0.1,
                    value=10.0,
                    step=0.5,
                    help="Desviacion estandar del error experimental",
                    key="sigma_dca"
                )
                d_calculado = delta_dca / sigma_dca
                st.info(f"**d calculado = {d_calculado:.3f}**")
            else:
                st.markdown("**Enfoque estandarizado:**")
                d_calculado = st.slider(
                    "Tamano del efecto (d)",
                    min_value=0.1,
                    max_value=3.0,
                    value=1.5,
                    step=0.1,
                    key="d_dca"
                )
                sigma_dca = st.number_input(
                    "Error experimental (σ) - solo para referencia",
                    min_value=0.1,
                    value=10.0,
                    step=0.5,
                    key="sigma_ref_dca"
                )
                delta_dca = d_calculado * sigma_dca
                st.info(f"**Δ equivalente = {delta_dca:.2f} unidades**")
            
            alpha_dca = st.select_slider(
                "Nivel de significancia (α)",
                options=[0.01, 0.05, 0.10],
                value=0.05,
                key="alpha_dca"
            )
            
            potencia_dca = st.select_slider(
                "Potencia deseada (1-β)",
                options=[0.70, 0.75, 0.80, 0.85, 0.90, 0.95],
                value=0.80,
                key="pot_dca"
            )
            beta_dca = 1 - potencia_dca
        
        with col2:
            st.markdown("### Resultados")
            
            # Calculo de replicas para DCA usando aproximacion
            # Formula: n ≈ 2(Zα + Zβ)² / d²  para comparacion de 2 medias
            # Para k grupos, ajustamos con factor de correccion
            z_alpha = norm.ppf(1 - alpha_dca / 2)
            z_beta = norm.ppf(potencia_dca)
            
            # Para DCA con k grupos (aproximacion conservadora)
            n_base = 2 * ((z_alpha + z_beta) / d_calculado) ** 2
            
            # Factor de ajuste para comparaciones multiples (Bonferroni conservador)
            if num_trat_dca > 2:
                ajuste = 1 + 0.15 * (num_trat_dca - 2)  # Ajuste empirico
                n_replicas_dca = int(np.ceil(n_base * ajuste))
            else:
                n_replicas_dca = int(np.ceil(n_base))
            
            # Asegurar minimo de replicas
            n_replicas_dca = max(n_replicas_dca, 3)
            
            st.metric("Replicas por tratamiento (r)", n_replicas_dca)
            st.metric("Unidades experimentales totales", num_trat_dca * n_replicas_dca)
            st.metric("Grados de libertad error", (num_trat_dca - 1) * (n_replicas_dca - 1))
            
            # Interpretacion del tamano del efecto
            if d_calculado < 0.2:
                efecto_interp = "Muy pequeño"
                color_badge = "🟡"
            elif d_calculado < 0.5:
                efecto_interp = "Pequeño"
                color_badge = "🟢"
            elif d_calculado < 0.8:
                efecto_interp = "Mediano"
                color_badge = "🔵"
            elif d_calculado < 1.2:
                efecto_interp = "Grande"
                color_badge = "🟣"
            else:
                efecto_interp = "Muy grande"
                color_badge = "🔴"
            
            st.success(f"""
            {color_badge} **Tamano del efecto:** {efecto_interp}
            
            **Interpretacion:**
            Con {n_replicas_dca} replicas por tratamiento, 
            tienes {potencia_dca*100:.0f}% de probabilidad de 
            detectar una diferencia de {delta_dca:.2f} unidades 
            (d = {d_calculado:.3f}) con α = {alpha_dca}.
            """)
            
            # Analisis de sensibilidad
            st.markdown("### Analisis de Sensibilidad")
            replicas_alt = [max(3, n_replicas_dca - 2), n_replicas_dca, n_replicas_dca + 2]
            potencias_alt = []
            
            for r_alt in replicas_alt:
                # Recalcular potencia con diferentes replicas
                ncp = d_calculado * np.sqrt(r_alt / 2)
                pot_alt = 1 - norm.cdf(z_alpha - ncp)
                potencias_alt.append(pot_alt)
            
            df_sens_dca = pd.DataFrame({
                'Replicas': replicas_alt,
                'Unidades totales': [r * num_trat_dca for r in replicas_alt],
                'Potencia estimada': [f"{p:.2%}" for p in potencias_alt]
            })
            st.dataframe(df_sens_dca, use_container_width=True)
        
        # Tabla resumen
        st.markdown("### Tabla Resumen del Diseno")
        df_resumen_dca = pd.DataFrame([{
            'Diseno': 'DCA',
            'Tratamientos (k)': num_trat_dca,
            'Replicas (r)': n_replicas_dca,
            'Total unidades': num_trat_dca * n_replicas_dca,
            'Δ': f"{delta_dca:.2f}",
            'σ': f"{sigma_dca:.2f}",
            'd Cohen': f"{d_calculado:.3f}",
            'α': alpha_dca,
            'Potencia': f"{potencia_dca:.2%}",
            'gl error': (num_trat_dca - 1) * (n_replicas_dca - 1)
        }])
        st.dataframe(df_resumen_dca, use_container_width=True)
        
        # Croquis del experimento
        st.markdown("### Croquis del Experimento")
        fig_dca, ax_dca = plt.subplots(figsize=(12, max(4, n_replicas_dca * 0.5)))
        
        colores = plt.cm.Set3(np.linspace(0, 1, num_trat_dca))
        
        for i in range(num_trat_dca):
            for j in range(n_replicas_dca):
                rect = plt.Rectangle((i, j), 0.9, 0.9, 
                                    facecolor=colores[i], 
                                    edgecolor='black', 
                                    linewidth=2)
                ax_dca.add_patch(rect)
                ax_dca.text(i + 0.45, j + 0.45, f'T{i+1}\nR{j+1}', 
                           ha='center', va='center', fontsize=10, fontweight='bold')
        
        ax_dca.set_xlim(0, num_trat_dca)
        ax_dca.set_ylim(0, n_replicas_dca)
        ax_dca.set_aspect('equal')
        ax_dca.set_xlabel('Tratamientos', fontsize=12)
        ax_dca.set_ylabel('Replicas', fontsize=12)
        ax_dca.set_title('DCA - Asignacion Aleatoria Completa', fontsize=14, fontweight='bold')
        ax_dca.set_xticks(np.arange(num_trat_dca) + 0.45)
        ax_dca.set_xticklabels([f'T{i+1}' for i in range(num_trat_dca)])
        ax_dca.set_yticks(np.arange(n_replicas_dca) + 0.45)
        ax_dca.set_yticklabels([f'R{j+1}' for j in range(n_replicas_dca)])
        ax_dca.grid(False)
        plt.close()
        st.pyplot(fig_dca)
        
        st.download_button("📥 Descargar Resumen", exportar_excel(df_resumen_dca), "diseno_dca.xlsx", key="dl_dca")
    
    # ==================== DBCA ====================
    elif tipo_diseno == "DBCA - Bloques Completos al Azar":
        st.subheader("Diseno de Bloques Completos al Azar (DBCA)")
        
        with st.expander("📖 Sobre el DBCA"):
            st.markdown("""
            **Caracteristicas:**
            - Agrupa unidades experimentales en bloques homogeneos
            - Cada bloque contiene todos los tratamientos
            - Controla variacion conocida (gradiente de fertilidad, tiempo, lote)
            - Mas eficiente que DCA cuando hay heterogeneidad
            
            **Modelo:** Yij = μ + τi + βj + εij
            
            **Cuando usarlo:**
            - Gradientes de fertilidad en campo
            - Diferentes lotes de material
            - Experimentos en el tiempo
            - Posiciones en invernadero
            
            **Ejemplo:** Comparar 4 variedades en campo con gradiente de fertilidad → 4 bloques
            
            **Ventaja:** Reduce el error experimental al eliminar variacion entre bloques
            """)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Parametros del Experimento")
            
            metodo_entrada_dbca = st.radio(
                "Metodo de entrada:",
                ["Por Δ (diferencia absoluta)", "Por d (tamano del efecto)"],
                key="metodo_dbca"
            )
            
            num_trat_dbca = st.number_input(
                "Numero de tratamientos (k)",
                min_value=2,
                max_value=20,
                value=4,
                key="k_dbca"
            )
            
            if metodo_entrada_dbca == "Por Δ (diferencia absoluta)":
                delta_dbca = st.number_input(
                    "Diferencia minima a detectar (Δ)",
                    min_value=0.1,
                    value=12.0,
                    step=0.5,
                    key="delta_dbca"
                )
                sigma_dbca = st.number_input(
                    "Error experimental esperado (σ)",
                    min_value=0.1,
                    value=8.0,
                    step=0.5,
                    help="Error DENTRO de bloques (menor que DCA)",
                    key="sigma_dbca"
                )
                d_calc_dbca = delta_dbca / sigma_dbca
                st.info(f"**d calculado = {d_calc_dbca:.3f}**")
            else:
                d_calc_dbca = st.slider(
                    "Tamano del efecto (d)",
                    min_value=0.1,
                    max_value=3.0,
                    value=1.5,
                    step=0.1,
                    key="d_dbca"
                )
                sigma_dbca = st.number_input(
                    "Error experimental (σ)",
                    min_value=0.1,
                    value=8.0,
                    step=0.5,
                    key="sigma_ref_dbca"
                )
                delta_dbca = d_calc_dbca * sigma_dbca
                st.info(f"**Δ equivalente = {delta_dbca:.2f} unidades**")
            
            eficiencia_bloques = st.slider(
                "Eficiencia esperada de bloques (%)",
                min_value=0,
                max_value=50,
                value=20,
                step=5,
                help="% de reduccion del error al usar bloques vs DCA",
                key="efic_dbca"
            )
            
            alpha_dbca = st.select_slider(
                "Nivel de significancia (α)",
                options=[0.01, 0.05, 0.10],
                value=0.05,
                key="alpha_dbca"
            )
            
            potencia_dbca = st.select_slider(
                "Potencia deseada (1-β)",
                options=[0.70, 0.75, 0.80, 0.85, 0.90, 0.95],
                value=0.80,
                key="pot_dbca"
            )
        
        with col2:
            st.markdown("### Resultados")
            
            z_alpha_dbca = norm.ppf(1 - alpha_dbca / 2)
            z_beta_dbca = norm.ppf(potencia_dbca)
            
            # Ajuste por eficiencia de bloques
            factor_eficiencia = 1 - (eficiencia_bloques / 100)
            d_efectivo = d_calc_dbca / np.sqrt(factor_eficiencia)
            
            n_base_dbca = 2 * ((z_alpha_dbca + z_beta_dbca) / d_efectivo) ** 2
            
            if num_trat_dbca > 2:
                ajuste_dbca = 1 + 0.15 * (num_trat_dbca - 2)
                n_bloques_dbca = int(np.ceil(n_base_dbca * ajuste_dbca))
            else:
                n_bloques_dbca = int(np.ceil(n_base_dbca))
            
            n_bloques_dbca = max(n_bloques_dbca, 3)
            
            st.metric("Numero de bloques (r)", n_bloques_dbca)
            st.metric("Parcelas por bloque", num_trat_dbca)
            st.metric("Unidades experimentales totales", num_trat_dbca * n_bloques_dbca)
            
            gl_trat = num_trat_dbca - 1
            gl_bloques = n_bloques_dbca - 1
            gl_error = gl_trat * gl_bloques
            
            st.metric("Grados de libertad error", gl_error)
            
            st.success(f"""
            **Interpretacion:**
            
            Con {n_bloques_dbca} bloques, cada uno con {num_trat_dbca} tratamientos,
            tienes {potencia_dbca*100:.0f}% de probabilidad de detectar 
            una diferencia de {delta_dbca:.2f} unidades.
            
            **Ganancia vs DCA:**
            Los bloques reducen el error en ~{eficiencia_bloques}%, 
            permitiendo usar menos replicas que DCA.
            """)
            
            # Comparacion con DCA
            st.markdown("### Comparacion con DCA")
            n_dca_equiv = int(np.ceil(n_bloques_dbca / factor_eficiencia))
            
            df_comp_dbca = pd.DataFrame({
                'Diseno': ['DBCA', 'DCA equivalente'],
                'Replicas/Bloques': [n_bloques_dbca, n_dca_equiv],
                'Unidades totales': [
                    num_trat_dbca * n_bloques_dbca,
                    num_trat_dbca * n_dca_equiv
                ],
                'Ahorro': ['', f'{((n_dca_equiv - n_bloques_dbca) / n_dca_equiv * 100):.0f}%']
            })
            st.dataframe(df_comp_dbca, use_container_width=True)
        
        # Tabla resumen
        st.markdown("### Tabla Resumen del Diseno")
        df_resumen_dbca = pd.DataFrame([{
            'Diseno': 'DBCA',
            'Tratamientos (k)': num_trat_dbca,
            'Bloques (r)': n_bloques_dbca,
            'Total unidades': num_trat_dbca * n_bloques_dbca,
            'Δ': f"{delta_dbca:.2f}",
            'σ': f"{sigma_dbca:.2f}",
            'd Cohen': f"{d_calc_dbca:.3f}",
            'Eficiencia': f"{eficiencia_bloques}%",
            'α': alpha_dbca,
            'Potencia': f"{potencia_dbca:.2%}",
            'gl error': gl_error
        }])
        st.dataframe(df_resumen_dbca, use_container_width=True)
        
        # Croquis
        st.markdown("### Croquis del Experimento")
        fig_dbca, ax_dbca = plt.subplots(figsize=(max(10, num_trat_dbca * 1.2), max(6, n_bloques_dbca * 0.8)))
        
        colores_dbca = plt.cm.Set3(np.linspace(0, 1, num_trat_dbca))
        
        # Aleatorizar tratamientos dentro de cada bloque
        np.random.seed(42)
        for j in range(n_bloques_dbca):
            trat_orden = np.random.permutation(num_trat_dbca)
            for i, trat in enumerate(trat_orden):
                rect = plt.Rectangle((i, j), 0.9, 0.9,
                                    facecolor=colores_dbca[trat],
                                    edgecolor='black',
                                    linewidth=2)
                ax_dbca.add_patch(rect)
                ax_dbca.text(i + 0.45, j + 0.45, f'T{trat+1}',
                           ha='center', va='center', fontsize=11, fontweight='bold')
            
            # Etiqueta de bloque
            ax_dbca.text(-0.5, j + 0.45, f'Bloque {j+1}',
                        ha='right', va='center', fontsize=10, fontweight='bold',
                        bbox=dict(boxstyle='round', facecolor='lightgray'))
        
        ax_dbca.set_xlim(-1, num_trat_dbca)
        ax_dbca.set_ylim(0, n_bloques_dbca)
        ax_dbca.set_aspect('equal')
        ax_dbca.set_xlabel('Posicion dentro del bloque', fontsize=12)
        ax_dbca.set_ylabel('Bloques', fontsize=12)
        ax_dbca.set_title('DBCA - Tratamientos aleatorizados dentro de cada bloque', 
                         fontsize=14, fontweight='bold')
        ax_dbca.set_xticks([])
        ax_dbca.set_yticks([])
        ax_dbca.grid(False)
        plt.close()
        st.pyplot(fig_dbca)
        
        st.download_button("📥 Descargar Resumen", exportar_excel(df_resumen_dbca), "diseno_dbca.xlsx", key="dl_dbca")
    
    # ==================== FACTORIAL ====================
    else:  # Factorial
        st.subheader("Diseno Factorial (AxB)")
        
        with st.expander("📖 Sobre el Diseno Factorial"):
            st.markdown("""
            **Caracteristicas:**
            - Estudia 2 o mas factores simultaneamente
            - Permite evaluar efectos principales E interaccion
            - Mas eficiente que experimentos separados
            
            **Modelo:** Yijk = μ + αi + βj + (αβ)ij + εijk
            
            **Ventajas:**
            - Detecta interacciones entre factores
            - Usa menos recursos que experimentos individuales
            - Conclusiones aplicables a rango mas amplio de condiciones
            
            **Ejemplo:** 
            - Factor A: 3 variedades
            - Factor B: 4 dosis de fertilizante
            - Total: 3 × 4 = 12 tratamientos
            
            **Interaccion:** El efecto de A depende del nivel de B (o viceversa)
            """)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Parametros del Experimento")
            
            st.markdown("**Factor A:**")
            niveles_a = st.number_input(
                "Numero de niveles Factor A",
                min_value=2,
                max_value=10,
                value=3,
                key="niv_a"
            )
            
            st.markdown("**Factor B:**")
            niveles_b = st.number_input(
                "Numero de niveles Factor B",
                min_value=2,
                max_value=10,
                value=4,
                key="niv_b"
            )
            
            num_trat_fact = niveles_a * niveles_b
            st.info(f"**Total de tratamientos:** {num_trat_fact} ({niveles_a} × {niveles_b})")
            
            metodo_fact = st.radio(
                "Metodo de entrada:",
                ["Por Δ (diferencia absoluta)", "Por d (tamano del efecto)"],
                key="metodo_fact"
            )
            
            if metodo_fact == "Por Δ (diferencia absoluta)":
                delta_fact = st.number_input(
                    "Diferencia minima a detectar (Δ)",
                    min_value=0.1,
                    value=10.0,
                    step=0.5,
                    key="delta_fact"
                )
                sigma_fact = st.number_input(
                    "Error experimental esperado (σ)",
                    min_value=0.1,
                    value=8.0,
                    step=0.5,
                    key="sigma_fact"
                )
                d_calc_fact = delta_fact / sigma_fact
                st.info(f"**d calculado = {d_calc_fact:.3f}**")
            else:
                d_calc_fact = st.slider(
                    "Tamano del efecto (d)",
                    min_value=0.1,
                    max_value=3.0,
                    value=1.25,
                    step=0.1,
                    key="d_fact"
                )
                sigma_fact = st.number_input(
                    "Error experimental (σ)",
                    min_value=0.1,
                    value=8.0,
                    step=0.5,
                    key="sigma_ref_fact"
                )
                delta_fact = d_calc_fact * sigma_fact
                st.info(f"**Δ equivalente = {delta_fact:.2f} unidades**")
            
            alpha_fact = st.select_slider(
                "Nivel de significancia (α)",
                options=[0.01, 0.05, 0.10],
                value=0.05,
                key="alpha_fact"
            )
            
            potencia_fact = st.select_slider(
                "Potencia deseada (1-β)",
                options=[0.70, 0.75, 0.80, 0.85, 0.90, 0.95],
                value=0.80,
                key="pot_fact"
            )
            
            arreglo_fact = st.radio(
                "Arreglo del diseno:",
                ["Completamente al Azar", "Bloques Completos al Azar"],
                key="arreglo_fact"
            )
        
        with col2:
            st.markdown("### Resultados")
            
            z_alpha_fact = norm.ppf(1 - alpha_fact / 2)
            z_beta_fact = norm.ppf(potencia_fact)
            
            # Ajuste para diseño factorial (mas conservador)
            n_base_fact = 2 * ((z_alpha_fact + z_beta_fact) / d_calc_fact) ** 2
            ajuste_factorial = 1 + 0.20 * np.log(num_trat_fact)  # Ajuste por numero de tratamientos
            n_rep_fact = int(np.ceil(n_base_fact * ajuste_factorial))
            n_rep_fact = max(n_rep_fact, 3)
            
            st.metric("Replicas por tratamiento (r)", n_rep_fact)
            st.metric("Combinaciones de tratamientos", num_trat_fact)
            st.metric("Unidades experimentales totales", num_trat_fact * n_rep_fact)
            
            # Grados de libertad
            gl_a = niveles_a - 1
            gl_b = niveles_b - 1
            gl_ab = gl_a * gl_b
            
            if arreglo_fact == "Completamente al Azar":
                gl_error_fact = num_trat_fact * (n_rep_fact - 1)
            else:  # DBCA
                gl_bloques_fact = n_rep_fact - 1
                gl_error_fact = (num_trat_fact - 1) * gl_bloques_fact
            
            st.markdown("**Grados de Libertad:**")
            df_gl_fact = pd.DataFrame({
                'Fuente': ['Factor A', 'Factor B', 'Interaccion A×B', 'Error'],
                'gl': [gl_a, gl_b, gl_ab, gl_error_fact]
            })
            st.dataframe(df_gl_fact, use_container_width=True)
            
            st.success(f"""
            **Interpretacion:**
            
            Con {n_rep_fact} replicas de cada una de las {num_trat_fact} 
            combinaciones, puedes detectar:
            
            - Efectos principales de A y B
            - Interaccion A×B
            - Con {potencia_fact*100:.0f}% de potencia
            
            **Total:** {num_trat_fact * n_rep_fact} unidades experimentales
            """)
            
            # Comparacion con experimentos separados
            st.markdown("### Ventaja vs Experimentos Separados")
            n_sep_a = int(np.ceil(n_base_fact))
            n_sep_b = int(np.ceil(n_base_fact))
            total_sep = (niveles_a * n_sep_a) + (niveles_b * n_sep_b)
            total_fact = num_trat_fact * n_rep_fact
            ahorro = total_sep - total_fact
            
            df_comp_fact = pd.DataFrame({
                'Estrategia': ['Experimentos separados', 'Factorial', 'Diferencia'],
                'Unidades necesarias': [total_sep, total_fact, ahorro],
                'Puede detectar interaccion': ['No', 'Si', '✓']
            })
            st.dataframe(df_comp_fact, use_container_width=True)
            
            if ahorro > 0:
                st.success(f"💰 Ahorro: {ahorro} unidades experimentales ({ahorro/total_sep*100:.1f}%)")
            
        # Tabla resumen
        st.markdown("### Tabla Resumen del Diseno")
        df_resumen_fact = pd.DataFrame([{
            'Diseno': f'Factorial {niveles_a}×{niveles_b}',
            'Arreglo': arreglo_fact,
            'Tratamientos': num_trat_fact,
            'Replicas (r)': n_rep_fact,
            'Total unidades': num_trat_fact * n_rep_fact,
            'Δ': f"{delta_fact:.2f}",
            'σ': f"{sigma_fact:.2f}",
            'd Cohen': f"{d_calc_fact:.3f}",
            'α': alpha_fact,
            'Potencia': f"{potencia_fact:.2%}",
            'gl error': gl_error_fact
        }])
        st.dataframe(df_resumen_fact, use_container_width=True)
        
        # Matriz del factorial
        st.markdown("### Matriz del Diseno Factorial")
        
        # Crear matriz visual
        fig_fact, ax_fact = plt.subplots(figsize=(max(8, niveles_b * 1.5), max(6, niveles_a * 1.2)))
        
        # Colores para cada combinacion
        colores_fact = plt.cm.viridis(np.linspace(0, 1, num_trat_fact))
        
        idx = 0
        for i in range(niveles_a):
            for j in range(niveles_b):
                rect = plt.Rectangle((j, niveles_a - 1 - i), 0.9, 0.9,
                                    facecolor=colores_fact[idx],
                                    edgecolor='black',
                                    linewidth=2)
                ax_fact.add_patch(rect)
                ax_fact.text(j + 0.45, niveles_a - 1 - i + 0.45, 
                           f'A{i+1}B{j+1}\n(n={n_rep_fact})',
                           ha='center', va='center', fontsize=10, fontweight='bold',
                           color='white')
                idx += 1
        
        # Etiquetas
        ax_fact.set_xlim(0, niveles_b)
        ax_fact.set_ylim(0, niveles_a)
        ax_fact.set_aspect('equal')
        ax_fact.set_xlabel('Factor B', fontsize=14, fontweight='bold')
        ax_fact.set_ylabel('Factor A', fontsize=14, fontweight='bold')
        ax_fact.set_title(f'Diseno Factorial {niveles_a}×{niveles_b} ({num_trat_fact} tratamientos, {n_rep_fact} replicas c/u)',
                         fontsize=14, fontweight='bold')
        
        ax_fact.set_xticks(np.arange(niveles_b) + 0.45)
        ax_fact.set_xticklabels([f'B{j+1}' for j in range(niveles_b)])
        ax_fact.set_yticks(np.arange(niveles_a) + 0.45)
        ax_fact.set_yticklabels([f'A{niveles_a-i}' for i in range(niveles_a)])
        ax_fact.grid(False)
        
        plt.close()
        st.pyplot(fig_fact)
        
        # Grafico de interaccion teorico
        st.markdown("### Patron de Interaccion (Ejemplo)")
        
        col_int1, col_int2 = st.columns(2)
        
        with col_int1:
            st.markdown("**Sin interaccion:**")
            fig_sin, ax_sin = plt.subplots(figsize=(6, 4))
            
            x_b = np.arange(niveles_b)
            for i in range(min(3, niveles_a)):
                y = 50 + i * 10 + x_b * 5
                ax_sin.plot(x_b, y, 'o-', linewidth=2, markersize=8, label=f'A{i+1}')
            
            ax_sin.set_xlabel('Niveles de Factor B')
            ax_sin.set_ylabel('Respuesta')
            ax_sin.set_title('Lineas paralelas → No hay interaccion')
            ax_sin.legend()
            ax_sin.grid(True, alpha=0.3)
            plt.close()
            st.pyplot(fig_sin)
        
        with col_int2:
            st.markdown("**Con interaccion:**")
            fig_con, ax_con = plt.subplots(figsize=(6, 4))
            
            for i in range(min(3, niveles_a)):
                if i == 0:
                    y = 50 + x_b * 8
                elif i == 1:
                    y = 60 + x_b * 2
                else:
                    y = 55 - x_b * 3
                ax_con.plot(x_b, y, 'o-', linewidth=2, markersize=8, label=f'A{i+1}')
            
            ax_con.set_xlabel('Niveles de Factor B')
            ax_con.set_ylabel('Respuesta')
            ax_con.set_title('Lineas no paralelas → Hay interaccion')
            ax_con.legend()
            ax_con.grid(True, alpha=0.3)
            plt.close()
            st.pyplot(fig_con)
        
        st.info("""
        **Interpretacion de la interaccion:**
        - **Sin interaccion:** El efecto de A es el mismo para todos los niveles de B
        - **Con interaccion:** El efecto de A depende del nivel de B (las lineas se cruzan)
        """)
        
        st.download_button("📥 Descargar Resumen", exportar_excel(df_resumen_fact), "diseno_factorial.xlsx", key="dl_fact")
    
    # Seccion comun: Recomendaciones
    st.markdown("---")
    st.markdown("### 💡 Recomendaciones Generales")
    
    col_rec1, col_rec2, col_rec3 = st.columns(3)
    
    with col_rec1:
        st.markdown("""
        **Tamano del efecto:**
        - d < 0.5: Pequeno (dificil detectar)
        - d = 0.5-0.8: Mediano (detectable)
        - d > 0.8: Grande (facil detectar)
        """)
    
    with col_rec2:
        st.markdown("""
        **Replicas minimas:**
        - DCA: minimo 3-4
        - DBCA: minimo 3-4 bloques
        - Factorial: minimo 3 por combinacion
        """)
    
    with col_rec3:
        st.markdown("""
        **Que diseno usar:**
        - Homogeneo → DCA
        - Heterogeneo → DBCA
        - 2+ factores → Factorial
        """)
    
    st.warning("""
    ⚠️ **Importante:** Estos calculos son aproximaciones basadas en teoria estadistica. 
    Factores como:
    - Datos no normales
    - Varianzas heterogeneas
    - Valores atipicos
    - Perdida de unidades experimentales
    
    Pueden requerir ajustes. Considere agregar 10-20% mas de replicas como margen de seguridad.
    """)

# ==================== FOOTER ====================import streamlit as st
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
import itertools

# Configuración
try:
    plt.style.use('seaborn-v0_8-whitegrid')
except:
    plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (10, 6)

# ==================== FUNCIONES ANOVA ====================

def calcular_anova_un_factor(grupos):
    """ANOVA de un factor"""
    k = len(grupos)  # número de grupos
    n_total = sum(len(g) for g in grupos)
    grand_mean = np.mean([x for grupo in grupos for x in grupo])
    
    # SST (Total)
    sst = sum((x - grand_mean)**2 for grupo in grupos for x in grupo)
    
    # SSB (Between - Entre grupos)
    ssb = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in grupos)
    
    # SSW (Within - Dentro de grupos)
    ssw = sum((x - np.mean(g))**2 for g in grupos for x in g)
    
    # Grados de libertad
    df_between = k - 1
    df_within = n_total - k
    df_total = n_total - 1
    
    # Cuadrados medios
    msb = ssb / df_between
    msw = ssw / df_within
    
    # Estadístico F
    f_stat = msb / msw
    p_value = 1 - f.cdf(f_stat, df_between, df_within)
    
    return {
        'F': f_stat,
        'p_value': p_value,
        'df_between': df_between,
        'df_within': df_within,
        'SSB': ssb,
        'SSW': ssw,
        'SST': sst,
        'MSB': msb,
        'MSW': msw
    }

def potencia_anova(medias, sigma, n_por_grupo, alpha=0.05):
    """Calcula potencia para ANOVA"""
    k = len(medias)
    grand_mean = np.mean(medias)
    phi = np.sqrt(n_por_grupo * sum((m - grand_mean)**2 for m in medias) / (k * sigma**2))
    df1 = k - 1
    df2 = k * (n_por_grupo - 1)
    f_crit = f.ppf(1 - alpha, df1, df2)
    
    # Aproximación de potencia
    lambda_nc = phi**2 * k
    potencia = 1 - f.cdf(f_crit, df1, df2, lambda_nc)
    
    return potencia, phi, df1, df2

# ==================== FUNCIONES CORRELACIÓN ====================

def calcular_correlacion(x, y, tipo='pearson'):
    """Calcula correlación y prueba de significancia"""
    n = len(x)
    
    if tipo == 'pearson':
        r, p_value = stats.pearsonr(x, y)
        nombre = "Pearson"
    else:  # spearman
        r, p_value = stats.spearmanr(x, y)
        nombre = "Spearman"
    
    # Intervalo de confianza para r usando transformación Fisher Z
    z = np.arctanh(r)
    se_z = 1 / np.sqrt(n - 3)
    z_crit = norm.ppf(0.975)
    
    ic_inf = np.tanh(z - z_crit * se_z)
    ic_sup = np.tanh(z + z_crit * se_z)
    
    # Estadístico t
    t_stat = r * np.sqrt(n - 2) / np.sqrt(1 - r**2)
    
    return {
        'r': r,
        'r2': r**2,
        'p_value': p_value,
        't_stat': t_stat,
        'n': n,
        'ic_inf': ic_inf,
        'ic_sup': ic_sup,
        'tipo': nombre
    }

# ==================== FUNCIONES REGRESIÓN ====================

def regresion_simple(x, y):
    """Regresión lineal simple"""
    n = len(x)
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    
    # Cálculo de pendiente y ordenada
    numerador = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    denominador = sum((x[i] - x_mean)**2 for i in range(n))
    b1 = numerador / denominador
    b0 = y_mean - b1 * x_mean
    
    # Predicciones y residuos
    y_pred = [b0 + b1 * xi for xi in x]
    residuos = [y[i] - y_pred[i] for i in range(n)]
    
    # Suma de cuadrados
    sst = sum((yi - y_mean)**2 for yi in y)
    ssr = sum((y_pred[i] - y_mean)**2 for i in range(n))
    sse = sum(r**2 for r in residuos)
    
    # R²
    r2 = ssr / sst
    r2_adj = 1 - (1 - r2) * (n - 1) / (n - 2)
    
    # Error estándar
    se = np.sqrt(sse / (n - 2))
    
    # Error estándar de b1
    se_b1 = se / np.sqrt(denominador)
    
    # Estadístico t para b1
    t_b1 = b1 / se_b1
    p_value_b1 = 2 * (1 - t.cdf(abs(t_b1), n - 2))
    
    # Estadístico F
    f_stat = ssr / (sse / (n - 2))
    p_value_f = 1 - f.cdf(f_stat, 1, n - 2)
    
    return {
        'b0': b0,
        'b1': b1,
        'r2': r2,
        'r2_adj': r2_adj,
        'se': se,
        't_b1': t_b1,
        'p_value_b1': p_value_b1,
        'f_stat': f_stat,
        'p_value_f': p_value_f,
        'y_pred': y_pred,
        'residuos': residuos
    }

# ==================== PRUEBAS NO PARAMÉTRICAS ====================

def mann_whitney_u(grupo1, grupo2):
    """Prueba U de Mann-Whitney"""
    stat, p_value = stats.mannwhitneyu(grupo1, grupo2, alternative='two-sided')
    n1, n2 = len(grupo1), len(grupo2)
    
    # Tamaño del efecto (r)
    z = norm.ppf(p_value/2)
    r = abs(z) / np.sqrt(n1 + n2)
    
    return {
        'U': stat,
        'p_value': p_value,
        'n1': n1,
        'n2': n2,
        'effect_size': r
    }

def kruskal_wallis(*grupos):
    """Prueba de Kruskal-Wallis"""
    stat, p_value = stats.kruskal(*grupos)
    k = len(grupos)
    n_total = sum(len(g) for g in grupos)
    
    # Eta cuadrado
    H = stat
    eta2 = (H - k + 1) / (n_total - k)
    
    return {
        'H': stat,
        'p_value': p_value,
        'k': k,
        'n_total': n_total,
        'eta2': eta2
    }

def wilcoxon_test(antes, despues):
    """Prueba de Wilcoxon para muestras pareadas"""
    stat, p_value = stats.wilcoxon(antes, despues)
    n = len(antes)
    
    # Tamaño del efecto
    z = norm.ppf(p_value/2)
    r = abs(z) / np.sqrt(n)
    
    return {
        'W': stat,
        'p_value': p_value,
        'n': n,
        'effect_size': r
    }

# ==================== CHI-CUADRADO ====================

def chi2_independencia(tabla):
    """Prueba Chi-cuadrado de independencia"""
    chi2_stat, p_value, dof, expected = stats.chi2_contingency(tabla)
    
    # Coeficientes de asociación
    n = np.sum(tabla)
    min_dim = min(tabla.shape[0], tabla.shape[1])
    
    # V de Cramer
    v_cramer = np.sqrt(chi2_stat / (n * (min_dim - 1)))
    
    return {
        'chi2': chi2_stat,
        'p_value': p_value,
        'dof': dof,
        'expected': expected,
        'v_cramer': v_cramer,
        'n': n
    }

# ==================== TAMAÑO DE MUESTRA ====================

def tamano_muestra_media(delta, sigma, alpha=0.05, beta=0.20, bilateral=True):
    """Calcula n necesario para prueba de media"""
    if bilateral:
        z_alpha = norm.ppf(1 - alpha/2)
    else:
        z_alpha = norm.ppf(1 - alpha)
    
    z_beta = norm.ppf(1 - beta)
    n = ((z_alpha + z_beta) * sigma / delta) ** 2
    
    return int(np.ceil(n))

def tamano_muestra_proporcion(p1, p2, alpha=0.05, beta=0.20, bilateral=True):
    """Calcula n necesario para prueba de proporción"""
    if bilateral:
        z_alpha = norm.ppf(1 - alpha/2)
    else:
        z_alpha = norm.ppf(1 - alpha)
    
    z_beta = norm.ppf(1 - beta)
    p_pooled = (p1 + p2) / 2
    
    n = (z_alpha * np.sqrt(2 * p_pooled * (1 - p_pooled)) + 
         z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p1 - p2) ** 2
    
    return int(np.ceil(n))

# ==================== EXPORTACIÓN ====================

def exportar_excel(dataframe):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Resultados')
    return output.getvalue()

def exportar_pdf(texto):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Analisis Estadistico Avanzado")
    c.setFont("Helvetica", 12)
    y_position = height - 100
    for line in texto.split('\n'):
        if y_position < 50:
            c.showPage()
            y_position = height - 50
        c.drawString(50, y_position, line)
        y_position -= 20
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# ==================== INTERFAZ ====================

st.set_page_config(page_title="Analisis Estadistico Avanzado", layout="wide", page_icon="📊")

with st.sidebar:
    st.title("📚 Estadistica Avanzada")
    st.markdown("""
    ### Contenido
    - **ANOVA:** Comparar 3+ grupos
    - **Correlacion:** Relacion entre variables
    - **Regresion:** Prediccion
    - **No Parametricas:** Sin supuestos de normalidad
    - **Chi-cuadrado:** Variables categoricas
    - **Tamano de muestra:** Planificacion
    
    ---
    
    ### Aplicacion Basica
    ¿Necesitas conceptos fundamentales?
    
    [📐 Ir a App Fundamentos](#)
    """)

st.title("🎓 Analisis Estadistico Avanzado")
st.markdown("Herramientas para analisis estadisticos complejos y diseno experimental.")

tabs = st.tabs([
    "📊 ANOVA",
    "🔗 Correlacion",
    "📈 Regresion",
    "📉 No Parametricas",
    "✖️ Chi-cuadrado",
    "🔢 Tamano de Muestra",
    "🌱 Diseno Experimental"
])

# ==================== TAB 1: ANOVA ====================
with tabs[0]:
    st.header("ANOVA - Analisis de Varianza")
    
    with st.expander("ℹ️ Informacion"):
        st.markdown("""
        **ANOVA de un factor** permite comparar las medias de 3 o mas grupos independientes.
        
        **Hipotesis:**
        - H₀: μ₁ = μ₂ = μ₃ = ... = μₖ (todas las medias son iguales)
        - H₁: Al menos una media es diferente
        
        **Supuestos:**
        - Independencia de observaciones
        - Normalidad en cada grupo
        - Homogeneidad de varianzas (Levene)
        
        **Ejemplo:** Comparar el rendimiento de 4 metodos de ensenanza diferentes.
        """)
    
    tipo_anova = st.radio("Selecciona el tipo de analisis:", 
                          ["Analisis de Potencia", "Analisis con Datos"])
    
    if tipo_anova == "Analisis de Potencia":
        st.subheader("Calculo de Potencia para ANOVA")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            num_grupos = st.slider("Numero de grupos (k)", 3, 10, 4)
            
            st.subheader("Prueba de Significancia")
            st.metric("t (β₁)", f"{resultado_reg['t_b1']:.4f}")
            st.metric("p-value (β₁)", f"{resultado_reg['p_value_b1']:.4f}")
            st.metric("F", f"{resultado_reg['f_stat']:.4f}")
            st.metric("p-value (modelo)", f"{resultado_reg['p_value_f']:.4f}")
            
            if resultado_reg['p_value_b1'] < 0.05:
                st.success("✅ β₁ significativo")
            else:
                st.warning("❌ β₁ no significativo")
        
        with col2:
            st.subheader("Ecuacion Estimada")
            st.latex(f"\\hat{{Y}} = {resultado_reg['b0']:.3f} + {resultado_reg['b1']:.3f}X")
            
            # Grafico de regresion
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            
            # Grafico 1: Datos y linea de regresion
            ax1.scatter(x_reg, y_reg, alpha=0.6, label='Datos observados')
            ax1.plot(x_reg, resultado_reg['y_pred'], 'r-', linewidth=2, label='Linea de regresion')
            ax1.set_xlabel('X')
            ax1.set_ylabel('Y')
            ax1.set_title(f'Regresion Lineal (R² = {resultado_reg["r2"]:.3f})')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Grafico 2: Residuos
            ax2.scatter(resultado_reg['y_pred'], resultado_reg['residuos'], alpha=0.6)
            ax2.axhline(y=0, color='r', linestyle='--')
            ax2.set_xlabel('Valores ajustados')
            ax2.set_ylabel('Residuos')
            ax2.set_title('Grafico de Residuos')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.close()
            st.pyplot(fig)
        
        df_reg = pd.DataFrame([{
            'n': n_reg,
            'β₀': round(resultado_reg['b0'], 4),
            'β₁': round(resultado_reg['b1'], 4),
            'R²': round(resultado_reg['r2'], 4),
            'R² adj': round(resultado_reg['r2_adj'], 4),
            'SE': round(resultado_reg['se'], 4),
            'F': round(resultado_reg['f_stat'], 4),
            'p-value': round(resultado_reg['p_value_f'], 4)
        }])
        st.dataframe(df_reg, use_container_width=True)
        st.download_button("📥 Excel", exportar_excel(df_reg), "regresion.xlsx", key="dl_reg")

# ==================== TAB 4: NO PARAMÉTRICAS ====================
with tabs[3]:
    st.header("Pruebas No Parametricas")
    
    with st.expander("ℹ️ Informacion"):
        st.markdown("""
        Las pruebas no parametricas no requieren supuestos de normalidad.
        
        **Mann-Whitney U:** Alternativa no parametrica a t-test para 2 grupos independientes
        
        **Kruskal-Wallis:** Alternativa no parametrica a ANOVA para 3+ grupos
        
        **Wilcoxon:** Alternativa no parametrica a t-test pareado
        
        **Cuando usarlas:**
        - Datos ordinales
        - Distribuciones no normales
        - Muestras pequeñas
        - Presencia de outliers
        """)
    
    tipo_no_param = st.selectbox(
        "Selecciona la prueba:",
        ["Mann-Whitney U", "Kruskal-Wallis", "Wilcoxon"]
    )
    
    if tipo_no_param == "Mann-Whitney U":
        st.subheader("Prueba U de Mann-Whitney (2 grupos independientes)")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            datos_g1_str = st.text_input(
                "Grupo 1 (separados por comas):",
                "23, 25, 27, 29, 31, 33, 35, 37",
                key="mw_g1"
            )
            datos_g2_str = st.text_input(
                "Grupo 2 (separados por comas):",
                "18, 20, 22, 24, 26, 28, 30",
                key="mw_g2"
            )
        
        if st.button("Calcular Mann-Whitney", key="calc_mw"):
            try:
                g1 = [float(x.strip()) for x in datos_g1_str.split(',')]
                g2 = [float(x.strip()) for x in datos_g2_str.split(',')]
                
                resultado_mw = mann_whitney_u(g1, g2)
                
                with col2:
                    st.metric("Estadistico U", f"{resultado_mw['U']:.0f}")
                    st.metric("p-value", f"{resultado_mw['p_value']:.4f}")
                    st.metric("Tamano efecto (r)", f"{resultado_mw['effect_size']:.3f}")
                    
                    if resultado_mw['p_value'] < 0.05:
                        st.success("✅ Diferencia significativa")
                    else:
                        st.info("❌ No hay diferencia significativa")
                
                # Grafico
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.boxplot([g1, g2], labels=['Grupo 1', 'Grupo 2'])
                ax.set_ylabel('Valores')
                ax.set_title('Comparacion de Grupos (Mann-Whitney)')
                ax.grid(True, alpha=0.3)
                plt.close()
                st.pyplot(fig)
                
                df_mw = pd.DataFrame([{
                    'n₁': resultado_mw['n1'],
                    'n₂': resultado_mw['n2'],
                    'U': resultado_mw['U'],
                    'p-value': round(resultado_mw['p_value'], 4),
                    'r': round(resultado_mw['effect_size'], 3)
                }])
                st.dataframe(df_mw, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    elif tipo_no_param == "Kruskal-Wallis":
        st.subheader("Prueba de Kruskal-Wallis (3+ grupos independientes)")
        
        num_grupos_kw = st.slider("Numero de grupos", 3, 6, 3, key="n_kw")
        
        grupos_kw = []
        for i in range(num_grupos_kw):
            datos_str = st.text_input(
                f"Grupo {i+1} (separados por comas):",
                ", ".join(map(str, np.random.normal(100 + i*10, 10, 8).round(1))),
                key=f"kw_g{i}"
            )
            try:
                datos = [float(x.strip()) for x in datos_str.split(',')]
                grupos_kw.append(datos)
            except:
                grupos_kw.append([])
        
        if st.button("Calcular Kruskal-Wallis", key="calc_kw"):
            if all(len(g) > 0 for g in grupos_kw):
                resultado_kw = kruskal_wallis(*grupos_kw)
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.metric("Estadistico H", f"{resultado_kw['H']:.4f}")
                    st.metric("p-value", f"{resultado_kw['p_value']:.4f}")
                    st.metric("Eta² (tamano efecto)", f"{resultado_kw['eta2']:.3f}")
                    
                    if resultado_kw['p_value'] < 0.05:
                        st.success("✅ Diferencias significativas entre grupos")
                    else:
                        st.info("❌ No hay diferencias significativas")
                
                with col2:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.boxplot(grupos_kw, labels=[f"Grupo {i+1}" for i in range(num_grupos_kw)])
                    ax.set_ylabel('Valores')
                    ax.set_title('Comparacion de Grupos (Kruskal-Wallis)')
                    ax.grid(True, alpha=0.3)
                    plt.close()
                    st.pyplot(fig)
                
                df_kw = pd.DataFrame([{
                    'k grupos': resultado_kw['k'],
                    'n total': resultado_kw['n_total'],
                    'H': round(resultado_kw['H'], 4),
                    'p-value': round(resultado_kw['p_value'], 4),
                    'η²': round(resultado_kw['eta2'], 3)
                }])
                st.dataframe(df_kw, use_container_width=True)
            else:
                st.error("Ingresa datos validos en todos los grupos")
    
    else:  # Wilcoxon
        st.subheader("Prueba de Wilcoxon (muestras pareadas)")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            antes_str = st.text_input(
                "Mediciones ANTES (separadas por comas):",
                "65, 68, 70, 72, 75, 78, 80, 82",
                key="wilc_antes"
            )
            despues_str = st.text_input(
                "Mediciones DESPUES (separadas por comas):",
                "70, 72, 75, 78, 80, 83, 85, 88",
                key="wilc_despues"
            )
        
        if st.button("Calcular Wilcoxon", key="calc_wilc"):
            try:
                antes = [float(x.strip()) for x in antes_str.split(',')]
                despues = [float(x.strip()) for x in despues_str.split(',')]
                
                if len(antes) == len(despues):
                    resultado_wilc = wilcoxon_test(antes, despues)
                    
                    with col2:
                        st.metric("Estadistico W", f"{resultado_wilc['W']:.0f}")
                        st.metric("p-value", f"{resultado_wilc['p_value']:.4f}")
                        st.metric("Tamano efecto (r)", f"{resultado_wilc['effect_size']:.3f}")
                        
                        if resultado_wilc['p_value'] < 0.05:
                            st.success("✅ Cambio significativo")
                        else:
                            st.info("❌ No hay cambio significativo")
                    
                    # Grafico
                    fig, ax = plt.subplots(figsize=(10, 6))
                    x_pos = np.arange(len(antes))
                    ax.plot(x_pos, antes, 'o-', label='Antes', linewidth=2)
                    ax.plot(x_pos, despues, 's-', label='Despues', linewidth=2)
                    for i in range(len(antes)):
                        ax.plot([i, i], [antes[i], despues[i]], 'k--', alpha=0.3)
                    ax.set_xlabel('Sujeto')
                    ax.set_ylabel('Valor')
                    ax.set_title('Comparacion Antes-Despues (Wilcoxon)')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    plt.close()
                    st.pyplot(fig)
                    
                    df_wilc = pd.DataFrame([{
                        'n': resultado_wilc['n'],
                        'W': resultado_wilc['W'],
                        'p-value': round(resultado_wilc['p_value'], 4),
                        'r': round(resultado_wilc['effect_size'], 3)
                    }])
                    st.dataframe(df_wilc, use_container_width=True)
                else:
                    st.error("Antes y Despues deben tener la misma cantidad de datos")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ==================== TAB 5: CHI-CUADRADO ====================
with tabs[4]:
    st.header("Prueba Chi-cuadrado")
    
    with st.expander("ℹ️ Informacion"):
        st.markdown("""
        **Prueba de Independencia:** Evalua si dos variables categoricas estan asociadas.
        
        **Ejemplo:** ¿El genero esta asociado con la preferencia de producto?
        
        **V de Cramer:** Medida del tamano del efecto (0-1)
        - 0.00-0.10: Efecto trivial
        - 0.10-0.30: Efecto pequeño
        - 0.30-0.50: Efecto moderado
        - 0.50+: Efecto grande
        
        **Supuestos:**
        - Frecuencias esperadas ≥ 5 en al menos 80% de las celdas
        - Observaciones independientes
        """)
    
    st.subheader("Tabla de Contingencia")
    st.info("Ingresa las frecuencias observadas para cada combinacion")
    
    num_filas = st.slider("Numero de filas (Variable 1)", 2, 5, 2, key="chi_filas")
    num_cols = st.slider("Numero de columnas (Variable 2)", 2, 5, 2, key="chi_cols")
    
    # Crear tabla de entrada
    st.markdown("**Frecuencias observadas:**")
    
    tabla_chi = []
    cols_input = st.columns(num_cols)
    
    for i in range(num_filas):
        fila = []
        st.markdown(f"**Fila {i+1}:**")
        cols_fila = st.columns(num_cols)
        for j in range(num_cols):
            with cols_fila[j]:
                valor = st.number_input(
                    f"Col {j+1}",
                    min_value=0,
                    value=np.random.randint(10, 50),
                    key=f"chi_{i}_{j}"
                )
                fila.append(valor)
        tabla_chi.append(fila)
    
    if st.button("Calcular Chi-cuadrado", key="calc_chi"):
        tabla_array = np.array(tabla_chi)
        resultado_chi = chi2_independencia(tabla_array)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Resultados")
            st.metric("Chi-cuadrado (χ²)", f"{resultado_chi['chi2']:.4f}")
            st.metric("p-value", f"{resultado_chi['p_value']:.4f}")
            st.metric("Grados de libertad", f"{resultado_chi['dof']}")
            st.metric("V de Cramer", f"{resultado_chi['v_cramer']:.3f}")
            st.metric("n total", f"{resultado_chi['n']}")
            
            if resultado_chi['p_value'] < 0.05:
                st.success("✅ Variables asociadas (dependientes)")
            else:
                st.info("❌ Variables independientes")
            
            # Interpretacion V de Cramer
            v = resultado_chi['v_cramer']
            if v < 0.10:
                interpretacion = "Efecto trivial"
            elif v < 0.30:
                interpretacion = "Efecto pequeño"
            elif v < 0.50:
                interpretacion = "Efecto moderado"
            else:
                interpretacion = "Efecto grande"
            
            st.info(f"**Tamano del efecto:** {interpretacion}")
        
        with col2:
            st.subheader("Frecuencias Esperadas")
            df_esperadas = pd.DataFrame(
                resultado_chi['expected'],
                columns=[f"Col {j+1}" for j in range(num_cols)],
                index=[f"Fila {i+1}" for i in range(num_filas)]
            )
            st.dataframe(df_esperadas.round(2), use_container_width=True)
            
            # Verificar supuestos
            esperadas_flat = resultado_chi['expected'].flatten()
            prop_menor_5 = np.sum(esperadas_flat < 5) / len(esperadas_flat)
            
            if prop_menor_5 > 0.20:
                st.warning(f"⚠️ {prop_menor_5*100:.1f}% de celdas con frecuencia esperada < 5")
                st.write("Considere combinar categorias o aumentar muestra")
            else:
                st.success("✅ Supuestos cumplidos")
        
        # Visualizacion
        st.subheader("Visualizacion")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Mapa de calor - Observadas
        im1 = ax1.imshow(tabla_array, cmap='Blues', aspect='auto')
        ax1.set_title('Frecuencias Observadas')
        ax1.set_xlabel('Variable 2')
        ax1.set_ylabel('Variable 1')
        plt.colorbar(im1, ax=ax1)
        
        # Mapa de calor - Esperadas
        im2 = ax2.imshow(resultado_chi['expected'], cmap='Oranges', aspect='auto')
        ax2.set_title('Frecuencias Esperadas')
        ax2.set_xlabel('Variable 2')
        ax2.set_ylabel('Variable 1')
        plt.colorbar(im2, ax=ax2)
        
        plt.tight_layout()
        plt.close()
        st.pyplot(fig)
        
        df_chi_result = pd.DataFrame([{
            'χ²': round(resultado_chi['chi2'], 4),
            'df': resultado_chi['dof'],
            'p-value': round(resultado_chi['p_value'], 4),
            'V Cramer': round(resultado_chi['v_cramer'], 3),
            'n': resultado_chi['n']
        }])
        st.dataframe(df_chi_result, use_container_width=True)
        st.download_button("📥 Excel", exportar_excel(df_chi_result), "chi_cuadrado.xlsx", key="dl_chi")

# ==================== TAB 6: TAMAÑO DE MUESTRA ====================
with tabs[5]:
    st.header("Calculadora de Tamano de Muestra")
    
    with st.expander("ℹ️ Informacion"):
        st.markdown("""
        Calcula el tamaño de muestra necesario para detectar un efecto dado con cierta potencia.
        
        **Parametros:**
        - **α (alfa):** Probabilidad de Error Tipo I (usualmente 0.05)
        - **β (beta):** Probabilidad de Error Tipo II (usualmente 0.20)
        - **Potencia:** 1 - β (usualmente 0.80 o 80%)
        - **Tamaño del efecto:** Diferencia que queremos detectar
        
        **Tipos de prueba:**
        - **Media:** Diferencia en unidades de la variable
        - **Proporcion:** Diferencia en porcentaje
        """)
    
    tipo_calc = st.selectbox(
        "Tipo de prueba:",
        ["Diferencia de Medias", "Diferencia de Proporciones"]
    )
    
    col1, col2 = st.columns([1, 1])
    
    if tipo_calc == "Diferencia de Medias":
        with col1:
            st.subheader("Parametros")
            delta_media = st.number_input(
                "Diferencia a detectar (δ = |μ₁ - μ₂|)",
                min_value=0.1,
                value=5.0,
                step=0.1,
                help="Diferencia minima importante"
            )
            sigma_calc = st.number_input(
                "Desviacion estandar (σ)",
                min_value=0.1,
                value=10.0,
                step=0.1
            )
            alpha_calc = st.select_slider(
                "Nivel de significancia (α)",
                options=[0.01, 0.05, 0.10],
                value=0.05
            )
            beta_calc = st.select_slider(
                "Error Tipo II (β)",
                options=[0.05, 0.10, 0.20],
                value=0.20
            )
            bilateral_calc = st.checkbox("Prueba bilateral", value=True)
        
        potencia_calc = 1 - beta_calc
        n_necesario = tamano_muestra_media(delta_media, sigma_calc, alpha_calc, beta_calc, bilateral_calc)
        
        with col2:
            st.subheader("Resultados")
            st.metric("n por grupo requerido", f"{n_necesario}")
            st.metric("n total (2 grupos)", f"{2 * n_necesario}")
            st.metric("Potencia objetivo", f"{potencia_calc:.2%}")
            
            # Tamaño del efecto (d de Cohen)
            d_cohen = delta_media / sigma_calc
            st.metric("Tamano del efecto (d)", f"{d_cohen:.3f}")
            
            if d_cohen < 0.2:
                efecto = "Muy pequeño"
                color = "🟡"
            elif d_cohen < 0.5:
                efecto = "Pequeño"
                color = "🟢"
            elif d_cohen < 0.8:
                efecto = "Mediano"
                color = "🔵"
            else:
                efecto = "Grande"
                color = "🟣"
            
            st.info(f"{color} **Efecto:** {efecto}")
            
            st.success(f"""
            **Interpretacion:**
            
            Necesitas **{n_necesario} participantes por grupo** 
            (total: {2*n_necesario}) para detectar una diferencia 
            de {delta_media} unidades con {potencia_calc:.0%} de 
            potencia y α={alpha_calc}.
            """)
        
        # Grafico de sensibilidad
        st.subheader("Analisis de Sensibilidad")
        
        potencias_analisis = [0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
        ns_por_potencia = []
        
        for pot in potencias_analisis:
            beta_temp = 1 - pot
            n_temp = tamano_muestra_media(delta_media, sigma_calc, alpha_calc, beta_temp, bilateral_calc)
            ns_por_potencia.append(n_temp)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(potencias_analisis, ns_por_potencia, 'o-', linewidth=2, markersize=8)
        ax.axhline(y=n_necesario, color='r', linestyle='--', label=f'n actual ({n_necesario})')
        ax.axvline(x=potencia_calc, color='g', linestyle='--', label=f'Potencia objetivo ({potencia_calc:.2%})')
        ax.set_xlabel('Potencia', fontsize=12)
        ax.set_ylabel('n por grupo', fontsize=12)
        ax.set_title('Tamano de Muestra vs. Potencia', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.close()
        st.pyplot(fig)
        
        df_calc = pd.DataFrame([{
            'δ': delta_media,
            'σ': sigma_calc,
            'd (Cohen)': round(d_cohen, 3),
            'α': alpha_calc,
            'Potencia': potencia_calc,
            'n por grupo': n_necesario,
            'n total': 2 * n_necesario
        }])
        st.dataframe(df_calc, use_container_width=True)
        st.download_button("📥 Excel", exportar_excel(df_calc), "tamano_muestra.xlsx", key="dl_calc")
    
    else:  # Diferencia de Proporciones
        with col1:
            st.subheader("Parametros")
            p1_calc = st.slider(
                "Proporcion grupo 1 (p₁)",
                0.0, 1.0, 0.5, 0.01,
                help="Proporcion esperada en grupo 1"
            )
            p2_calc = st.slider(
                "Proporcion grupo 2 (p₂)",
                0.0, 1.0, 0.6, 0.01,
                help="Proporcion esperada en grupo 2"
            )
            alpha_calc_prop = st.select_slider(
                "Nivel de significancia (α)",
                options=[0.01, 0.05, 0.10],
                value=0.05,
                key="alpha_prop_calc"
            )
            beta_calc_prop = st.select_slider(
                "Error Tipo II (β)",
                options=[0.05, 0.10, 0.20],
                value=0.20,
                key="beta_prop_calc"
            )
            bilateral_calc_prop = st.checkbox("Prueba bilateral", value=True, key="bilat_prop_calc")
        
        potencia_calc_prop = 1 - beta_calc_prop
        n_necesario_prop = tamano_muestra_proporcion(
            p1_calc, p2_calc, alpha_calc_prop, beta_calc_prop, bilateral_calc_prop
        )
        
        with col2:
            st.subheader("Resultados")
            st.metric("n por grupo requerido", f"{n_necesario_prop}")
            st.metric("n total (2 grupos)", f"{2 * n_necesario_prop}")
            st.metric("Potencia objetivo", f"{potencia_calc_prop:.2%}")
            
            # h de Cohen
            h_cohen = 2 * (np.arcsin(np.sqrt(p1_calc)) - np.arcsin(np.sqrt(p2_calc)))
            st.metric("Tamano del efecto (h)", f"{abs(h_cohen):.3f}")
            st.metric("Diferencia (%)", f"{abs(p1_calc - p2_calc)*100:.1f}%")
            
            st.success(f"""
            **Interpretacion:**
            
            Necesitas **{n_necesario_prop} participantes por grupo** 
            (total: {2*n_necesario_prop}) para detectar una diferencia 
            de {abs(p1_calc - p2_calc)*100:.1f}% con {potencia_calc_prop:.0%} 
            de potencia y α={alpha_calc_prop}.
            """)
        
        df_calc_prop = pd.DataFrame([{
            'p₁': p1_calc,
            'p₂': p2_calc,
            'Diferencia': f"{abs(p1_calc - p2_calc)*100:.1f}%",
            'h (Cohen)': round(abs(h_cohen), 3),
            'α': alpha_calc_prop,
            'Potencia': potencia_calc_prop,
            'n por grupo': n_necesario_prop,
            'n total': 2 * n_necesario_prop
        }])
        st.dataframe(df_calc_prop, use_container_width=True)
        st.download_button("📥 Excel", exportar_excel(df_calc_prop), "tamano_muestra_prop.xlsx", key="dl_calc_prop")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>📊 Analisis Estadistico Avanzado | Streamlit</p>
    <p><small>Herramienta desarrollada para cursos avanzados de estadistica</small></p>
    <p><small>Version 1.0 - 2025</small></p>
</div>
""", unsafe_allow_html=True)markdown("**Medias de cada grupo:**")
            medias = []
            cols_medias = st.columns(min(num_grupos, 4))
            for i in range(num_grupos):
                with cols_medias[i % 4]:
                    media = st.number_input(f"μ{i+1}", value=100.0 + i*5, key=f"media_{i}")
                    medias.append(media)
            
            sigma_anova = st.slider("Desviacion estandar comun (σ)", 1.0, 50.0, 10.0, 0.1)
            n_anova = st.slider("Tamano de muestra por grupo (n)", 5, 100, 20, 1)
            alpha_anova = st.select_slider("Nivel de significancia (α)", [0.01, 0.05, 0.10], value=0.05)
        
        with col2:
            st.subheader("Resultados")
            potencia, phi, df1, df2 = potencia_anova(medias, sigma_anova, n_anova, alpha_anova)
            
            st.metric("Potencia (1-β)", f"{potencia:.4f}")
            st.metric("Phi (φ)", f"{phi:.3f}")
            st.info(f"""
            **Grados de libertad:**
            - Entre grupos: {df1}
            - Dentro grupos: {df2}
            
            **n total:** {num_grupos * n_anova}
            """)
            
            if potencia >= 0.80:
                st.success("✅ Potencia adecuada")
            else:
                st.warning("⚠️ Aumentar n por grupo")
        
        # Visualizacion
        st.subheader("Visualizacion de las Medias")
        fig, ax = plt.subplots(figsize=(10, 6))
        grupos_nombres = [f"Grupo {i+1}" for i in range(num_grupos)]
        ax.bar(grupos_nombres, medias, color='steelblue', alpha=0.7)
        ax.axhline(y=np.mean(medias), color='red', linestyle='--', label='Media general')
        ax.set_ylabel('Media')
        ax.set_title('Comparacion de Medias por Grupo')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.close()
        st.pyplot(fig)
        
        df_anova_pot = pd.DataFrame([{
            'k grupos': num_grupos,
            'n por grupo': n_anova,
            'n total': num_grupos * n_anova,
            'σ': sigma_anova,
            'α': alpha_anova,
            'Potencia': round(potencia, 4),
            'φ': round(phi, 3)
        }])
        st.dataframe(df_anova_pot, use_container_width=True)
        st.download_button("📥 Excel", exportar_excel(df_anova_pot), "anova_potencia.xlsx", key="dl_anova_pot")
    
    else:  # Analisis con datos
        st.subheader("ANOVA con tus Datos")
        st.info("Ingresa los datos de cada grupo separados por comas")
        
        num_grupos_datos = st.slider("Numero de grupos", 3, 6, 3, key="ng_datos")
        
        grupos_data = []
        for i in range(num_grupos_datos):
            datos_str = st.text_input(
                f"Datos Grupo {i+1} (separados por comas)",
                value=", ".join(map(str, np.random.normal(100 + i*5, 10, 10).round(1))),
                key=f"datos_grupo_{i}"
            )
            try:
                datos = [float(x.strip()) for x in datos_str.split(',')]
                grupos_data.append(datos)
            except:
                st.error(f"Error en formato de Grupo {i+1}")
                grupos_data.append([])
        
        if st.button("Calcular ANOVA", key="calc_anova"):
            if all(len(g) > 0 for g in grupos_data):
                resultado = calcular_anova_un_factor(grupos_data)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Tabla ANOVA")
                    tabla_anova = pd.DataFrame({
                        'Fuente': ['Entre grupos', 'Dentro grupos', 'Total'],
                        'SS': [resultado['SSB'], resultado['SSW'], resultado['SST']],
                        'df': [resultado['df_between'], resultado['df_within'], 
                               resultado['df_between'] + resultado['df_within']],
                        'MS': [resultado['MSB'], resultado['MSW'], ''],
                        'F': [f"{resultado['F']:.4f}", '', ''],
                        'p-value': [f"{resultado['p_value']:.4f}", '', '']
                    })
                    st.dataframe(tabla_anova, use_container_width=True)
                
                with col2:
                    st.subheader("Interpretacion")
                    if resultado['p_value'] < 0.05:
                        st.success(f"✅ Rechazamos H₀ (p = {resultado['p_value']:.4f})")
                        st.write("Al menos una media es significativamente diferente.")
                    else:
                        st.info(f"❌ No rechazamos H₀ (p = {resultado['p_value']:.4f})")
                        st.write("No hay evidencia de diferencias entre las medias.")
                    
                    st.metric("Estadistico F", f"{resultado['F']:.4f}")
                    st.metric("p-value", f"{resultado['p_value']:.4f}")
                
                # Grafico de cajas
                st.subheader("Diagrama de Cajas")
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.boxplot(grupos_data, labels=[f"Grupo {i+1}" for i in range(len(grupos_data))])
                ax.set_ylabel('Valores')
                ax.set_title('Comparacion de Distribuciones')
                ax.grid(True, alpha=0.3)
                plt.close()
                st.pyplot(fig)
            else:
                st.error("Por favor, ingresa datos validos en todos los grupos")

# ==================== TAB 2: CORRELACIÓN ====================
with tabs[1]:
    st.header("Analisis de Correlacion")
    
    with st.expander("ℹ️ Informacion"):
        st.markdown("""
        **Correlacion de Pearson (r):**
        - Mide relacion lineal entre variables continuas
        - Requiere normalidad bivariada
        - Rango: -1 a +1
        
        **Correlacion de Spearman (ρ):**
        - No parametrica (usa rangos)
        - No requiere normalidad
        - Detecta relaciones monotonas
        
        **Interpretacion de |r|:**
        - 0.00-0.19: Muy debil
        - 0.20-0.39: Debil
        - 0.40-0.59: Moderada
        - 0.60-0.79: Fuerte
        - 0.80-1.00: Muy fuerte
        """)
    
    metodo_input = st.radio("Metodo de entrada:", ["Generar datos", "Ingresar datos manualmente"])
    
    if metodo_input == "Generar datos":
        col1, col2 = st.columns([1, 1])
        
        with col1:
            n_corr = st.slider("Numero de pares de datos (n)", 10, 200, 50)
            r_real = st.slider("Correlacion real a simular", -1.0, 1.0, 0.7, 0.05)
            tipo_corr = st.selectbox("Tipo de correlacion", ["pearson", "spearman"])
        
        # Generar datos correlacionados
        mean = [0, 0]
        cov = [[1, r_real], [r_real, 1]]
        x_corr, y_corr = np.random.multivariate_normal(mean, cov, n_corr).T
        
        with col2:
            resultado_corr = calcular_correlacion(x_corr, y_corr, tipo_corr)
            
            st.metric(f"Correlacion {resultado_corr['tipo']}", f"{resultado_corr['r']:.4f}")
            st.metric("R² (varianza explicada)", f"{resultado_corr['r2']:.4f}")
            st.metric("p-value", f"{resultado_corr['p_value']:.4f}")
            
            st.info(f"""
            **IC 95%:** [{resultado_corr['ic_inf']:.3f}, {resultado_corr['ic_sup']:.3f}]
            
            **Estadistico t:** {resultado_corr['t_stat']:.3f}
            """)
            
            if resultado_corr['p_value'] < 0.05:
                st.success("✅ Correlacion significativa")
            else:
                st.warning("❌ Correlacion no significativa")
        
        # Grafico de dispersion
        st.subheader("Grafico de Dispersion")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(x_corr, y_corr, alpha=0.6)
        
        # Linea de tendencia
        z = np.polyfit(x_corr, y_corr, 1)
        p = np.poly1d(z)
        ax.plot(x_corr, p(x_corr), "r--", linewidth=2, label=f'r = {resultado_corr["r"]:.3f}')
        
        ax.set_xlabel('Variable X')
        ax.set_ylabel('Variable Y')
        ax.set_title(f'Correlacion {resultado_corr["tipo"]}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.close()
        st.pyplot(fig)
        
        df_corr = pd.DataFrame([{
            'n': n_corr,
            'Tipo': resultado_corr['tipo'],
            'r': round(resultado_corr['r'], 4),
            'R²': round(resultado_corr['r2'], 4),
            'p-value': round(resultado_corr['p_value'], 4),
            't': round(resultado_corr['t_stat'], 3)
        }])
        st.dataframe(df_corr, use_container_width=True)
        st.download_button("📥 Excel", exportar_excel(df_corr), "correlacion.xlsx", key="dl_corr")
    
    else:
        st.info("Ingresa los datos separados por comas")
        x_str = st.text_input("Variable X:", "1, 2, 3, 4, 5, 6, 7, 8, 9, 10")
        y_str = st.text_input("Variable Y:", "2.1, 3.9, 6.2, 7.8, 10.1, 12.3, 13.9, 16.2, 17.8, 20.1")
        tipo_corr_manual = st.selectbox("Tipo", ["pearson", "spearman"], key="tipo_manual")
        
        if st.button("Calcular Correlacion"):
            try:
                x_manual = [float(v.strip()) for v in x_str.split(',')]
                y_manual = [float(v.strip()) for v in y_str.split(',')]
                
                if len(x_manual) == len(y_manual):
                    resultado = calcular_correlacion(x_manual, y_manual, tipo_corr_manual)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(f"Correlacion {resultado['tipo']}", f"{resultado['r']:.4f}")
                        st.metric("R²", f"{resultado['r2']:.4f}")
                        st.metric("p-value", f"{resultado['p_value']:.4f}")
                    
                    with col2:
                        fig, ax = plt.subplots()
                        ax.scatter(x_manual, y_manual)
                        z = np.polyfit(x_manual, y_manual, 1)
                        p = np.poly1d(z)
                        ax.plot(x_manual, p(x_manual), "r--")
                        ax.set_xlabel('X')
                        ax.set_ylabel('Y')
                        ax.grid(True, alpha=0.3)
                        plt.close()
                        st.pyplot(fig)
                else:
                    st.error("X e Y deben tener la misma cantidad de datos")
            except:
                st.error("Error en el formato de los datos")

# ==================== TAB 3: REGRESIÓN ====================
with tabs[2]:
    st.header("Regresion Lineal Simple")
    
    with st.expander("ℹ️ Informacion"):
        st.markdown("""
        **Regresion Lineal Simple:** Y = β₀ + β₁X + ε
        
        - **β₀:** Ordenada al origen (intercepto)
        - **β₁:** Pendiente (efecto de X sobre Y)
        - **R²:** Proporcion de varianza explicada (0-1)
        - **R² ajustado:** R² penalizado por numero de predictores
        
        **Supuestos:**
        - Linealidad
        - Independencia de residuos
        - Homoscedasticidad (varianza constante)
        - Normalidad de residuos
        """)
    
    n_reg = st.slider("Numero de observaciones", 10, 200, 50, key="n_reg")
    beta0_real = st.slider("Intercepto real (β₀)", -50.0, 50.0, 10.0, 0.1)
    beta1_real = st.slider("Pendiente real (β₁)", -5.0, 5.0, 2.0, 0.1)
    ruido = st.slider("Nivel de ruido (σ)", 0.1, 20.0, 5.0, 0.1)
    
    # Generar datos
    x_reg = np.linspace(0, 10, n_reg)
    y_reg = beta0_real + beta1_real * x_reg + np.random.normal(0, ruido, n_reg)
    
    if st.button("Calcular Regresion", key="calc_reg"):
        resultado_reg = regresion_simple(x_reg, y_reg)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Coeficientes")
            st.metric("Intercepto (β₀)", f"{resultado_reg['b0']:.4f}")
            st.metric("Pendiente (β₁)", f"{resultado_reg['b1']:.4f}")
            
            st.subheader("Bondad de Ajuste")
            st.metric("R²", f"{resultado_reg['r2']:.4f}")
            st.metric("R² ajustado", f"{resultado_reg['r2_adj']:.4f}")
            st.metric("Error estandar", f"{resultado_reg['se']:.4f}")
            
            st.

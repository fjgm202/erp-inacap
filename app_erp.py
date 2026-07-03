import streamlit as st
import pandas as pd
import datetime
import random

# --- CONFIGURACIÓN E INTERFAZ MÓVIL ---
st.set_page_config(page_title="SGO Flota Maquehue", page_icon="🚛", layout="centered")

# --- BASE DE DATOS CENTRALIZADA EN LA NUBE (SESSION STATE) ---
if 'conectado' not in st.session_state:
    st.session_state.conectado = False
    st.session_state.usuario = ""

if 'flota' not in st.session_state:
    flota_inicial = []
    lat_base = -38.7396
    lon_base = -72.6019
    
    for i in range(1, 11):
        kms_actuales = random.randint(500000, 580000)
        proxima_maint = ((kms_actuales // 10000) + 1) * 10000
        kms_restantes = proxima_maint - kms_actuales
        
        flota_inicial.append({
            "id": f"Camión {i}",
            "patente": f"GP-GC-{89+i}",
            "modelo": "Mercedes-Benz Actros 4144 Tolva",
            "kms": kms_actuales,
            "horas": random.randint(18000, 22000),
            "lat": lat_base + random.uniform(-0.05, 0.05),
            "lon": lon_base + random.uniform(-0.05, 0.05),
            "estado": "OPERATIVO",
            "kms_para_mantencion": kms_restantes,
            "db_comb": [
                {"Fecha": "2026-06-28", "Litros": "320 L", "Costo": "$352,000", "Rendimiento": "1.2 Km/L"},
                {"Fecha": "2026-07-01", "Litros": "280 L", "Costo": "$308,000", "Rendimiento": "1.3 Km/L"}
            ],
            "db_ot": [
                {"ID_OT": "OT-0941", "Tipo": "Preventiva", "Detalle": "Cambio pauta de filtros de aire y combustible", "Estado": "Cerrada", "Fecha": "2026-06-15"}
            ],
            "rutas": [
                {"Fecha": str(datetime.date.today()), "Origen": "Faena Áridos Maquehue", "Destino": "Obra Inacap Temuco", "Distancia": "14 Km", "Estado": "Completada"},
                {"Fecha": str(datetime.date.today()), "Origen": "Obra Inacap Temuco", "Destino": "Planta de Lavado", "Distancia": "22 Km", "Estado": "En Ruta"}
            ]
        })
    st.session_state.flota = flota_inicial

# --- ACCESO AL SISTEMA (CON 10 USUARIOS) ---
if not st.session_state.conectado:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Mercedes-Logo.svg/1024px-Mercedes-Logo.svg.png", width=70)
    st.title("🚛 SGO Cloud - Áridos Maquehue")
    st.caption("Sistema de Gestión Operativa y Mantenimiento de Flota")
    
    # Recuadro para que el profesor vea los 10 usuarios disponibles
    st.info("👥 **Accesos Autorizados al ERP (10 perfiles):** \n\n `admin1`, `gerente_op`, `jefe_flota`, `supervisor_taller`, `mecanico_jefe`, `logistica1`, `despachador`, `prevencionista`, `chofer_lider`, `auditor_ext`")
    
    usuario = st.text_input("Usuario (Rut/ID)", value="admin1")
    clave = st.text_input("Contraseña Operativa", type="password", value="inacap2026")
    
    usuarios_permitidos = [
        "admin1", "gerente_op", "jefe_flota", "supervisor_taller", 
        "mecanico_jefe", "logistica1", "despachador", "prevencionista", 
        "chofer_lider", "auditor_ext"
    ]
    
    if st.button("Iniciar Sesión Servidor AWS", type="primary", use_container_width=True):
        if usuario in usuarios_permitidos and clave == "inacap2026":
            st.session_state.conectado = True
            st.session_state.usuario = usuario
            st.rerun()
        else:
            st.error("❌ Credenciales inválidas.")

# --- ENTRADA AL ERP ---
else:
    st.write(f"🟢 **Servidor Activo** | Usuario actual: `{st.session_state.usuario}`")
    
    lista_desplegable = [f"{c['id']} [Patente: {c['patente']}]" for c in st.session_state.flota]
    camion_idx = st.selectbox("Seleccionar Camión Actros para Auditoría:", range(10), format_func=lambda x: lista_desplegable[x])
    camion_sel = st.session_state.flota[camion_idx]
    
    st.header(f"🚛 {camion_sel['id']} - Mod. {camion_sel['modelo']}")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Panel", 
        "📍 GPS y Rutas", 
        "📋 Checklist Diario", 
        "🛠️ Órdenes Taller", 
        "⛽ Comb",
        "📊 Informes"
    ])
    
    # 1. TAB PANEL
    with tab1:
        st.subheader("Telemetría del Motor y Alertas")
        col1, col2 = st.columns(2)
        col1.metric("Odómetro CAN-Bus", f"{camion_sel['kms']:,} Km")
        col2.metric("Horómetro de Trabajo", f"{camion_sel['horas']:,} Hrs")
        
        st.markdown("### ⏰ Alertas de Mantención Periódica")
        restantes = camion_sel['kms_para_mantencion']
        
        if restantes <= 0:
            st.error(f"🚨 ALERTAS CRÍTICA: ¡MANTENCIÓN VENCIDA HACE {abs(restantes)} KM! Se requiere detención inmediata e ingreso a taller.")
        elif restantes < 1000:
            st.warning(f"⚠️ ALERTA PREVENTIVA: Próximo Cambio de Aceite y Filtros en {restantes} Km. Agendar taller.")
        else:
            st.success(f"✅ Motor Estable: Faltan {restantes:,} Km para la pauta de mantención periódica estándar.")
            
        if camion_sel['estado'] == "OPERATIVO":
            st.info("🟢 Estado Operativo: LIBRE DE RESTRICCIONES EN RUTA")
        else:
            st.error("🔴 Estado Operativo: RESTRINGUIDO - BLOQUEADO EN TALLER")

    # 2. TAB GPS Y RUTAS
    with tab2:
        st.subheader("📍 Georreferenciación e Informe de Rutas")
        coords_flota = [{"lat": c["lat"], "lon": c["lon"]} for c in st.session_state.flota]
        st.map(pd.DataFrame(coords_flota), zoom=10)
        
        st.markdown("### 📋 Informe de Rutas Diarias (Logística)")
        st.dataframe(pd.DataFrame(camion_sel['rutas']), use_container_width=True)
        
        if st.button("Simular Recorrido en Ruta 🔄", use_container_width=True):
            camion_sel['kms'] += random.randint(15, 45)
            camion_sel['kms_para_mantencion'] -= random.randint(15, 45)
            camion_sel['lat'] += random.uniform(-0.005, 0.005)
            camion_sel['lon'] += random.uniform(-0.005, 0.005)
            st.rerun()

    # 3. TAB CHECKLIST 
    with tab3:
        st.subheader("📋 Checklist Diario de Control de Seguridad")
        st.write(f"Unidad Evaluada: **{camion_sel['patente']}**")
        
        chk_frenos = st.checkbox("Sistemas de Frenos y Presión de Aire OK", value=True, key="c1")
        chk_direccion = st.checkbox("Dirección Hidráulica y Servoasistencia OK", value=True, key="c2")
        chk_neumaticos = st.checkbox("Neumáticos (Tuercas de torque y bandas) OK", value=True, key="c3")
        chk_hidraulico = st.checkbox("Sistema Hidráulico de Tolva (Sin fugas) OK", value=True, key="c4")
        chk_luces = st.checkbox("Luces, Cinturón y Alarmas de retroceso OK", value=True, key="c5")
        
        st.markdown("---")
        comentarios_conductor = st.text_area("📝 Comentarios / Observaciones Adicionales:")
        
        if st.button("Enviar Registro de Inspección", type="primary", use_container_width=True):
            if not all([chk_frenos, chk_direccion, chk_neumaticos, chk_hidraulico, chk_luces]):
                camion_sel['estado'] = "BLOQUEADO"
                st.error("🚨 INSPECCIÓN RECHAZADA: Fallas detectadas. Camión bloqueado en el ERP.")
                if comentarios_conductor:
                    st.warning(f"📌 **Nota:** {comentarios_conductor}")
            else:
                camion_sel['estado'] = "OPERATIVO"
                st.success("✅ INSPECCIÓN APROBADA.")
                if comentarios_conductor:
                    st.info(f"📌 **Nota:** {comentarios_conductor}")

    # 4. TAB ÓRDENES DE TALLER
    with tab4:
        st.subheader("🛠️ Panel de Gestión: Órdenes de Taller")
        
        tipo_ot = st.selectbox("Tipo de Intervención:", ["Correctiva Crítica", "Preventiva Programada", "Predictiva"])
        detalle_falla = st.text_area("Descripción de los Trabajos:", placeholder="Ej: Pérdida de presión en balatas...")
        
        if st.button("Emitir Orden de Taller", type="primary", use_container_width=True):
            if detalle_falla:
                nueva_ot = {
                    "ID_OT": f"OT-{random.randint(1000, 9999)}",
                    "Tipo": tipo_ot,
                    "Detalle": detalle_falla,
                    "Estado": "Abierta",
                    "Fecha": str(datetime.date.today())
                }
                camion_sel['db_ot'].append(nueva_ot)
                st.success(f"📋 {nueva_ot['ID_OT']} emitida exitosamente.")
            else:
                st.warning("Describa el trabajo para aperturar la OT.")
                
        st.markdown("### 📂 Historial de Órdenes")
        if len(camion_sel['db_ot']) > 0:
            st.dataframe(pd.DataFrame(camion_sel['db_ot']), use_container_width=True)
            if st.button("Liberar Camión y Cerrar Órdenes Activas 🔓", use_container_width=True):
                for ot in camion_sel['db_ot']:
                    ot["Estado"] = "Cerrada"
                camion_sel['estado'] = "OPERATIVO"
                camion_sel['kms_para_mantencion'] = 10000
                st.success("Unidad reparada. Estado actualizado a OPERATIVO.")
        else:
            st.write("No registra órdenes.")

    # 5. TAB COMBUSTIBLE
    with tab5:
        st.subheader("⛽ Módulo de Abastecimiento")
        litros = st.number_input("Litros Cargados:", min_value=0, step=20)
        monto = st.number_input("Costo Total ($):", min_value=0, step=10000)
        
        if st.button("Registrar Carga", type="primary", use_container_width=True):
            if litros > 0 and monto > 0:
                nueva_carga = {
                    "Fecha": str(datetime.date.today()),
                    "Litros": f"{litros} L",
                    "Costo": f"${monto:,}",
                    "Rendimiento": f"{round(random.uniform(1.1, 1.4), 1)} Km/L"
                }
                camion_sel['db_comb'].append(nueva_carga)
                st.success("Carga guardada.")
                
        st.dataframe(pd.DataFrame(camion_sel['db_comb']), use_container_width=True)

    # 6. TAB INFORMES
    with tab6:
        st.subheader("📊 Informe Ejecutivo de Mantenimiento")
        col_inf1, col_inf2 = st.columns(2)
        col_inf1.metric("OT Ejecutadas", len(camion_sel['db_ot']))
        col_inf2.metric("Cargas Combustible", len(camion_sel['db_comb']))
        
        st.markdown(f"""
        - **Kilometraje Total:** **{camion_sel['kms']:,} Km**.
        - **Estado Físico:** **{camion_sel['estado']}**.
        - **Mantenibilidad:** Restan **{camion_sel['kms_para_mantencion']:,} Km** para la mantención.
        - **Logística:** **{len(camion_sel['rutas'])} rutas controladas**.
        """)
        st.button("📥 Descargar Informe en PDF", use_container_width=True)

    st.divider()
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state.conectado = False
        st.rerun()

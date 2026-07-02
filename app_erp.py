import streamlit as st
import pandas as pd
import datetime
import random

# --- CONFIGURACIÓN PARA CELULARES ---
st.set_page_config(page_title="ERP Flota Maquehue", page_icon="🚛", layout="centered")

# --- BASE DE DATOS EN LA NUBE (MEMORIA DE SESIÓN) ---
if 'conectado' not in st.session_state:
    st.session_state.conectado = False
if 'usuario' not in st.session_state:
    st.session_state.usuario = ""
if 'kms' not in st.session_state:
    st.session_state.kms = 532156
if 'horas' not in st.session_state:
    st.session_state.horas = 20000
if 'lat' not in st.session_state:
    st.session_state.lat = -38.7396
if 'lon' not in st.session_state:
    st.session_state.lon = -72.6019
if 'db_comb' not in st.session_state:
    st.session_state.db_comb = [
        {"Fecha": "2026-06-25", "Litros": "350 L", "Costo": "$385,000", "Rendimiento": "1.3 Km/L", "Operador": "operario1"},
        {"Fecha": "2026-06-28", "Litros": "400 L", "Costo": "$440,000", "Rendimiento": "1.2 Km/L", "Operador": "operario2"}
    ]

# --- PANTALLA DE LOGIN ---
if not st.session_state.conectado:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Mercedes-Logo.svg/1024px-Mercedes-Logo.svg.png", width=80)
    st.title("🏭 ERP Cloud - Maquehue")
    st.write("Autenticación segura requerida (AWS)")
    
    usuario = st.text_input("Usuario Corporativo", value="admin1")
    clave = st.text_input("Contraseña", type="password", value="inacap2026")
    
    if st.button("Conectar al Servidor Remoto", type="primary", use_container_width=True):
        if usuario in ["admin1", "jefe_taller"] and clave == "inacap2026":
            st.session_state.conectado = True
            st.session_state.usuario = usuario
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas.")

# --- INTERFAZ PRINCIPAL DEL ERP (CELULAR) ---
else:
    st.success(f"🌐 AWS Conectado | Operador: {st.session_state.usuario}")
    st.header("🚛 Actros 4144 (GP-GC-93)")
    
    # Crear pestañas deslizables (ideales para el dedo en el celular)
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Dash", "📍 GPS", "⛽ Comb", "📋 Check", "📊 Matriz"])
    
    # MÓDULO 1: DASHBOARD
    with tab1:
        st.subheader("Resumen de Operación")
        col1, col2 = st.columns(2)
        col1.metric("Odómetro CAN-Bus", f"{st.session_state.kms:,} Km", "+12 Km hoy")
        col2.metric("Horómetro Motor", f"{st.session_state.horas:,} Hrs", "+1.5 Hrs hoy")
        
        st.info("🟢 ESTADO FLOTA: OPERATIVO")
        st.warning("⚠️ ALERTA: 1 Orden Pendiente (SM1 - Chasis)")

    # MÓDULO 2: GPS EN VIVO
    with tab2:
        st.subheader("Rastreo Satelital")
        st.write(f"**Velocidad:** 45 Km/h | **Temp. Motor:** 90°C")
        
        # Mapa real interactivo para el celular
        df_mapa = pd.DataFrame({'lat': [st.session_state.lat], 'lon': [st.session_state.lon]})
        st.map(df_mapa, zoom=13)
        
        if st.button("Simular Movimiento (Ping)", use_container_width=True):
            st.session_state.kms += random.randint(5, 15)
            st.session_state.lat += 0.002
            st.session_state.lon -= 0.002
            st.rerun()

    # MÓDULO 3: COMBUSTIBLE
    with tab3:
        st.subheader("Carga de Diésel")
        litros = st.number_input("Litros Cargados", min_value=0, step=10)
        costo = st.number_input("Costo Total ($)", min_value=0, step=5000)
        
        if st.button("Guardar Registro", type="primary", use_container_width=True):
            if litros > 0 and costo > 0:
                nuevo_reg = {
                    "Fecha": str(datetime.date.today()),
                    "Litros": f"{litros} L",
                    "Costo": f"${costo:,}",
                    "Rendimiento": f"{round(random.uniform(1.1, 1.4), 1)} Km/L",
                    "Operador": st.session_state.usuario
                }
                st.session_state.db_comb.append(nuevo_reg)
                st.success("Guardado en la nube.")
        
        st.write("**Historial de Cargas:**")
        st.dataframe(pd.DataFrame(st.session_state.db_comb), use_container_width=True)

    # MÓDULO 4: CHECKLIST
    with tab4:
        st.subheader("Inspección Pre-Uso")
        st.write("Marque las fallas encontradas:")
        
        f1 = st.checkbox("Frenos y Sistema Neumático (Campanas, balatas)")
        f2 = st.checkbox("Chasis, Grapas y Suspensión Parabólica")
        f3 = st.checkbox("Niveles de Motor (Aceite, O-Rings)")
        f4 = st.checkbox("Sistema Hidráulico (Pistón de tolva)")
        f5 = st.checkbox("Neumáticos y Tuercas")
        
        if st.button("Enviar Evaluación", type="primary", use_container_width=True):
            if any([f1, f2, f3, f4, f5]):
                st.error("🚨 FALLA CRÍTICA DETECTADA: Vehículo bloqueado.")
            else:
                st.success("✅ Aprobado: Vehículo autorizado para operar.")

    # MÓDULO 5: CRITICIDAD
    with tab5:
        st.subheader("Matriz Kaufmann (FxF)")
        datos_crit = [
            {"Sistema": "Frenos", "F": 4, "I": 5, "Total": 20, "Riesgo": "🔴 CRÍTICO"},
            {"Sistema": "Chasis", "F": 4, "I": 4, "Total": 16, "Riesgo": "🔴 CRÍTICO"},
            {"Sistema": "Hidráulico", "F": 3, "I": 5, "Total": 15, "Riesgo": "🔴 CRÍTICO"},
            {"Sistema": "Motor", "F": 3, "I": 4, "Total": 12, "Riesgo": "🟡 MEDIO"},
            {"Sistema": "Eléctrico", "F": 2, "I": 3, "Total": 6, "Riesgo": "🟢 BAJO"}
        ]
        st.dataframe(pd.DataFrame(datos_crit), use_container_width=True)
        
    st.divider()
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state.conectado = False
        st.rerun()
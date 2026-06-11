import streamlit as st
import anthropic

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="ADS Design Spec Assistant",
    page_icon="🔩",
    layout="centered"
)

# ── Estilos ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .stTextInput input { background-color: #161b22; color: #e6edf3; border: 1px solid #30363d; }
    .stButton button { background-color: #2f81f7; color: white; border: none; border-radius: 6px; }
    .doc-tags { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
    .doc-tag { background: #1a3a5c; border: 1px solid #2f81f7; color: #388bfd;
               font-size: 11px; padding: 2px 10px; border-radius: 20px; }
    .source { background: #1a3020; border: 1px solid #2ea043; color: #3fb950;
              font-size: 11px; padding: 1px 8px; border-radius: 20px; display: inline-block; margin-top: 6px; }
</style>
""", unsafe_allow_html=True)

# ── System prompt con todas las specs ────────────────────────────────────────
SYSTEM_PROMPT = """Eres un asistente técnico interno de Acumed Digital Surgery (ADS), especializado en las especificaciones de diseño de dispositivos quirúrgicos CMF (craneomaxilofacial). Tu función es responder preguntas concretas sobre dimensiones, tolerancias, materiales, part numbers y requerimientos de diseño.

DOCUMENTOS DE REFERENCIA CARGADOS:

=== PS-015200 · ADS CMF DIAGNOSTIC MODEL DESIGN SPECIFICATIONS (v1.3) ===
- Productos: Modelos anatómicos de resina impresos en 3D (Formlabs 3B o 4B)
- Material: Clear Resin (Formlabs)
- Build volumes: Form 3B = 145×145×185 mm | Form 4B = 200×125×210 mm
- Regiones: Mandible, Maxilla, Cranium, Fibula (DEMO only)
- Struts/conectores: diámetro 7–10 mm
- Markings (embossed/debossed, Arial Black, 0.5mm profundo):
  • Case ID: 2.5–6.0 mm
  • Orientación PEEK Cranial: A/P/R/L
  • Orientación DEMO Fibula: PROX/DIST
  • DEMO marking requerido en todos los bench models
- Part Numbers Diagnóstico: 7701-7001N (Mandible), 7701-7003N (Maxilla), 7701-7005N (Max-to-Mand), 7701-7007N (Cranium-to-Max), 7701-7009N (Cranium-to-Mand), 7702-7001N (Upper Dental Arch), 7702-7003N (Lower Dental Arch), 7704-7001N (Cranial Implant Model), 7704-7002N (Cranial Defect Model)
- Cranial Defect Model: incluye ~20–50 mm de hueso alrededor del defecto
- DEMO PNs: 7701-8001N a 7703-8001R (bench testing only)

=== PS-015201 · ADS CMF TITANIUM IMPLANT DESIGN SPECIFICATIONS (v1.7) ===
- Material: CP Ti Grade 4 Per ASTM F67 | Color: Anodize blue violet
- Tolerancia: ±0.2 mm | Surface offset: 0.1 mm desde el hueso
- ORTHOGNATHIC IMPLANTS:
  • Plate Thickness: 0.8–1.0 mm (Maxilla), 1.0–1.2 mm (Mandible) | Min 0.6 mm | Max 2.0 mm
  • Plate Width Between Holes: preferido 3.5 mm | Min 3.0 mm
  • Screw Hole Bridge Width: Min 1.6 mm
  • Plate Length: Min 18 mm, Max 350 mm
  • Screw hole spacing (c-to-c): preferido 8.0 mm | Min 4.5 mm
  • Degree of curvature parallel: 0°–150° | Normal: 0°–165°
  • Compatible screws: ø1.6 y ø2.0, longitudes 4–22 mm
- RECONSTRUCTION Mid-Face/Maxilla:
  • Plate Thickness: 1.6–2.5 mm | Min 0.6 mm | Max 10.0 mm
  • Screw hole spacing: Min 4.0 mm
  • Compatible screws: ø1.6, ø2.0, ø2.4, longitudes 4–22 mm
- RECONSTRUCTION Mandible:
  • Plate Thickness: 2.0–2.5 mm | Min 2.0 mm | Max 3.0 mm
  • Plate Width Between Holes: 6.63–7.0 mm | Min 6.63 mm | Max 16.0 mm
  • Plate Length: Min 78 mm, Max 320 mm
  • Screw hole spacing: Min 8.0 mm
- PLATE HOLE SPECS (Table 9):
  • ø1.6 non-locking: Hole ID ø2.0±0.1 mm | Bridge 1.60 mm | Plate OD ø5.20 mm
  • ø2.0 non-locking: Hole ID ø2.4±0.1 mm | Bridge 1.60 mm | Plate OD ø5.60 mm
  • ø2.0 locking: Hole ID ø2.3±0.1 mm | Bridge 1.60 mm | Plate OD ø5.40 mm
- PLATE HOLE SPECS (Table 10):
  • ø2.0/ø2.4: Hole ID ø2.81±0.1 mm | Standard bridge 2.08 mm → OD ø7.00 mm | Wide 2.58 mm → OD ø8.00 mm
- LASER MARKING: Required: Batch Number, Reticle, Laterality | Preferred: Patient Initials, Part Number, Single Use | Min 0.04 inches
- SCREW CLEARANCE: min ø8 mm c-to-c | min ø8 mm desde bordes | buffer ø8mm a min 5 mm del cuello de dientes

=== PS-015203 · ADS CMF RESIN GUIDE DESIGN SPECIFICATIONS (v1.3) ===
- Material: Biomed Clear Resin (Formlabs) | Tolerancia: ±0.2 mm | Surface offset: 0.1 mm
- DENTAL SPLINTS:
  • Length: 60–70 mm | Thickness: 2.0–20 mm | Depth: 45–55 mm | Width: 15–50 mm
  • Vestibular Width: Min 1 mm / Max 2.5 mm (3.5 mm si tiene wiring holes)
  • Wire hole diameter: 1.85–3.2 mm | Surface offset: 0.1 mm (0.15 mm trauma)
  • Dental impression: Shallow ~1mm | Medium: hasta brackets | Deep: hasta 0.5mm sobre brackets
- PALATAL SPLINTS:
  • Length: 20–70 mm | Width: 15–50 mm | Depth: 15–50 mm
  • Thickness (holes): MIN 1.5 mm | Thickness (palatal): MIN 2.5 mm
  • Wire hole: 0.8–2.2 mm | Surface offset: 0.1–2.0 mm (típico ~1.5 mm)
- DENTAL SPLINT CUT GUIDE ALIGNER: Rod diameter MIN 3.5 mm | Assembly: Butterfly o Hole & Peg
- RECON CUT GUIDE ALIGNER: Rod diameter 3.5–6 mm | Assembly: Hole & Peg
- MARKINGS (debossed, Arial Black, 0.5mm): Case ID Min 2.5 mm (pref. 3.0 mm) | IS/FS + Top para splints
- PART NUMBERS: 7702-6001N (Intermediate Splint), 7702-6002N (Final Splint), 7702-6004N (Palatal Splint), 7702-6003N (Dental Splint Cut Guide Aligner), 7703-6006N (RECON Cut Guide Aligner)

=== PS-015204 · ADS CMF TITANIUM GUIDE DESIGN SPECIFICATIONS (v1.5) ===
- Material: CP Ti Grade 4 | Color: Anodize blue violet | Tolerancia: ±0.2 mm | Surface offset: 0.1 mm
- CUT FEATURES:
  • Thin Slot: Height MIN 0.8 mm | Wall MIN 2.5 mm | Width 0.8–1.2 mm | Length 3.5–8.0 mm | Int fillet 0.3–0.5 mm | Ext fillet 0.5–1.0 mm
  • Standard Slot: Height 1 mm | Wall MIN 2.5 mm | Connection MIN 6 mm | Width 0.8–1.2 mm
  • Thin Resection: Height MIN 0.8 mm | Wall MIN 2.5 mm | Width 0.8–8.2 mm | Length 3.5–8.0 mm
  • Standard Resection: Height 1 mm | Wall MIN 2.5 mm | Connection MIN 6 mm | Width 0.8–12.2 mm
  • Flange: Height 1.5–5.5 mm (pref. 3.5 mm) | Width 2.5 mm
- DENTAL SUPPORT: Le Fort & Genio 4–6 dientes | BSSO 2–6 dientes | Width MIN 4 mm | Rod MIN 3 mm | Impression depth MIN 1 mm | Clearance brackets MIN 0.5 mm
- FENESTRATIONS: Hole 1.5–2.0 mm | Separation 2.5–4.0 mm | Edge distance MIN 2.6 mm
- DRILL CYLINDERS (familias 216-16XX, 208-16XX, 202-20XX, etc.):
  • ø1.6: Drill ø1.3 | Cyl ID ø1.5±0.1 | OD ø5.6 | Height MIN 2 mm
  • ø2.0: Drill ø1.6 | Cyl ID ø1.8±0.1 | OD ø5.6 | Height MIN 2 mm
  • ø2.4 (familias 234-20XX, 206-24XX, etc.): Drill ø2.0 | Cyl ID ø2.2±0.1 | OD ø5.6 | Height MIN 2 mm
- TEMP FIX CYLINDERS:
  • ø1.6: Fix Cyl ID ø2.0±0.1 | OD ø5.6 | Height MIN 2 mm
  • ø2.0 (familias estándar): Fix Cyl ID ø2.4±0.1 | OD ø5.6 | Height MIN 2 mm
  • ø2.0/ø2.4 (familias recon): Fix Cyl ID ø2.84±0.1 | OD ø5.6 | Height MIN 2 mm
- TROCAR HOLES: OD 6.0 mm | ID 5.0 mm | Thru fixation 2.84±0.1 mm | Thru drill 2.3 mm | Counterbore MIN 4.4 mm
- CONNECTION FEATURES:
  • Hole & Peg: Radius 1.15 mm | Wall MIN 1.1 mm | Flat width 2.7 mm | Engagement MIN 2.2 mm | Overall ~8.6 mm
  • Butterfly: Length base ~8.7 mm | Height ~6.7 mm | Pin diameter 2.0 mm | Wall resin 1.9 mm
  • Hook: Offset 0.27 mm | Height MIN 1.2 mm | Width MIN 1.4 mm / 4.0 mm
- LE FORT GUIDE: Length 40–95 mm | Width 20–60 mm | Bridge (bilateral) 4.0–6.0 mm | Depth 15–45 mm | Thickness MIN 0.8 mm
- BSSO GUIDE: Length 20–70 mm | Width 13–50 mm | Depth 10–30 mm | Thickness MIN 0.8 mm
- GENIOPLASTY GUIDE: Length 30–100 mm | Width 13–90 mm | Depth 10–30 mm | Thickness MIN 0.8 mm
- CONDYLE ALIGNMENT: Length 15–65 mm | Width 10–30 mm | Bridge thickness MIN 2.3 mm | Bridge width MIN 2.0 mm | Min temp fix 3 por lado
- RECON GUIDE (Mand/Max): Length 15–70 mm | Width 13–50 mm | Depth 10–25 mm | Thickness MIN 0.8 mm
- FIBULA GUIDE: Length 20–300 mm | Width 10–30 mm | Depth 6–12 mm | Thickness MIN 1.3 mm | Surface offset 0.5 mm | Cut Slot Width 0.3–1.0 mm | Segments 1–7 | Markings PROX & DIST
- DENTAL ANCHOR GUIDE: Length 30–90 mm | Width 20–60 mm | Depth 5–30 mm | Thickness 2.0 mm | Bridge MIN 3.0 mm
- TI PALATAL SPLINT: Length 20–70 mm | Width 15–50 mm | Thickness holes MIN 0.8 mm | Thickness palatal MIN 1.2 mm | Wire hole 0.3–1.8 mm
- LASER MARKING: Required: Batch Number, Reticle, Laterality | Preferred: Patient Initials, Part Number, Single Use | Min 0.04 inches

INSTRUCCIONES:
- Responde siempre en español
- Sé preciso: cita la tabla, sección y documento
- Presenta valores mínimos, máximos y preferidos cuando existan
- Usa tablas para múltiples dimensiones
- Si no encuentras la información, dilo claramente
- No inventes especificaciones"""

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("## 🔩 ADS Design Spec Assistant")
st.markdown("**Acumed Digital Surgery · TDS Internal Tool**")
st.markdown("""
<div class="doc-tags">
  <span class="doc-tag">PS-015200 · Diagnostic Model</span>
  <span class="doc-tag">PS-015201 · Ti Implant</span>
  <span class="doc-tag">PS-015203 · Resin Guide</span>
  <span class="doc-tag">PS-015204 · Ti Guide</span>
</div>
""", unsafe_allow_html=True)
st.divider()

# ── API Key input ─────────────────────────────────────────────────────────────
api_key = st.text_input(
    "🔑 API Key de Anthropic",
    type="password",
    placeholder="sk-ant-api03-...",
    help="Ingresa tu API key de console.anthropic.com"
)

# ── Historial de chat ─────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes anteriores
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Sugerencias ──────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("**💡 Preguntas de ejemplo:**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("¿Grosor mínimo del dental splint?"):
            st.session_state.suggested = "¿Cuál es el grosor mínimo del dental splint en resina?"
        if st.button("¿Dimensiones del slot tipo thin?"):
            st.session_state.suggested = "¿Cuáles son las dimensiones del slot tipo thin en Ti guides?"
    with col2:
        if st.button("¿Drill cylinder para tornillo ø2.0?"):
            st.session_state.suggested = "¿Qué dimensiones tiene el drill cylinder para tornillo ø2.0?"
        if st.button("¿Markings requeridos en Ti implant?"):
            st.session_state.suggested = "¿Qué markings son requeridos en un Ti implant?"

# ── Input de chat ─────────────────────────────────────────────────────────────
prompt = st.chat_input("Escribe tu pregunta sobre las specs de diseño...")

# Manejar sugerencias
if "suggested" in st.session_state:
    prompt = st.session_state.suggested
    del st.session_state.suggested

if prompt:
    if not api_key:
        st.error("⚠️ Ingresa tu API key de Anthropic para continuar.")
    else:
        # Mostrar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Obtener respuesta de Claude
        with st.chat_message("assistant"):
            with st.spinner("Consultando specs..."):
                try:
                    client = anthropic.Anthropic(api_key=api_key)
                    response = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1000,
                        system=SYSTEM_PROMPT,
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ]
                    )
                    reply = response.content[0].text
                    st.markdown(reply)
                    st.markdown('<span class="source">✓ Fuente: PS-015200/01/03/04</span>', unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Error: {str(e)}")

import os
import io
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk

# ==========================================================
#                   DATOS DEL SISTEMA
# ==========================================================
USUARIO_ADMIN = "admin"
PASS_ADMIN = "1234"
URL_IMAGEN_FONDO = "https://www.shutterstock.com/image-illustration/soccer-ball-basket-3d-illustration-260nw-1898407648.jpg"

productos = [
    {
        "codigo": "F001",
        "nombre": "Balón Adidas Pro",
        "deporte": "Fútbol",
        "categoria": "Balones",
        "precio": 350.00,
        "stock": 10,
        "imagen_url": "https://images.unsplash.com/photo-1614632537190-23e4146777db?w=300"
    },
    {
        "codigo": "F002",
        "nombre": "Guantes de Portero",
        "deporte": "Fútbol",
        "categoria": "Porteros",
        "precio": 275.00,
        "stock": 6,
        "imagen_url": "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=300"
    },
    {
        "codigo": "F003",
        "nombre": "Tacos Nike Phantom",
        "deporte": "Fútbol",
        "categoria": "Calzado",
        "precio": 850.00,
        "stock": 5,
        "imagen_url": "https://images.unsplash.com/photo-1511886929837-354d827aae26?w=300"
    },
    {
        "codigo": "B001",
        "nombre": "Balón Spalding NBA",
        "deporte": "Básquetbol",
        "categoria": "Balones",
        "precio": 400.00,
        "stock": 8,
        "imagen_url": "https://images.unsplash.com/photo-1519861531473-9200262188bf?w=300"
    },
    {
        "codigo": "B002",
        "nombre": "Camiseta Deportiva",
        "deporte": "Básquetbol",
        "categoria": "Ropa",
        "precio": 300.00,
        "stock": 12,
        "imagen_url": "https://images.unsplash.com/photo-1577219491135-ce391730fb2c?w=300"
    },
    {
        "codigo": "B003",
        "nombre": "Tenis Básquetbol Nike",
        "deporte": "Básquetbol",
        "categoria": "Calzado",
        "precio": 750.00,
        "stock": 7,
        "imagen_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300"
    }
]

ventas = []
carrito_cliente = []
cache_imagenes = {}

# ==========================================================
#                   CONFIGURACIÓN VENTANA
# ==========================================================
ventana = tk.Tk()
ventana.title("SPORTZONE - Tienda Deportiva")
ventana.geometry("1050x700")
ventana.minsize(950, 650)

img_original = None
imagen_tk = None

def cargar_imagen_fondo():
    global img_original
    try:
        if not os.path.exists("fondo.jpg"):
            headers = {'User-Agent': 'Mozilla/5.0'}
            respuesta = requests.get(URL_IMAGEN_FONDO, headers=headers, timeout=5)
            if respuesta.status_code == 200:
                with open("fondo.jpg", "wb") as f:
                    f.write(respuesta.content)
        img_original = Image.open("fondo.jpg")
    except Exception as e:
        print(f"No se pudo cargar la imagen de fondo: {e}")

cargar_imagen_fondo()

canvas = tk.Canvas(ventana, highlightthickness=0)
canvas.pack(fill="both", expand=True)

def actualizar_fondo(event=None):
    global imagen_tk
    if img_original:
        w, h = ventana.winfo_width(), ventana.winfo_height()
        if w > 10 and h > 10:
            img_res = img_original.resize((w, h), Image.Resampling.LANCZOS)
            imagen_tk = ImageTk.PhotoImage(img_res)
            canvas.delete("fondo")
            canvas.create_image(0, 0, image=imagen_tk, anchor="nw", tags="fondo")
            canvas.tag_lower("fondo")

ventana.bind("<Configure>", actualizar_fondo)

def cargar_imagen_async(url, label_destino):
    if not url:
        return
    if url in cache_imagenes:
        label_destino.config(image=cache_imagenes[url], text="")
        label_destino.image = cache_imagenes[url]
        return

    def tarea_descarga():
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=3)
            if resp.status_code == 200:
                img_data = Image.open(io.BytesIO(resp.content))
                img_data = img_data.resize((170, 110), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img_data)
                cache_imagenes[url] = img_tk
                
                ventana.after(0, lambda: label_destino.config(image=img_tk, text="") if label_destino.winfo_exists() else None)
                if hasattr(label_destino, "image"):
                    label_destino.image = img_tk
        except Exception:
            ventana.after(0, lambda: label_destino.config(text="📦 Imagen no disponible") if label_destino.winfo_exists() else None)

    threading.Thread(target=tarea_descarga, daemon=True).start()

def limpiar_ventana():
    for widget in canvas.winfo_children():
        widget.destroy()

style = ttk.Style()
style.theme_use("clam")
style.configure("TFrame", background="#ffffff")
style.configure("TLabel", background="#ffffff", foreground="#000000")

# ==========================================================
#                   SELECCIÓN DE PERFIL / INICIO
# ==========================================================
def mostrar_inicio():
    limpiar_ventana()
    
    marco_padre = tk.Frame(canvas, bg="")
    canvas.create_window(525, 350, window=marco_padre, anchor="center")

    marco = ttk.Frame(marco_padre, padding=40)
    marco.pack()

    ttk.Label(marco, text="⚽ SPORTZONE 🏀", font=("Arial", 28, "bold")).pack(pady=10)
    ttk.Label(marco, text="¡Bienvenido a la Tienda Deportiva!", font=("Arial", 14)).pack(pady=5)
    ttk.Label(marco, text="Seleccione su modo de acceso:", font=("Arial", 11)).pack(pady=15)

    ttk.Button(marco, text="🛍️ INGRESAR COMO CLIENTE", command=mostrar_tienda_cliente, width=32).pack(pady=10)
    ttk.Button(marco, text="🔑 ACCESO ADMINISTRADOR", command=mostrar_login_admin, width=32).pack(pady=10)

# ==========================================================
#                     LOGIN ADMIN
# ==========================================================
def mostrar_login_admin():
    limpiar_ventana()
    
    marco_padre = tk.Frame(canvas, bg="")
    canvas.create_window(525, 350, window=marco_padre, anchor="center")

    marco = ttk.Frame(marco_padre, padding=40)
    marco.pack()

    ttk.Label(marco, text="🔑 PANEL DE ADMINISTRACIÓN", font=("Arial", 20, "bold")).pack(pady=10)

    ttk.Label(marco, text="Usuario:").pack(anchor="w", pady=(15, 5))
    e_usuario = ttk.Entry(marco, width=35)
    e_usuario.pack()
    e_usuario.insert(0, "admin")  # Valor por defecto para agilizar pruebas

    ttk.Label(marco, text="Contraseña:").pack(anchor="w", pady=(10, 5))
    e_pass = ttk.Entry(marco, width=35, show="*")
    e_pass.pack()
    e_pass.insert(0, "1234")  # Valor por defecto para agilizar pruebas

    def ingresar():
        usuario_ingresado = e_usuario.get().strip()
        pass_ingresada = e_pass.get().strip()
        
        if usuario_ingresado == USUARIO_ADMIN and pass_ingresada == PASS_ADMIN:
            messagebox.showinfo("Bienvenido", "¡Acceso concedido!")
            mostrar_menu_admin()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    ttk.Button(marco, text="INGRESAR", command=ingresar).pack(pady=20)
    ttk.Button(marco, text="⬅️ Volver", command=mostrar_inicio).pack()

# ==========================================================
#           MODO CLIENTE - CATÁLOGO TARJETAS E-COMMERCE
# ==========================================================
def mostrar_tienda_cliente():
    limpiar_ventana()

    top_frame = ttk.Frame(canvas, padding=10)
    canvas.create_window(0, 0, window=top_frame, anchor="nw", width=ventana.winfo_width())

    ttk.Label(top_frame, text="🛒 CATÁLOGO DE PRODUCTOS", font=("Arial", 18, "bold")).pack(side="left", padx=10)
    ttk.Button(top_frame, text="🚪 Cambiar Perfil", command=mostrar_inicio).pack(side="right", padx=5)
    
    cant_carrito = sum(item['cantidad'] for item in carrito_cliente)
    btn_carrito = ttk.Button(top_frame, text=f"🛍️ Ver Carrito ({cant_carrito})", command=vista_carrito)
    btn_carrito.pack(side="right", padx=5)

    global contenedor_dinamico
    contenedor_dinamico = ttk.Frame(canvas, padding=10)
    canvas.create_window(525, 370, window=contenedor_dinamico, anchor="center")

    vista_catalogo_tarjetas()

def vista_catalogo_tarjetas(filtro_deporte=None):
    for widget in contenedor_dinamico.winfo_children():
        widget.destroy()

    # Filtros
    frame_filtros = ttk.Frame(contenedor_dinamico)
    frame_filtros.pack(fill="x", pady=5)

    ttk.Button(frame_filtros, text="Todos", command=lambda: vista_catalogo_tarjetas(None)).pack(side="left", padx=5)
    ttk.Button(frame_filtros, text="⚽ Fútbol", command=lambda: vista_catalogo_tarjetas("Fútbol")).pack(side="left", padx=5)
    ttk.Button(frame_filtros, text="🏀 Básquetbol", command=lambda: vista_catalogo_tarjetas("Básquetbol")).pack(side="left", padx=5)

    lista_mostrar = productos if not filtro_deporte else [p for p in productos if p["deporte"] == filtro_deporte]

    # Canvas interno con Scrollbar
    canvas_scroll = tk.Canvas(contenedor_dinamico, width=820, height=460, bg="#f5f5f5", highlightthickness=0)
    scrollbar = ttk.Scrollbar(contenedor_dinamico, orient="vertical", command=canvas_scroll.yview)
    grid_frame = tk.Frame(canvas_scroll, bg="#f5f5f5")

    grid_frame.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
    canvas_scroll.create_window((0, 0), window=grid_frame, anchor="nw")
    canvas_scroll.configure(yscrollcommand=scrollbar.set)

    canvas_scroll.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Renderizar Tarjetas
    columnas_max = 3
    for index, prod in enumerate(lista_mostrar):
        row = index // columnas_max
        col = index % columnas_max

        card = tk.Frame(grid_frame, bg="#ffffff", bd=1, relief="solid", padx=10, pady=8)
        card.grid(row=row, column=col, padx=10, pady=10)

        # Tag Oferta
        lbl_tag = tk.Label(card, text="OFERTA", bg="#e63946", fg="white", font=("Arial", 8, "bold"))
        lbl_tag.pack(anchor="ne")

        # Contenedor de imagen con tamaño fijo para evitar que se aplaste
        frame_img = tk.Frame(card, width=170, height=110, bg="#eeeeee")
        frame_img.pack_propagate(False)
        frame_img.pack(pady=4)

        lbl_img = tk.Label(frame_img, text="Cargando...", font=("Arial", 9), bg="#eeeeee", fg="#555555")
        lbl_img.pack(fill="both", expand=True)
        
        cargar_imagen_async(prod.get("imagen_url", ""), lbl_img)

        # Nombre
        lbl_nom = tk.Label(card, text=prod["nombre"], font=("Arial", 10, "bold"), bg="#ffffff", wraplength=170)
        lbl_nom.pack()

        # Categoría
        lbl_cat = tk.Label(card, text=f"{prod['deporte']} • {prod['categoria']}", font=("Arial", 8), fg="#666666", bg="#ffffff")
        lbl_cat.pack()

        # Precio
        lbl_precio = tk.Label(card, text=f"Q{prod['precio']:.2f}", font=("Arial", 11, "bold"), fg="#1d3557", bg="#ffffff")
        lbl_precio.pack(pady=2)

        # Stock
        lbl_stock = tk.Label(card, text=f"Stock: {prod['stock']} un.", font=("Arial", 8), fg="#2a9d8f", bg="#ffffff")
        lbl_stock.pack()

        # Botón
        def crear_cmd(p=prod):
            return lambda: agregar_carrito_directo(p)

        btn_add = tk.Button(card, text="🛒 Añadir al carrito", bg="#2a9d8f", fg="white", font=("Arial", 9, "bold"), relief="flat", command=crear_cmd())
        btn_add.pack(pady=6, fill="x")

def agregar_carrito_directo(prod):
    cant_en_carrito = sum(c["cantidad"] for c in carrito_cliente if c["producto"]["codigo"] == prod["codigo"])
    if cant_en_carrito + 1 > prod["stock"]:
        messagebox.showerror("Sin Stock", f"No hay más unidades disponibles de {prod['nombre']}.")
        return

    for c in carrito_cliente:
        if c["producto"]["codigo"] == prod["codigo"]:
            c["cantidad"] += 1
            c["subtotal"] = c["cantidad"] * prod["precio"]
            break
    else:
        carrito_cliente.append({"producto": prod, "cantidad": 1, "subtotal": prod["precio"]})

    messagebox.showinfo("Carrito Actualizado", f"¡{prod['nombre']} añadido al carrito!")
    mostrar_tienda_cliente()

def vista_carrito():
    for widget in contenedor_dinamico.winfo_children():
        widget.destroy()

    ttk.Label(contenedor_dinamico, text="🛍️ TU CARRITO DE COMPRAS", font=("Arial", 16, "bold")).pack(pady=10)

    if not carrito_cliente:
        ttk.Label(contenedor_dinamico, text="El carrito está vacío.").pack(pady=30)
        ttk.Button(contenedor_dinamico, text="⬅️ Volver al Catálogo", command=mostrar_tienda_cliente).pack()
        return

    columnas = ("codigo", "nombre", "precio", "cantidad", "subtotal")
    tabla = ttk.Treeview(contenedor_dinamico, columns=columnas, show="headings", height=6)

    headers = {"codigo": "Código", "nombre": "Producto", "precio": "Precio Unit.", "cantidad": "Cantidad", "subtotal": "Subtotal"}
    for col in columnas:
        tabla.heading(col, text=headers[col])

    for item in carrito_cliente:
        p = item["producto"]
        tabla.insert("", "end", values=(p["codigo"], p["nombre"], f"Q{p['precio']:.2f}", item["cantidad"], f"Q{item['subtotal']:.2f}"))

    tabla.pack(fill="both", expand=True, pady=10)

    total_compra = sum(item["subtotal"] for item in carrito_cliente)
    ttk.Label(contenedor_dinamico, text=f"TOTAL A PAGAR: Q{total_compra:.2f}", font=("Arial", 14, "bold")).pack(pady=5)

    frame_acciones = ttk.Frame(contenedor_dinamico)
    frame_acciones.pack(pady=10)

    def quitar_item():
        selected = tabla.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un ítem del carrito para quitar.")
            return
        cod = tabla.item(selected[0])["values"][0]
        global carrito_cliente
        carrito_cliente = [item for item in carrito_cliente if item["producto"]["codigo"] != cod]
        mostrar_tienda_cliente()
        vista_carrito()

    def finalizar_compra():
        if messagebox.askyesno("Confirmar Compra", f"¿Desea confirmar su compra por un total de Q{total_compra:.2f}?"):
            for item in carrito_cliente:
                prod = item["producto"]
                cant = item["cantidad"]
                prod["stock"] -= cant
                ventas.append({"codigo": prod["codigo"], "nombre": prod["nombre"], "cantidad": cant, "total": item["subtotal"]})

            carrito_cliente.clear()
            messagebox.showinfo("¡Gracias por su compra!", "Su pedido se ha procesado exitosamente y se ha registrado en el historial de ventas.")
            mostrar_tienda_cliente()

    ttk.Button(frame_acciones, text="❌ Quitar Ítem", command=quitar_item).pack(side="left", padx=5)
    ttk.Button(frame_acciones, text="⬅️ Seguir Comprando", command=mostrar_tienda_cliente).pack(side="left", padx=5)
    ttk.Button(frame_acciones, text="✅ FINALIZAR COMPRA", command=finalizar_compra).pack(side="left", padx=5)

# ==========================================================
#                   PANEL ADMINISTRADOR
# ==========================================================
def mostrar_menu_admin():
    limpiar_ventana()

    top_frame = ttk.Frame(canvas, padding=10)
    canvas.create_window(0, 0, window=top_frame, anchor="nw", width=ventana.winfo_width())

    ttk.Label(top_frame, text="⚙️ PANEL DE ADMINISTRADOR", font=("Arial", 18, "bold")).pack(side="left", padx=10)
    ttk.Button(top_frame, text="🚪 Cerrar Sesión", command=mostrar_inicio).pack(side="right", padx=5)
    ttk.Button(top_frame, text="🏠 Menú Admin", command=mostrar_home_admin).pack(side="right", padx=5)

    global contenedor_dinamico
    contenedor_dinamico = ttk.Frame(canvas, padding=15)
    canvas.create_window(525, 370, window=contenedor_dinamico, anchor="center")

    mostrar_home_admin()

def mostrar_home_admin():
    for widget in contenedor_dinamico.winfo_children():
        widget.destroy()

    ttk.Label(contenedor_dinamico, text="Gestión de Inventario y Finanzas", font=("Arial", 15, "bold")).pack(pady=10)

    marco_botones = ttk.Frame(contenedor_dinamico)
    marco_botones.pack(expand=True)

    botones = [
        ("📦 Inventario General", lambda: mostrar_tabla_productos_admin(productos, "INVENTARIO GENERAL")),
        ("🛒 Reabastecer Stock", vista_reabastecer),
        ("➕ Agregar Producto Nuevo", vista_agregar),
        ("🔎 Buscar Producto", vista_buscar),
        ("🗑️ Eliminar Producto", vista_eliminar),
        ("📋 Historial de Ventas", vista_historial_ventas),
        ("📊 Estadísticas de Ventas", mostrar_estadisticas),
        ("🔃 Ordenar Inventario", vista_ordenar)
    ]

    for i, (texto, func) in enumerate(botones):
        btn = ttk.Button(marco_botones, text=texto, command=func, width=28)
        btn.grid(row=i//2, column=i%2, padx=10, pady=8)

def mostrar_tabla_productos_admin(lista, titulo):
    for widget in contenedor_dinamico.winfo_children(): widget.destroy()
    ttk.Label(contenedor_dinamico, text=titulo, font=("Arial", 16, "bold")).pack(pady=10)

    columnas = ("codigo", "nombre", "deporte", "categoria", "precio", "stock")
    tabla = ttk.Treeview(contenedor_dinamico, columns=columnas, show="headings", height=8)
    
    headers = {"codigo": "Código", "nombre": "Producto", "deporte": "Deporte", "categoria": "Categoría", "precio": "Precio", "stock": "Stock"}
    for col in columnas:
        tabla.heading(col, text=headers[col])
        tabla.column(col, width=110)

    for p in lista:
        tabla.insert("", "end", values=(p["codigo"], p["nombre"], p["deporte"], p["categoria"], f"Q{p['precio']:.2f}", p["stock"]))

    tabla.pack(fill="both", expand=True, pady=10)

def vista_reabastecer():
    for widget in contenedor_dinamico.winfo_children(): widget.destroy()
    ttk.Label(contenedor_dinamico, text="🛒 REABASTECER STOCK", font=("Arial", 16, "bold")).pack(pady=15)

    marco = ttk.Frame(contenedor_dinamico)
    marco.pack(pady=10)

    ttk.Label(marco, text="Código del Producto:").grid(row=0, column=0, pady=5, sticky="w")
    e_cod = ttk.Entry(marco, width=20)
    e_cod.grid(row=0, column=1, pady=5)

    ttk.Label(marco, text="Cantidad a Agregar:").grid(row=1, column=0, pady=5, sticky="w")
    e_cant = ttk.Entry(marco, width=20)
    e_cant.grid(row=1, column=1, pady=5)

    def confirmar():
        try:
            cod, cant = e_cod.get().strip().upper(), int(e_cant.get())
            if cant <= 0: raise ValueError()
            for p in productos:
                if p["codigo"] == cod:
                    p["stock"] += cant
                    messagebox.showinfo("Éxito", f"Nuevo stock de {p['nombre']}: {p['stock']}")
                    mostrar_home_admin()
                    return
            messagebox.showerror("Error", "Producto no encontrado.")
        except ValueError:
            messagebox.showerror("Error", "Ingrese una cantidad entera válida.")

    ttk.Button(contenedor_dinamico, text="SUMAR AL STOCK", command=confirmar).pack(pady=15)

def vista_agregar():
    for widget in contenedor_dinamico.winfo_children(): widget.destroy()
    ttk.Label(contenedor_dinamico, text="➕ AGREGAR NUEVO PRODUCTO", font=("Arial", 16, "bold")).pack(pady=10)

    marco = ttk.Frame(contenedor_dinamico)
    marco.pack(pady=10)

    campos = ["Código", "Nombre", "Deporte", "Categoría", "Precio", "Stock", "URL Imagen"]
    entradas = {}

    for i, campo in enumerate(campos):
        ttk.Label(marco, text=campo).grid(row=i, column=0, sticky="w", pady=4, padx=10)
        e = ttk.Entry(marco, width=30)
        e.grid(row=i, column=1, pady=4, padx=10)
        entradas[campo] = e

    def guardar():
        try:
            cod, nom, dep, cat = entradas["Código"].get().strip().upper(), entradas["Nombre"].get().strip(), entradas["Deporte"].get().strip(), entradas["Categoría"].get().strip()
            pre, stk = float(entradas["Precio"].get()), int(entradas["Stock"].get())
            url_img = entradas["URL Imagen"].get().strip() or "https://images.unsplash.com/photo-1511886929837-354d827aae26?w=300"

            if not all([cod, nom, dep, cat]) or pre <= 0 or stk < 0: raise ValueError()
            if any(p["codigo"] == cod for p in productos):
                messagebox.showerror("Error", "El código ya existe.")
                return

            productos.append({"codigo": cod, "nombre": nom, "deporte": dep, "categoria": cat, "precio": pre, "stock": stk, "imagen_url": url_img})
            messagebox.showinfo("Éxito", "Producto registrado correctamente.")
            mostrar_home_admin()
        except ValueError:
            messagebox.showerror("Error", "Revise los campos introducidos.")

    ttk.Button(contenedor_dinamico, text="GUARDAR", command=guardar).pack(pady=10)

def vista_buscar():
    for widget in contenedor_dinamico.winfo_children(): widget.destroy()
    ttk.Label(contenedor_dinamico, text="🔎 BUSCAR PRODUCTO", font=("Arial", 16, "bold")).pack(pady=10)

    marco = ttk.Frame(contenedor_dinamico)
    marco.pack(pady=10)

    ttk.Label(marco, text="Código o Nombre:").pack(side="left", padx=5)
    e_buscar = ttk.Entry(marco, width=25)
    e_buscar.pack(side="left", padx=5)

    res_frame = ttk.Frame(contenedor_dinamico)
    res_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def ejecutar_busqueda():
        for w in res_frame.winfo_children(): w.destroy()
        texto = e_buscar.get().strip().lower()
        encontrados = [p for p in productos if texto in p["codigo"].lower() or texto in p["nombre"].lower()]
        if not encontrados:
            ttk.Label(res_frame, text="No se encontraron coincidencias.").pack()
            return
        mostrar_tabla_productos_admin(encontrados, "Resultados")

    ttk.Button(marco, text="BUSCAR", command=ejecutar_busqueda).pack(side="left", padx=5)

def vista_eliminar():
    for widget in contenedor_dinamico.winfo_children(): widget.destroy()
    ttk.Label(contenedor_dinamico, text="🗑️ ELIMINAR PRODUCTO", font=("Arial", 16, "bold")).pack(pady=15)

    marco = ttk.Frame(contenedor_dinamico)
    marco.pack(pady=10)

    ttk.Label(marco, text="Ingrese Código:").pack(side="left", padx=5)
    e_cod = ttk.Entry(marco, width=20)
    e_cod.pack(side="left", padx=5)

    def eliminar():
        cod = e_cod.get().strip().upper()
        for p in productos:
            if p["codigo"] == cod:
                if messagebox.askyesno("Confirmar", f"¿Eliminar {p['nombre']}?"):
                    productos.remove(p)
                    messagebox.showinfo("Éxito", "Producto eliminado.")
                    mostrar_home_admin()
                return
        messagebox.showerror("Error", "Producto no encontrado.")

    ttk.Button(marco, text="ELIMINAR", command=eliminar).pack(side="left", padx=5)

def vista_historial_ventas():
    for widget in contenedor_dinamico.winfo_children(): widget.destroy()
    ttk.Label(contenedor_dinamico, text="📋 HISTORIAL DE VENTAS", font=("Arial", 16, "bold")).pack(pady=10)

    if not ventas:
        ttk.Label(contenedor_dinamico, text="No hay ventas registradas.").pack(pady=30)
        return

    columnas = ("codigo", "producto", "cantidad", "total")
    tabla = ttk.Treeview(contenedor_dinamico, columns=columnas, show="headings", height=8)
    headers = {"codigo": "Código", "producto": "Producto", "cantidad": "Cantidad", "total": "Total"}
    
    for col in columnas:
        tabla.heading(col, text=headers[col])

    for v in ventas:
        tabla.insert("", "end", values=(v["codigo"], v["nombre"], v["cantidad"], f"Q{v['total']:.2f}"))

    tabla.pack(fill="both", expand=True, pady=10)

def mostrar_estadisticas():
    for widget in contenedor_dinamico.winfo_children(): widget.destroy()
    ingresos = sum(v["total"] for v in ventas)
    unidades = sum(v["cantidad"] for v in ventas)
    
    cantidades = {}
    for v in ventas:
        cantidades[v["nombre"]] = cantidades.get(v["nombre"], 0) + v["cantidad"]
    
    mayor_prod = max(cantidades, key=cantidades.get) if cantidades else "Ninguno"
    menor_stock = min(productos, key=lambda x: x["stock"]) if productos else None

    texto = (
        f"📊 ESTADÍSTICAS GENERALES DE SPORTZONE\n\n"
        f"• Productos en catálogo: {len(productos)}\n"
        f"• Compras de clientes realizadas: {len(ventas)}\n"
        f"• Unidades totales vendidas: {unidades}\n"
        f"• Ingresos totales generados: Q{ingresos:.2f}\n\n"
        f"⭐ Producto más vendido: {mayor_prod}\n"
    )
    if menor_stock:
        texto += f"⚠️ Alerta Stock Bajo: {menor_stock['nombre']} ({menor_stock['stock']} un.)"

    ttk.Label(contenedor_dinamico, text=texto, font=("Arial", 13), justify="left").pack(pady=20)

def vista_ordenar():
    for widget in contenedor_dinamico.winfo_children(): widget.destroy()
    ttk.Label(contenedor_dinamico, text="🔃 ORDENAR INVENTARIO", font=("Arial", 16, "bold")).pack(pady=15)

    def burbuja(criterio, clave):
        n = len(productos)
        for i in range(n - 1):
            for j in range(n - 1 - i):
                v1, v2 = productos[j][criterio], productos[j+1][criterio]
                if isinstance(v1, str): v1, v2 = v1.lower(), v2.lower()
                if v1 > v2:
                    productos[j], productos[j+1] = productos[j+1], productos[j]
        messagebox.showinfo("Éxito", f"Inventario ordenado por {clave}.")
        mostrar_tabla_productos_admin(productos, f"INVENTARIO ORDENADO POR {clave.upper()}")

    ttk.Button(contenedor_dinamico, text="Ordenar por Precio", command=lambda: burbuja("precio", "precio"), width=25).pack(pady=6)
    ttk.Button(contenedor_dinamico, text="Ordenar por Stock", command=lambda: burbuja("stock", "stock"), width=25).pack(pady=6)
    ttk.Button(contenedor_dinamico, text="Ordenar por Nombre", command=lambda: burbuja("nombre", "nombre"), width=25).pack(pady=6)

# ==========================================================
#                   INICIAR APLICACIÓN
# ==========================================================
mostrar_inicio()
ventana.mainloop()
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import hashlib
import re
import random
import json
import os
from datetime import datetime
from fpdf import FPDF
from pathlib import Path

class Usuario:
    def __init__(self, id, nombre, apellido, username, password, edad, cedula, rol, numero_cuenta, saldo, tipo_cuenta):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.username = username
        self.password = password
        self.edad = edad
        self.cedula = cedula
        self.rol = rol
        self.numero_cuenta = numero_cuenta
        self.saldo = saldo
        self.tipo_cuenta = tipo_cuenta
        self.historial_transacciones = []

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'username': self.username,
            'password': self.password,
            'edad': self.edad,
            'cedula': self.cedula,
            'rol': self.rol,
            'numero_cuenta': self.numero_cuenta,
            'saldo': self.saldo,
            'tipo_cuenta': self.tipo_cuenta,
            'historial_transacciones': self.historial_transacciones
        }

# Update the SistemaAutenticacion class's registrar_usuario method
class SistemaAutenticacion:
    def __init__(self):
        self.usuarios = []
        self.cargar_usuarios()

    def cargar_usuarios(self):
        if os.path.exists('usuarios.json'):
            try:
                with open('usuarios.json', 'r') as f:
                    usuarios_data = json.load(f)
                    self.usuarios = [Usuario(**user_data) for user_data in usuarios_data]
            except:
                self.usuarios = []

    def guardar_usuarios(self):
        usuarios_data = [usuario.to_dict() for usuario in self.usuarios]
        with open('usuarios.json', 'w') as f:
            json.dump(usuarios_data, f)

    def generar_numero_cuenta(self):
        return ''.join([str(random.randint(0,9)) for _ in range(8)])

    def registrar_usuario(self, nombre, apellido, username, password, edad, cedula, tipo_cuenta):
        if edad < 18:
            return "Menor de edad"

        if not re.match(r'^\d{10}$', cedula):
            return "Cédula inválida"

        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$', nombre) or \
           not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$', apellido):
            return "Nombre y apellido deben contener solo letras"

        if any(usuario.cedula == cedula for usuario in self.usuarios):
            return "Cédula ya registrada"

        if len(password) < 8:
            return "Contraseña debe tener al menos 8 caracteres"

        while True:
            numero_cuenta = self.generar_numero_cuenta()
            if not any(usuario.numero_cuenta == numero_cuenta for usuario in self.usuarios):
                break

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        nuevo_usuario = Usuario(
            len(self.usuarios) + 1, 
            nombre, 
            apellido, 
            username, 
            password_hash, 
            edad, 
            cedula, 
            "cliente", 
            numero_cuenta,
            0,
            tipo_cuenta
        )
        self.usuarios.append(nuevo_usuario)
        self.guardar_usuarios()
        return nuevo_usuario

    def autenticar_usuario(self, cedula, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        for usuario in self.usuarios:
            if usuario.cedula == cedula and usuario.password == password_hash:
                return usuario
        return None

class InterfazBancaria:
    def __init__(self, usuario, sistema_autenticacion):
        self.usuario = usuario
        self.sistema_autenticacion = sistema_autenticacion
        self.ventana_bancaria = tk.Tk()
        self.ventana_bancaria.title(f"Banca en Línea - {usuario.nombre} {usuario.apellido}")
        self.ventana_bancaria.geometry("500x700")
        self.ventana_bancaria.configure(bg='#f0f0f0')

        frame_principal = tk.Frame(self.ventana_bancaria, bg='#f0f0f0')
        frame_principal.pack(pady=20, padx=20, fill='both', expand=True)

        tk.Label(frame_principal, text=f"Bienvenido/a {usuario.nombre} {usuario.apellido}", 
                 font=('Arial', 16, 'bold'), bg='#f0f0f0').pack(pady=(0,10))
        
        tk.Label(frame_principal, text=f"Número de Cuenta: {usuario.numero_cuenta}", 
                 font=('Arial', 12), bg='#f0f0f0').pack(pady=(0,10))
        
        self.label_saldo = tk.Label(frame_principal, 
                                    text=f"Saldo Actual: ${usuario.saldo:,.2f}", 
                                    font=('Arial', 14, 'bold'), 
                                    bg='#f0f0f0', 
                                    fg='green')
        self.label_saldo.pack(pady=(0,20))

        estilo_boton = {
            'font': ('Arial', 10, 'bold'),
            'width': 30,
            'pady': 10,
            'bg': '#4CAF50',
            'fg': 'white'
        }

        botones = [
            ("Depositar", self.depositar),
            ("Retirar", self.retirar),
            ("Ver Historial", self.ver_historial),
            ("Transferencia", self.transferencia),
            ("Certificado Bancario", self.generar_certificado),
            ("Cerrar Sesión", self.cerrar_sesion)
        ]

        for texto, comando in botones:
            if texto == "Cerrar Sesión":
                boton = tk.Button(frame_principal, text=texto, command=comando, 
                                bg='#f44336', **{k: v for k, v in estilo_boton.items() if k != 'bg'})
            elif texto == "Certificado Bancario":
                boton = tk.Button(frame_principal, text=texto, command=comando,
                                bg='#2196F3', **{k: v for k, v in estilo_boton.items() if k != 'bg'})
            else:
                boton = tk.Button(frame_principal, text=texto, command=comando, **estilo_boton)
            boton.pack(pady=10)

    def generar_certificado(self):
     try:
       # Ruta de Descargas para Windows
       downloads_path = str(Path.home() / "Downloads")  
       
       # Generar nombre único para el certificado
       fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
       nombre_archivo = f"certificado_bancario_{self.usuario.cedula}_{fecha_actual}.pdf"
       ruta_completa = os.path.join(downloads_path, nombre_archivo)
        # Crear PDF
       pdf = FPDF()
       pdf.add_page()
        
        # Configurar fuente
       pdf.set_font('Arial', 'B', 16)
        
        # Título
       pdf.cell(0, 20, 'BANCO DEL CARIBE', 0, 1, 'C')
       pdf.set_font('Arial', '', 14)
       pdf.cell(0, 10, 'Certificado Bancario', 0, 1, 'C')
        
        # Espacio
       pdf.ln(10)
        
        # Fecha
       pdf.set_font('Arial', '', 12)
       fecha_texto = datetime.now().strftime("%d de %B del %Y")
       pdf.cell(0, 10, f'Fecha: {fecha_texto}', 0, 1, 'L')
        
        # Espacio
       pdf.ln(10)
        
        # Contenido
       pdf.set_font('Arial', '', 12)
       pdf.multi_cell(0, 10, 'Por medio de la presente, el BANCO DEL CARIBE certifica que:')
       pdf.ln(5)
        
       texto = (
            f"El/La Sr./Sra. {self.usuario.nombre} {self.usuario.apellido}, "
            f"identificado(a) con cédula número {self.usuario.cedula}, "
            f"es titular de la cuenta {self.usuario.tipo_cuenta} "
            f"N° {self.usuario.numero_cuenta} en nuestra institución.\n\n"
            f"La cuenta mencionada mantiene un saldo actual de "
            f"${self.usuario.saldo:,.2f} y se encuentra en estado activo."
        )
        
       pdf.multi_cell(0, 10, texto)
        
        # Espacio
       pdf.ln(10)
        
        # Texto adicional
       pdf.multi_cell(0, 10, 'Este certificado se expide a solicitud del interesado para los fines que considere pertinentes.')
        
        # Espacio para firma
       pdf.ln(20)
       pdf.cell(0, 10, '_____________________', 0, 1, 'L')
       pdf.cell(0, 10, 'Gerente General', 0, 1, 'L')
       pdf.cell(0, 10, 'Banco del Caribe', 0, 1, 'L')
        
        # Nota al pie
       pdf.set_font('Arial', 'I', 8)
       pdf.ln(10)
       pdf.cell(0, 10, 'Este documento es de carácter informativo y no representa un título valor.', 0, 1, 'L')
        
        # Guardar PDF en la carpeta de Descargas
       pdf.output(ruta_completa)

       messagebox.showinfo("Éxito",
                   f"Certificado bancario generado exitosamente.\n"
                   f"Guardado en: {ruta_completa}")
     except Exception as e:
        messagebox.showerror("Error", f"Error al generar el certificado: {str(e)}")

    def depositar(self):
        try:
            monto = simpledialog.askfloat("Depositar", "Ingrese el monto a depositar:", minvalue=0.01)
            if monto is not None:
                self.usuario.saldo += monto
                self.usuario.historial_transacciones.append({
                    'tipo': 'Depósito',
                    'monto': monto,
                    'fecha': datetime.now()
                })
                self.label_saldo.config(text=f"Saldo Actual: ${self.usuario.saldo:,.2f}")
                messagebox.showinfo("Éxito", f"Depósito de ${monto:,.2f} realizado correctamente")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def retirar(self):
        try:
            monto = simpledialog.askfloat("Retirar", "Ingrese el monto a retirar:", minvalue=0.01)
            if monto is not None:
                if monto <= self.usuario.saldo:
                    self.usuario.saldo -= monto
                    self.usuario.historial_transacciones.append({
                        'tipo': 'Retiro',
                        'monto': monto,
                        'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    self.label_saldo.config(text=f"Saldo Actual: ${self.usuario.saldo:,.2f}")
                    messagebox.showinfo("Éxito", f"Retiro de ${monto:,.2f} realizado correctamente")
                else:
                    messagebox.showerror("Error", "Saldo insuficiente")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ver_historial(self):
        if not self.usuario.historial_transacciones:
            messagebox.showinfo("Historial", "No hay transacciones")
            return

        ventana_historial = tk.Toplevel(self.ventana_bancaria)
        ventana_historial.title("Historial de Transacciones")
        ventana_historial.geometry("500x400")

        columnas = ('Tipo', 'Monto', 'Fecha')
        tree = ttk.Treeview(ventana_historial, columns=columnas, show='headings')
        
        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor='center')

        for transaccion in self.usuario.historial_transacciones:
            tree.insert('', 'end', values=(
                transaccion['tipo'], 
                f"${transaccion['monto']:,.2f}", 
                transaccion['fecha']
            ))

        tree.pack(padx=10, pady=10, fill='both', expand=True)

        tree.pack(padx=10, pady=10, fill='both', expand=True)

    def transferencia(self):
        try:
            monto = simpledialog.askfloat("Transferencia", "Ingrese el monto a transferir:", minvalue=0.01)
            cuenta_destino = simpledialog.askstring("Transferencia", "Ingrese el número de cuenta destino:")
            
            if monto is not None and cuenta_destino is not None:
                if monto <= self.usuario.saldo:
                    # En un sistema real, aquí se buscaría la cuenta de destino
                    self.usuario.saldo -= monto
                    self.usuario.historial_transacciones.append({
                        'tipo': 'Transferencia',
                        'monto': monto,
                        'cuenta_destino': cuenta_destino,
                        'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    self.label_saldo.config(text=f"Saldo Actual: ${self.usuario.saldo:,.2f}")
                    messagebox.showinfo("Éxito", f"Transferencia de ${monto:,.2f} realizada correctamente")
                else:
                    messagebox.showerror("Error", "Saldo insuficiente")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def cerrar_sesion(self):
        self.ventana_bancaria.destroy()
        login = InterfazLogin(self.sistema_autenticacion)
        login.ventana_login.mainloop()

class InterfazRegistro:
    def __init__(self, sistema_autenticacion, ventana_login):
        self.sistema_autenticacion = sistema_autenticacion
        self.ventana_login = ventana_login
        self.ventana_registro = tk.Toplevel(ventana_login)
        self.ventana_registro.title("Registro de  nuevo usuario")
        self.ventana_registro.geometry("330x635")  # Aumentado para el nuevo campo
        self.ventana_registro.configure(bg='#F5DEB3')

        # Frame principal
        frame_principal = tk.Frame(self.ventana_registro, bg='#F5DEB3')
        frame_principal.pack(pady=20, padx=20, fill='both', expand=True)

        # Estilo para etiquetas y entradas
        estilo_label = {'bg': '#F5DEB3', 'font': ('Arial', 10)}
        estilo_entry = {'font': ('Arial', 10), 'width': 40, 'bd': 2, 'relief': 'groove'}

        # Título
        tk.Label(frame_principal, text="Registro de nuevo usuario", 
                 font=('Arial', 16, 'bold'), bg='#F5DEB3').pack(pady=(0,20))

        # Nombre
        tk.Label(frame_principal, text="Dos nombres:", **estilo_label).pack(anchor='w')
        self.nombre_entry = tk.Entry(frame_principal, **estilo_entry)
        self.nombre_entry.pack(pady=(0,10))

        # Apellido
        tk.Label(frame_principal, text="Dos apellidos:", **estilo_label).pack(anchor='w')
        self.apellido_entry = tk.Entry(frame_principal, **estilo_entry)
        self.apellido_entry.pack(pady=(0,10))

        # Username
        tk.Label(frame_principal, text="Nombre de usuario(ponga su nombre y apellido):", **estilo_label).pack(anchor='w')
        self.username_entry = tk.Entry(frame_principal, **estilo_entry)
        self.username_entry.pack(pady=(0,10))

        # Edad
        tk.Label(frame_principal, text="Edad:", **estilo_label).pack(anchor='w')
        self.edad_entry = tk.Entry(frame_principal, **estilo_entry)
        self.edad_entry.pack(pady=(0,10))

        # Cédula
        tk.Label(frame_principal, text="Cedula 10 digitos:", **estilo_label).pack(anchor='w')
        self.cedula_entry = tk.Entry(frame_principal, **estilo_entry)
        self.cedula_entry.pack(pady=(0,10))

        # Contraseña
        tk.Label(frame_principal, text="Contraseña:", **estilo_label).pack(anchor='w')
        self.password_entry = tk.Entry(frame_principal, show="*", **estilo_entry)
        self.password_entry.pack(pady=(0,10))

        # Tipo de Cuenta
        tk.Label(frame_principal, text="Tipo de cuenta que desea:", **estilo_label).pack(anchor='w')
        self.tipo_cuenta_var = tk.StringVar(value="Ahorro")
        frame_tipo_cuenta = tk.Frame(frame_principal, bg='#F5DEB3')
        frame_tipo_cuenta.pack(pady=(0,10))
        
        tk.Radiobutton(frame_tipo_cuenta, 
                      text="Cuenta de Ahorro", 
                      variable=self.tipo_cuenta_var, 
                      value="Ahorro",
                      bg='#f0f0f0').pack(side='left', padx=20)
        
        tk.Radiobutton(frame_tipo_cuenta, 
                      text="Cuenta Corriente", 
                      variable=self.tipo_cuenta_var, 
                      value="Corriente",
                      bg='#f0f0f0').pack(side='left')

        # Botones con estilo
        frame_botones = tk.Frame(frame_principal, bg='#f0f0f0')
        frame_botones.pack(pady=20)

        boton_registrar = tk.Button(frame_botones, text="Registrarse", 
                                    command=self.registrar, 
                                    bg='#90EE90', 
                                    fg='white', 
                                    font=('Verdana', 10, 'bold'),
                                    padx=20, 
                                    pady=10)
        boton_registrar.pack(side='left', padx=10)

        boton_cancelar = tk.Button(frame_botones, text="Cancelar", 
                                   command=self.ventana_registro.destroy, 
                                   bg='#FF0000', 
                                   fg='white', 
                                   font=('Verdana', 10, 'bold'),
                                   padx=20, 
                                   pady=10)
        boton_cancelar.pack(side='left')

    def registrar(self):
        nombre = self.nombre_entry.get().strip()
        apellido = self.apellido_entry.get().strip()
        username = self.username_entry.get().strip()
        edad = self.edad_entry.get().strip()
        cedula = self.cedula_entry.get().strip()
        password = self.password_entry.get()
        tipo_cuenta = self.tipo_cuenta_var.get()

        # Validar campos
        try:
            edad_int = int(edad)
            nuevo_usuario = self.sistema_autenticacion.registrar_usuario(
                nombre, apellido, username, password, edad_int, cedula, tipo_cuenta)
            
            if isinstance(nuevo_usuario, Usuario):
                # Mostrar número de cuenta
                messagebox.showinfo("Registro Exitoso", 
                                    f"Usuario registrado exitosamente.\n\n"
                                    f"Tu número de cuenta es: {nuevo_usuario.numero_cuenta}\n"
                                    f"Tipo de cuenta: {nuevo_usuario.tipo_cuenta}")
                self.ventana_registro.destroy()
                self.ventana_login.deiconify()
            else:
                messagebox.showerror("Error", nuevo_usuario)  # Muestra el mensaje de error específico
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese datos válidos:\n- Edad debe ser un número")

class InterfazLogin:
    def __init__(self, sistema_autenticacion):
        self.sistema_autenticacion = sistema_autenticacion
        self.ventana_login = tk.Tk()
        self.ventana_login.title("Iniciar Sesión")
        self.ventana_login.geometry("400x500")
        self.ventana_login.configure(bg='#F5DEB3')

        frame_principal = tk.Frame(self.ventana_login, bg='#F5DEB3')
        frame_principal.pack(pady=50, padx=30, fill='both', expand=True)

        tk.Label(frame_principal, text="🌴Banco del caribe🌴", 
                 font=('Helvica', 16, 'italic'), bg='#F5DEB3').pack(pady=(0,30))

        tk.Label(frame_principal, text="Cédula:", bg='#F5DEB3', font=('Arial', 10)).pack(anchor='w')
        self.cedula_entry = tk.Entry(frame_principal, width=40, font=('Arial', 10), bd=2, relief='groove')
        self.cedula_entry.pack(pady=(0,10))

        tk.Label(frame_principal, text="Contraseña:", bg='#F5DEB3', font=('Arial', 10)).pack(anchor='w')
        self.password_entry = tk.Entry(frame_principal, show="*", width=40, font=('Arial', 10), bd=2, relief='groove')
        self.password_entry.pack(pady=(0,20))

        boton_login = tk.Button(frame_principal, text="Iniciar Sesión", 
                                command=self.login, 
                                bg='#002F6C', 
                                fg='white', 
                                font=('Verdana', 10, 'bold'),
                                padx=20, 
                                pady=10)
        boton_login.pack(pady=(0,10))

        boton_registro = tk.Button(frame_principal, text="Registrarse", 
                                   command=self.abrir_registro, 
                                   bg='#4FC3F7', 
                                   fg='white', 
                                   font=('Verdana', 10, 'bold'),
                                   padx=20, 
                                   pady=10)
        boton_registro.pack()

    def login(self):
        cedula = self.cedula_entry.get()
        password = self.password_entry.get()

        usuario = self.sistema_autenticacion.autenticar_usuario(cedula, password)
        if usuario:
            self.ventana_login.destroy()
            interfaz_bancaria = InterfazBancaria(usuario, self.sistema_autenticacion)
            interfaz_bancaria.ventana_bancaria.mainloop()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    def abrir_registro(self):
        self.ventana_login.withdraw()
        registro = InterfazRegistro(self.sistema_autenticacion, self.ventana_login)
        registro.ventana_registro.mainloop()
def main():
    sistema_autenticacion = SistemaAutenticacion()
    login = InterfazLogin(sistema_autenticacion)
    login.ventana_login.mainloop()
if __name__ == "__main__":
    main()

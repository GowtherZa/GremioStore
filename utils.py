from telebot import types
from functions import *
from models import User

# ☑️ ✅ 🛒 ➡️ ⬅️ ↩️ 💰 Editar *️⃣  Eliminar ❌

def get_botonera_inicial():
      markup = types.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)
      maderatosButton = types.KeyboardButton('Maderatos 🌴')
      maceticasButton = types.KeyboardButton('Maceticas 🎍')
      markup.row(maderatosButton,maceticasButton)
      return markup
      
def get_botonera_admin():
      markup = types.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)
      maderatosButton = types.KeyboardButton('Maderatos 🌴')
      maceticasButton = types.KeyboardButton('Maceticas 🎍')
      agregarButton = types.KeyboardButton("Agregar Producto ➕")
      markup.row(maderatosButton,maceticasButton)
      markup.row(agregarButton)
      return markup

def get_botonera_agregando_producto():
      markup = types.ReplyKeyboardMarkup(row_width=1,resize_keyboard=True)
      returnButton = types.KeyboardButton("Cancelar ↩️")
      markup.add(returnButton)
      return markup

def get_botonera_edicion_producto():

      markup = types.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)

      nombreButton = types.KeyboardButton("Nombre ✍️") 
      detallesButton = types.KeyboardButton ("Detalles 📋")
      precioButton = types.KeyboardButton("Precio 💰")
      fotoButton = types.KeyboardButton("Foto 🖼")
      returnButton = types.KeyboardButton("Regresar ↩️")

      markup.row(nombreButton,detallesButton)
      markup.row(precioButton,limiteButton)
      markup.row(fotoButton,returnButton)
      return markup
      
def get_productos_menu():
      comprarButton = types.KeyboardButton('Hacer compra 💰')
      carritoButton = types.KeyboardButton('Carrito 🛒')
      deshacerButton = types.KeyboardButton('Regresar ↩️')
      
      markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
      markup.row(comprarButton)
      markup.row(carritoButton,deshacerButton)

      return markup

def get_botonera_carrito():
      
      comprarButton = types.KeyboardButton('Hacer compra 💰')
      refrescarCarritoButton = types.KeyboardButton('Refrescar Carrito 🛒')
      vaciarCarritoButton = types.KeyboardButton('Vaciar carrito ♻️') 
      regresarButton = types.KeyboardButton('Regresar ↩️')
      
      markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
      markup.row(comprarButton,refrescarCarritoButton)
      markup.row(vaciarCarritoButton,regresarButton)

      return markup

def info_renovar_botonera():
      sms = '''```
   ⚠️Advertencia⚠️
El producto sobre el cual desea
consultar, ha sido renovado o eliminado
. Porfavor vuelva a consultar los productos
directamente desde las categorías.
      ```'''
      return sms

def info_producto_para_carrito(nombre,precio,cantidad):
      sms = f'''```
\n{cantidad}x {nombre} ({precio} cup c/u)```'''
      return sms

def get_botonera_cancelar(categorias):
      markup = types.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)
      if categorias:
            maderatosButton = types.KeyboardButton('Maderatos 🌴')
            maceticasButton = types.KeyboardButton('Maceticas 🎍')
            cancelarButton = types.KeyboardButton('Cancelar ↩️')
            markup.add(maderatosButton, maceticasButton,cancelarButton)
      else:
            cancelarButton = types.KeyboardButton('Cancelar ↩️')
            markup.add(cancelarButton)
      return markup

def get_inline_b(producto,user,len,cantidad,index,admin):

      keyboard = []

      # Buscamos la cantidad temporal, no real:
      # cantidad = cantidad_de_producto_en_carro_t(producto,user)

      # ide del producto
      p_id = producto.id

      categoria = producto.categoria

      length = get_cantidad_en_categoria(categoria) - 1

      print(f'Showing index :{index} , length: {length}')

      if cantidad > 0 :
            emoji_check = "✅"
      else:
            emoji_check = "☑️"

      emoji_carrito = "🛒"
      emoji_sgt = "➡️"
      emoji_ant = "⬅️"

      # agregando botonera
      comprarButton = types.InlineKeyboardButton(
                              text= f'Cantidad a comprar: {cantidad} {emoji_check}',
                              callback_data= f'charge_{p_id}_{cantidad}_{index}_{categoria}'
                        )

      descontar_carritoButton = types.InlineKeyboardButton(
                              text = f'Bajar una unidad {emoji_carrito}',
                              callback_data= f'reduce_{p_id}_{cantidad}_{index}_{categoria}'
                        )

      keyboard.append([comprarButton])
      keyboard.append([descontar_carritoButton])

      sgte = False
      ant = False

      if index < length:   
            sgte = True
      
      if index > 0 or (index == length and length!=0):
            ant = True
           
      arrows = []

      if ant :

            antButton = types.InlineKeyboardButton(
                        text = f'{emoji_ant}',
                        callback_data=f'prev_{index}_{categoria}'
                  )
            
            arrows.append(antButton)

      if sgte:

            sgteButton = types.InlineKeyboardButton(
                        text = f'{emoji_sgt}',
                        callback_data=f'next_{index}_{categoria}'
                  )
            
            arrows.append(sgteButton)
      
      if arrows != []:
            keyboard.append(arrows)      
  
      if admin:

            editarButton = types.InlineKeyboardButton(
                        text = f'Editar *️⃣',
                        callback_data=f'edit_{p_id}'
                  )
            
            eliminarButton = types.InlineKeyboardButton(
                  text = f'Eliminar ❌',
                  callback_data=f'delete_{p_id}'
            )

            keyboard.append([editarButton,eliminarButton])

      markup = types.InlineKeyboardMarkup(keyboard)
      markup.row_width = 2
      
      return markup 

def welcome_message():
      return '''```
      Hola! Bienvenido al bot no oficial y de pruebas de maderato!
    ```'''

def comandos_info():
      sms = '''
      ```
/decir <id> - <texto>  -> Envia el texto al usuario segun su id

/ban <id> -> Banea al usuario

/unban <id> -> Desbanea al usuario

/i_u <id> -> Inspecciona al usuario

/anunciar <texto> -> Envia el texto a todos los usuarios
      ```
      '''

      return sms

def hacer_sms_producto(producto):
      sms = f'''```
{producto.nombre}

{producto.detalles}

Precio: {producto.precio}cup
                        ```'''
      return sms
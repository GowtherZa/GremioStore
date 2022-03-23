from functions import *
import telebot
import telegram
import requests
import logging
from models import User, Producto, session
from utils import *
from telebot import types, util, apihelper
from datetime import datetime
import calendar
import schedule
import time
import threading
import os

# apihelper.SESSION_TIME_TO_LIVE = 5 * 60
bot_token = os.getenv("BOT")
bot = telebot.TeleBot(bot_token)
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
dev = int(os.getenv("DEV"))
owner = int(os.getenv("OWNER"))

####### Variables de ayuda ##############

utils = init_utils(dev,owner)
admins = get_admins()
dev = utils.dev
admins.append(dev)
owner = utils.owner
categorias = utils.categorias
p_mostrados = utils.p_mostrados
waiting = utils.response_waiting
session.close()
baneados = get_usuarios_baneados()
detalles_de_producto = utils.image_secs
###############################

# Valida el id del mensaje y dewelve la funcion si el id es el indicado
def is_admin(message):
    print(utils)
    if int(message.from_user.id) in admins:
        return True
    elif int(message.from_user.id) == dev:
        return True
    else:
        bot.send_message(message.from_user.id,"Usted no tiene los permisos suficientes.")
        return False

def is_dev(message):
    if message.from_user.id == dev:
        return True
    else:
        bot.send_message(message.from_user.id,"Usted no tiene los permisos suficientes.")
        return False

def is_not_baned(message):
    if message.from_user.id not in baneados:
        return True
    else:
        bot.send_message(message.from_user.id,"Lo sentimos, usted esta baneado de nuestro sistema.")
        return False

################# Comandos de dev ########################

@bot.message_handler(commands=['create_db'], func=is_dev)
def create_database(message):

    if is_msg_too_old(message,bot,waiting):
        return
    
    create_db()

@bot.message_handler(commands=['rollback_db'], func=is_dev)
def rollback_database(message):

    session.rollback()
    

@bot.message_handler(commands=['delete_db'], func=is_dev)
def delete_database(message):

    if is_msg_too_old(message,bot,waiting):
        return

    del_db()

@bot.message_handler(commands=['promote'], func=is_dev)
def set_admin(message):

    if is_msg_too_old(message,bot,waiting):
        return

    global admins
    sms = message.text.replace("/promote","")

    try:
        sms = int(sms)
    except ValueError:
        bot.send_message("Introduzca el id porfavor.")

    usuario = get_user_por_id(sms)
    
    if usuario != "El usuario no existe":
        usuario.admin = True
        session.commit()

        admins = get_admins()

        bot.send_message(usuario.tg_id,"Felicitaciones, usted ha sido promovido a admin 🎉.")
        bot.send_message(message.from_user.id,f'Usuario {usuario.tg_id} promovido (^w^)/')
    else:
        bot.send_message(message.from_user.id,"El usuario no existe.")

@bot.message_handler(commands=['demote'], func=is_dev)
def demote_admin(message):

    if is_msg_too_old(message,bot,waiting):
        return

    global admins
    sms = message.text.replace("/demote","")

    try:
        sms = int(sms)
    except ValueError:
        bot.send_message("Introduzca el id porfavor.")

    usuario = get_user_por_id(sms)
    if usuario != "El usuario no existe":
        if usuario == utils.dev or usuario == utils.owner:
            bot.send_message(usuario.tg_id,"Lo sentimos, usted ha sido degradado de sus permisos.")
        usuario.admin = False
        session.commit()

        admins = get_admins()

        bot.send_message(usuario.tg_id,"Lo sentimos, usted ha sido degradado de sus permisos.")
        bot.send_message(message.from_user.id,f'Usuario {usuario.tg_id} degradado (TwT)/')
    else:
        bot.send_message(message.from_user.id,"El usuario no existe.")
# _______________________________________________________#
################## ################## ###################

################ Comandos de admins ######################

@bot.message_handler(func=is_admin , commands=['anunciar'])
def anunciar(message):

    if is_msg_too_old(message,bot,waiting):
        return

    usuarios = get_usuarios()
    sms = message.text.replace("/anunciar","")
    for usuario in usuarios:
        try:
            bot.send_message(usuario.tg_id,sms)
        except:
            print(f'El usuario {usuario.tg_id} cerró el bot. No es posible contactarlo')
    bot.send_message(message.from_user.id,"Mensaje correctamente enviado")

@bot.message_handler(func=is_admin ,commands=['i_u'])
def inspeccionar_usuario(message):

    if is_msg_too_old(message,bot,waiting):
        return

    usuario = ""

    u_sms = message.text.replace("/i_u","")

    if u_sms == "":
        bot.send_message(message.from_user.id,"Debe introducir el id del usuario")
        return
    else:
        try:
            u_id = int(u_sms)
            usuario = get_user_por_id(u_id)  
        except ValueError as e:
            bot.send_message(message.from_user.id,"Debe introducir el id del usuario.")
        bot.send_message(message.from_user.id,usuario,parse_mode="MarkdownV2")
    
@bot.message_handler(func=is_admin ,commands=['unban'])
def unban(message):

    if is_msg_too_old(message,bot,waiting):
        return

    try:
        u_id = int(message.text.replace("/unban",""))
        usuario = get_user_por_id(u_id)
    except ValueError as e:
        bot.send_message(message.from_user.id,"Debe introducir el id del usuario.")
    if u_id == dev:
        bot.send_message(message.from_user.id,"¿Si? No me digas (≧▽≦)") 
    else:
        usuario.baneado = False
        session.commit()
        bot.send_message(message.from_user.id,f'Se desbaneo al usuario {usuario.tg_id}')

@bot.message_handler(func=is_admin ,commands=['ban'])
def ban(message):

    if is_msg_too_old(message,bot,waiting):
        return

    try:
        u_id = int(message.text.replace("/ban",""))
        usuario = get_user_por_id(u_id)
    except ValueError as e:
        bot.send_message(message.from_user.id,"Debe introducir el id del usuario.")
    if u_id == dev or u_id == owner:
        bot.send_message(message.from_user.id,"¿Si? No me digas (≧▽≦)") 
    else:
        usuario.baneado = True
        session.commit()
        bot.send_message(message.from_user.id,f'Se baneo al usuario {usuario.tg_id}')

@bot.message_handler(func=is_admin, commands=['decir'])
def decir(message):

    if is_msg_too_old(message,bot,waiting):
        return

    usuario = ""

    sms = message.text.replace("/decir","").split("-")
    if len(sms) != 2:
        bot.send_message(message.from_user.id,"El comando se usa de la siguiente manera: \n/decir <id> - <texto>.")
        return
    u_id = sms[0]
    u_sms = sms[1]
    found = True
    if u_sms == "":
        bot.send_message(message.from_user.id,"Debe introducir un texto para enviar.")
        return
    else:
        try:
            u_id = int(u_id)
            usuario = get_user_por_id(u_id)  
            bot.send_message(u_id,u_sms)
        except ValueError as e:
            bot.send_message(message.from_user.id,"Debe introducir el id del usuario.")
        except Exception as e:
            bot.send_message(message.from_user.id,"El usuario no existe o salió del bot.")
            found = False
        if found:
            bot.send_message(message.from_user.id,"Mensaje enviado.")

@bot.message_handler(func=is_admin, commands=['comandos'])
def comandos(message):

    if is_msg_too_old(message,bot,waiting):
        return

    sms = comandos_info()

    bot.send_message(message.from_user.id,sms,parse_mode="MarkdownV2")

@bot.message_handler(func=is_admin, commands=['limite'])
def set_limite(message):

    if is_msg_too_old(message,bot,waiting):
        return

    global p_mostrados
    sms = message.text.replace("/limite","")

    try:
        limite = int(sms)
    except ValueError:
        bot.send_message(message.from_user.id,"El límite debe ser un número.")
        return
    
    if limite <= 0:
        bot.send_message(message.from_user.id,"El límite debe ser un número positivo mayor que 0.")
        return

    utils = init_utils()
    utils.p_mostrados = limite

    session.commit()

    p_mostrados = limite
    bot.send_message(message.from_user.id,f"Limite establecido a {p_mostrados} productos")

@bot.message_handler(func=is_admin, commands=['waiting'])
def set_espera(message):
    global waiting

    if is_msg_too_old(message,bot,waiting):
        return

    sms = message.text.replace("/waiting","")

    try:
        waiting = int(sms)
    except ValueError:
        bot.send_message(message.from_user.id,"El límite debe ser un número.")
        return
    
    if limite <= 0:
        bot.send_message(message.from_user.id,"El límite debe ser un número positivo mayor que 0.")
        return

    utils = init_utils()
    utils.response_waiting = waiting

    session.commit()

    bot.send_message(message.from_user.id,f"Limite establecido a {waiting} segundos")
# _______________________________________________________#
################## ################## ###################


############### Respondiendo a usuarios #################

@bot.message_handler(commands=['start'])
def on_pm(message):
    bot.send_chat_action(message.from_user.id,'typing')

    if is_msg_too_old(message,bot,waiting):
        return

    usuario = get_user(message)
    if usuario.tg_id in admins or usuario.tg_id == dev:
       markup = get_botonera_admin()
    else:
       markup = get_botonera_inicial()  
    sms = welcome_message()
    bot.send_message(message.from_user.id,sms, reply_markup=markup,parse_mode="MarkdownV2")
    session.close()

@bot.message_handler(func=is_not_baned)
def validate(message):

    if is_msg_too_old(message,bot,waiting):
        return

    print(utils.categorias )
    if message.text in categorias:
    
        bot.send_chat_action(message.from_user.id,'typing')
    
        productos = get_productos_por_categoria(message.text)
        length = len(productos)

        if productos != []: 
            menu = get_productos_menu()
            empty_k = types.ReplyKeyboardRemove()
            msg = bot.send_message(message.from_user.id,"Productos disponibles:",reply_markup= menu)
            
            index = 0
            limit = p_mostrados
            for producto in productos:
                
                if limit == 0:
                    break

                sms = hacer_sms_producto(producto)

                user = get_user(message)

                ##### MARKED
                cantidad = get_deseo(producto,user).cantidad

                if user.tg_id in admins:
                    markup = get_inline_b(producto,user,length,cantidad,index,True)
                else:
                    markup = get_inline_b(producto,user,length,cantidad,index,False)

                index = index + 1

                photo = producto.imagen

                bot.send_photo(message.from_user.id,photo= photo, caption = sms,reply_markup=markup, parse_mode="MarkdownV2") 
                
                limit = limit - 1

        else:
            bot.send_message(message.from_user.id,"Por el momento no hay productos en esta categoria")

    elif "Agregar Producto ➕" in message.text:

        usuario = get_user(message)
        if usuario.tg_id in admins:
                markup = get_botonera_cancelar(False)
                question = bot.send_message(
                    message.from_user.id,
                    "Introduzca el nombre del producto a agregar",
                    reply_markup=markup
                    )
                bot.register_next_step_handler(question,procesar_producto)
        else:
            markup = get_botonera_agregando_producto()
            bot.send_message(message.from_user.id,"Usted no tiene los permisos suficientes.",reply_markup=markup)

    elif "Carrito 🛒" in message.text or "Refrescar Carrito 🛒" in message.text:

        bot.send_chat_action(message.from_user.id,'typing')
        user = get_user_por_id(message.from_user.id)

        if user.carrito:
                carrito = user.carrito
             

                sms = f'''```
Detalles - Precio

        ```'''
                monto = 0

                hay_producto = False

                for deseo in carrito:
                    if deseo.cantidad != 0:
                        hay_producto = True
                        nombre = deseo.producto.nombre
                        precio = deseo.producto.precio
                        cantidad = deseo.cantidad

                        monto = (cantidad*precio) + monto

                        info = info_producto_para_carrito(nombre,precio,cantidad)

                        sms = sms + info

                sms = sms + f'''
```\n\n TOTAL A PAGAR: 
{monto} cup + 25 cup de delivery
(Pueden no aparecer productos en caso de haberse 
agotado)
```'''
                markup = get_botonera_carrito()

                intro = '''```
A continuacion los productos de su carrito:
                ```'''

                if not hay_producto:
                    bot.send_message(message.from_user.id,"Su carrito está vacío.")
                    return

                bot.send_message(message.from_user.id,intro,parse_mode="MarkdownV2")

                bot.send_message(message.from_user.id,sms,parse_mode="MarkdownV2",reply_markup = markup)
        else:
            bot.send_message(message.from_user.id,"Su carrito está vacío.")
    
    elif "Regresar ↩️" in message.text or "Cancelar ↩️" in message.text:

        bot.send_chat_action(message.from_user.id,'typing')
        usuario = get_user(message)
        if usuario.tg_id in admins:
            markup = get_botonera_admin()
        else:
            markup = get_botonera_inicial() 
        bot.send_message(message.from_user.id,"Mostrando categorias",reply_markup = markup)

    elif "Vaciar carrito ♻️" in message.text:

        bot.send_chat_action(message.from_user.id,'typing')
        user = get_user_por_id(message.from_user.id)

        if user.carrito:
            user.carrito = []
            session.commit()
            bot.send_message(message.from_user.id,"Carrito vaciado con éxito.")
    
        else:
            bot.send_message(message.from_user.id,"Su carrito ya estaba vacío.")

    elif "Hacer compra 💰" in message.text:
        bot.send_chat_action(message.from_user.id,'typing')
        user = get_user_por_id(message.from_user.id)

        if user.carrito:
                carrito = user.carrito
                
                if user.alias:
                    intro_a =f'''```
El usuario @{user.alias} - {user.tg_id} desea hacer
una compra.
A continuacion los productos de su carrito:
                ```'''

                else:
                    intro_a =f'''```
El usuario {user.tg_id} desea hacer
una compra.
                ```'''

                intro_c = '''```
A continuacion los productos de su carrito:
                ```'''

                sms = f'''```
Detalles - Precio

        ```'''

                monto = 0

                hay_producto = False

                for deseo in carrito:
                    if deseo.cantidad != 0:
                        hay_producto = True
                        nombre = deseo.producto.nombre
                        precio = deseo.producto.precio
                        cantidad = deseo.cantidad

                        monto = (cantidad*precio) + monto

                        info = info_producto_para_carrito(nombre,precio,cantidad)

                        sms = sms + info

                if not hay_producto:
                    bot.send_message(message.from_user.id,"Su carrito está vacío.",parse_mode="MarkdownV2")
                    return
                
                # bot.send_message(owner,intro_a,parse_mode="MarkdownV2")
                bot.send_message(dev,intro_a,parse_mode="MarkdownV2")
                bot.send_message(message.from_user.id,intro_c,parse_mode="MarkdownV2")

                sms = sms + f'''
```\n\n TOTAL A PAGAR: 
{monto} cup + 25 cup de delivery

(Pueden no aparecer productos en caso de haberse 
agotado)

Su encargo ha sido realizado. Manténgase a la espera
mientras uno de nuestros administradores procesa su encargo
y le contacta.
```'''          

                sms_a = intro_c + sms

                if user.tg_id in admins:
                    markup = get_botonera_admin()
                else:
                    markup = get_botonera_inicial() 

                user.carrito = []
                session.commit()

                bot.send_message(dev,sms_a,parse_mode="MarkdownV2")
                bot.send_message(message.from_user.id,sms,parse_mode="MarkdownV2",reply_markup = markup)
        else:
            bot.send_message(message.from_user.id,"Su carrito está vacío.")

    else:
        bot.send_message(message.from_user.id,"No estoy seguro de que quieres que haga. Revisa bien lo que me dices.")

# _______________________________________________________#
################## ################## ###################


################## Respondiendo Callbacks ###############

@bot.callback_query_handler(func= lambda call:True)
def answer(call):

    if call.from_user.id not in baneados:
        if "charge" in call.data:
            bot.send_chat_action(call.from_user.id,'typing')
            print(call.data)

            data = call.data.replace("charge_","").split("_")
            p_id = int(data[0])
            cantidad = int(data[1])
            index = int(data[2])
            categoria = data[3]

            cantidad = cantidad + 1

            user = get_user_por_id(int(call.from_user.id))
            carrito = user.carrito

            productos = get_productos_por_categoria(categoria)
            try:         
                producto = productos[index]
            except IndexError as e:
                print(f'Error en linea 350: {e}')
                sms = info_renovar_botonera()
                if call.from_user.id in admins or call.from_user.id == dev:
                    markup = get_botonera_admin()
                else:
                    markup = get_botonera_inicial()
                bot.delete_message(call.message.chat.id, call.message.id, timeout=None)
                bot.send_message(call.from_user.id,sms,parse_mode="MarkdownV2")
                return

            # if cantidad > producto.limite:
            #     bot.answer_callback_query(callback_query_id = call.id, text="No se puede comprar más.")
            #     return
            
            # limite_producto = producto.limite

            deseo = get_deseo(producto,user)

            print("Deseo:")
            print(deseo)

#             deseo_cantidad = deseo.cantidad

#             agrego = deseo_cantidad + cantidad

            # if cantidad > limite_producto:
            #     bot.answer_callback_query(callback_query_id = call.id, text="Aténgase al limite por favor")
            #     return 

            # else:
                
            #     deseo.cantidad = cantidad
            #     session.commit()

            deseo.cantidad = cantidad
            session.commit()

            # # y ya se habia encargado el limite
            # if deseo_cantidad == limite_producto:
            #     bot.answer_callback_query(callback_query_id = call.id, text="Aténgase al limite por favor")

            # # y se quiere ordenar el limite
            # elif cantidad == limite_producto:
            #     deseo.cantidad = cantidad
            #     session.commit() 

            # # y aun se puede desear mas de lo deseado
            # elif agrego < limite_producto:
            #     deseo.cantidad = agrego
            #     session.commit()

            # # y se quiere ordenar más del limite
            # elif agrego >= limite_producto:
            #     deseo.cantidad = limite_producto
            #     bot.answer_callback_query(callback_query_id = call.id, text="Se le ha agregado sólo hasta el límite disponible.")
            #     session.commit()
            
            length = len(productos)

            if user.tg_id in admins:
                    markup = get_inline_b(producto,user,length,cantidad,index,True)
            else:
                    markup = get_inline_b(producto,user,length,cantidad,index,False)

            photo = producto.imagen
            sms = hacer_sms_producto(producto)

            media = types.InputMediaPhoto(photo)
            media.caption = sms
            media.parse_mode = "MarkdownV2"

            bot.edit_message_media(media, chat_id = call.from_user.id, message_id= call.message.id,reply_markup= markup)
            bot.answer_callback_query(callback_query_id = call.id, text="Productos agregados al carrito.")

        if "next" in call.data:
            bot.send_chat_action(call.from_user.id,'typing')
            print(call.data)
        
            msg = call.data.replace("next_","").split("_")
            
            index = int(msg[0])
            index = index + 1

            categoria = msg[1]

            productos = get_productos_por_categoria(categoria)
            try:         
                producto = productos[index]
            except IndexError as e:
                print(f'Error en linea 350: {e}')
                sms = info_renovar_botonera()
                if call.from_user.id in admins or call.from_user.id == dev:
                    markup = get_botonera_admin()
                else:
                    markup = get_botonera_inicial()
                bot.delete_message(call.message.chat.id, call.message.id, timeout=None)
                bot.send_message(call.from_user.id,sms,parse_mode="MarkdownV2")
                return

            user = get_user_por_id(int(call.from_user.id))
            print(user)
            length = len(productos)

            # MARKED
            cantidad = get_deseo(producto,user).cantidad
            
            if user.tg_id in admins:
                    markup = get_inline_b(producto,user,length,cantidad,index,True)
            else:
                    markup = get_inline_b(producto,user,length,cantidad,index,False)

            photo = producto.imagen
            print("Im here")
            sms = hacer_sms_producto(producto)

            media = types.InputMediaPhoto(photo)
            media.caption = sms
            media.parse_mode = "MarkdownV2"

            bot.edit_message_media(media, chat_id = call.from_user.id, message_id= call.message.id,reply_markup= markup)
            bot.answer_callback_query(callback_query_id = call.id, text="Siguiente")

        if "prev" in call.data:
            bot.send_chat_action(call.from_user.id,'typing')
            print(call.data)
        
            msg = call.data.replace("prev_","").split("_")
            
            index = int(msg[0])
            index = index - 1

            categoria = msg[1]

            productos = get_productos_por_categoria(categoria)
            try:         
                producto = productos[index]
            except IndexError as e:
                print(f'Error en linea 684: {e}')
                sms = info_renovar_botonera()
                if call.from_user.id in admins or call.from_user.id == dev:
                    markup = get_botonera_admin()
                else:
                    markup = get_botonera_inicial()
                bot.delete_message(call.message.chat.id, call.message.id, timeout=None)
                bot.send_message(call.from_user.id,sms,parse_mode="MarkdownV2")
                return

            user = get_user_por_id(int(call.from_user.id))
            print(user)
            length = len(productos)

            cantidad = get_deseo(producto,user).cantidad
            
            if user.tg_id in admins:
                    markup = get_inline_b(producto,user,length,cantidad,index,True)
            else:
                    markup = get_inline_b(producto,user,length,cantidad,index,False)

            photo = producto.imagen
            print("Im here")
            sms = hacer_sms_producto(producto)

            media = types.InputMediaPhoto(photo)
            media.caption = sms
            media.parse_mode = "MarkdownV2"

            bot.edit_message_media(media, chat_id = call.from_user.id, message_id= call.message.id,reply_markup= markup)
            bot.answer_callback_query(callback_query_id = call.id, text="Anterior")


        if "reduce" in call.data:
            bot.send_chat_action(call.from_user.id,'typing')
            print(call.data)

            data = call.data.replace("reduce_","").split("_")
            print(data)
            p_id = int(data[0])
            cantidad = int(data[1])
            index = int(data[2])
            categoria = data[3]

            if cantidad <= 0:
                bot.answer_callback_query(callback_query_id = call.id, text="Usted no tiene este producto en el carrito.")
                return

            user = get_user_por_id(int(call.from_user.id))
            carrito = user.carrito

            productos = get_productos_por_categoria(categoria)
            try:         
                producto = productos[index]
            except IndexError as e:
                print(f'Error en linea 350: {e}')
                sms = info_renovar_botonera()
                if call.from_user.id in admins or call.from_user.id == dev:
                    markup = get_botonera_admin()
                else:
                    markup = get_botonera_inicial()
                bot.delete_message(call.message.chat.id, call.message.id, timeout=None)
                bot.send_message(call.from_user.id,sms,parse_mode="MarkdownV2")
                return
            id_producto = producto.id

            deseo = existe_deseo(producto,user)

            if deseo:
                print("Deseo:")
                print(deseo)

                deseo.cantidad = deseo.cantidad - 1
                cantidad = deseo.cantidad

                if deseo.cantidad == 0:
                    session.delete(deseo)

                session.commit()

                user = get_user_por_id(int(call.from_user.id))
                print(user)
                length = len(productos)
                
                if user.tg_id in admins:
                        markup = get_inline_b(producto,user,length,deseo.cantidad,index,True)
                else:
                        markup = get_inline_b(producto,user,length,deseo.cantidad,index,False)

                photo = producto.imagen
                print("Im here")
                sms = hacer_sms_producto(producto)

                media = types.InputMediaPhoto(photo)
                media.caption = sms
                media.parse_mode = "MarkdownV2"

                bot.edit_message_media(media, chat_id = call.from_user.id, message_id= call.message.id,reply_markup= markup)

                bot.answer_callback_query(callback_query_id = call.id, text="Se bajó un producto de su carrito.")
            else:
                bot.answer_callback_query(callback_query_id = call.id, text="Usted no tiene este producto en el carrito.")

        if "edit" in call.data:
            bot.send_chat_action(call.from_user.id,'typing')
            data = call.data.replace("edit_","")
            
            p_id = int(data)
            producto = get_producto_por_id(p_id)
            
            if producto == "None":
                # NO HAY PRODUCTO ////////// HAy que hacer
                bot.answer_callback_query(callback_query_id= call.id, text= "El producto no existe o fue movido.")
                sms = info_renovar_botonera()
                if call.from_user.id in admins or call.from_user.id == dev:
                    markup = get_botonera_admin()
                else:
                    markup = get_botonera_inicial()
                bot.delete_message(call.message.chat.id, call.message.id, timeout=None)
                bot.send_message(call.from_user.id,sms,parse_mode="MarkdownV2")
                return 
                
            bot.answer_callback_query(callback_query_id = call.id, text="Procediendo a editar el producto")

            markup = get_botonera_edicion_producto()

            question = bot.send_message(call.from_user.id,"Seleccione la sección a editar:",reply_markup = markup)
            bot.register_next_step_handler(question,procesar_edicion_producto,producto)

        if "delete" in call.data:
            print(call.data)
            bot.send_chat_action(call.from_user.id,'typing')
            data = call.data.replace("delete_","")
            
            p_id = int(data)
            producto = get_producto_por_id(p_id)
            
            if producto == "None":
                # NO HAY PRODUCTO ////////// Hay que hacer
                sms = info_renovar_botonera()
                if call.from_user.id in admins or call.from_user.id == dev:
                    markup = get_botonera_admin()
                else:
                    markup = get_botonera_inicial()
                bot.delete_message(call.message.chat.id, call.message.id, timeout=None)
                bot.send_message(call.from_user.id,sms,parse_mode="MarkdownV2")
                return

            bot.answer_callback_query(callback_query_id = call.id, text="Procediendo a borrar el producto")
            del_producto(producto)
            bot.delete_message(call.message.chat.id, call.message.id, timeout=None)

    else:
        bot.answer_callback_query(callback_query_id = call.id, text="Usuario baneado.")

# _______________________________________________________#
################## ################## ###################



################## Agregando Producto ###################

def procesar_producto(message):
    bot.send_chat_action(message.from_user.id,'typing')
    markup = get_botonera_cancelar(False)
    if message.text == None or message.text == "":
        question = bot.send_message(message.from_user.id,"Porfavor introduzca el nombre del producto a agregar",reply_markup= markup)
        bot.register_next_step_handler(question,procesar_producto)
    else:
        producto = get_producto(message)
        if "Cancelar ↩️" in message.text:
            cancelar_procesamiento(message,producto)
            return
        question = bot.send_message(message.from_user.id,"Introduzca los detalles del producto",producto,reply_markup =markup)
        bot.register_next_step_handler(question,procesar_detalles_producto,producto)

def procesar_detalles_producto(message,producto):
    if "Cancelar ↩️" in message.text:
        cancelar_procesamiento(message,producto)
        return
    bot.send_chat_action(message.from_user.id,'typing')
    markup = get_botonera_cancelar(False)
    if message.text == None or message.text == "":

        question = bot.send_message(message.from_user.id,"Porfavor introduzca los detalles del producto",reply_markup= markup)
        bot.register_next_step_handler(question,procesar_detalles_producto,producto)

    else:

        detalles = message.text
        producto.detalles = detalles

        question = bot.send_message(message.from_user.id,"Introduzca el precio del producto",reply_markup = markup)
        bot.register_next_step_handler(question,procesar_precio_producto,producto)

def procesar_precio_producto(message,producto):
    if "Cancelar ↩️" in message.text:
        cancelar_procesamiento(message,producto)
        return
    bot.send_chat_action(message.from_user.id,'typing')
    markup = get_botonera_cancelar(True)

    if message.text == None or message.text == "":

        question = bot.send_message(message.from_user.id,"Porfavor introduzca el precio del producto",reply_markup = markup)
        bot.register_next_step_handler(question,procesar_precio_producto,producto)

    else:

        try:

            precio = int(message.text)

        except ValueError as e:

            print(e)
            question = bot.send_message(message.from_user.id,"Porfavor introduzca el precio del producto",reply_markup = markup)
            bot.register_next_step_handler(question,procesar_precio_producto,producto)
            return

        except Exception as e:
            print(f'Error: [{e}]')
            question = bot.send_message(message.from_user.id,"Porfavor introduzca el precio del producto. Secciorese de introducir un numero")
            bot.register_next_step_handler(question,procesar_detalles_producto)
            return

        producto.precio = precio

        question = bot.send_message(message.from_user.id,"Introduzca la categoria del producto", reply_markup=markup)
        bot.register_next_step_handler(question,procesar_categoria_producto,producto)

def procesar_categoria_producto(message,producto):
    if "Cancelar ↩️" in message.text:
        cancelar_procesamiento(message,producto)
        return
    bot.send_chat_action(message.from_user.id,'typing')
    markup = get_botonera_cancelar(False)
    if message.text not in categorias:
        if_error_markup = get_botonera_cancelar(True)
        question = bot.send_message(message.from_user.id,"Porfavor seleccione la categoria del producto",reply_markup = if_error_markup)
        bot.register_next_step_handler(question,procesar_categoria_producto,producto)
    else:
        categoria = message.text
        producto.categoria = categoria

        question = bot.send_message(message.from_user.id,"Envie la imagen del producto",reply_markup = markup)
        bot.register_next_step_handler(question,procesar_imagen_producto,producto)

# def procesar_limite_producto(message,producto):
#     if "Cancelar ↩️" in message.text:
#         cancelar_procesamiento(message,producto)
#         return
#     bot.send_chat_action(message.from_user.id,'typing')
#     markup = get_botonera_cancelar(False)
#     try:

#         limite = int(message.text)

#     except ValueError as e:

#         print(e)
#         question = bot.send_message(message.from_user.id,"Porfavor introduzca el limite del producto",reply_markup = markup)
#         bot.register_next_step_handler(question,procesar_limite_producto,producto)
#         return

#     producto.limite = limite
#     question = bot.send_message(message.from_user.id,"Envie la foto del producto",reply_markup = markup)
#     bot.register_next_step_handler(question,procesar_imagen_producto,producto)

def procesar_imagen_producto(message,producto):
    if message.text:
        if "Cancelar ↩️" in message.text:
            cancelar_procesamiento(message,producto)
            return
    bot.send_chat_action(message.from_user.id,'typing')
    print("Entered image processing")
    if not message.photo:
        markup = get_botonera_cancelar(False)
        question = bot.send_message(message.from_user.id,"Porfavor envie la foto del producto",reply_markup = markup)
        bot.register_next_step_handler(question,procesar_detalles_producto)
    else:
        print("Photo array:")
        print(message.photo[0])
        photo = message.photo[0]
        
        producto.imagen = photo.file_id

        session.add(producto)
        session.commit()

        markup = get_botonera_admin()

        bot.send_message(message.from_user.id,f'Producto agregado: \n {producto}',reply_markup = markup)

def cancelar_procesamiento(message,producto):
    bot.send_chat_action(message.from_user.id,'typing')
    usuario = get_user(message)
    if usuario.tg_id in admins:
        markup = get_botonera_admin()
    else:
        markup = get_botonera_inicial() 
    bot.send_message(message.from_user.id,"Mostrando categorias",reply_markup = markup)


# ___________________________________________________#
################## ############### ###################

################## Editando Producto ###################

def procesar_edicion_producto(message,producto):
    bot.send_chat_action(message.from_user.id,'typing')
    markup = get_botonera_cancelar(False)
    # Nombre ✍️ Detalles 📋 Precio 💰 Limite 📦 Foto 🖼 Regresar ↩️
    if "Regresar ↩️" in message.text:
        bot.send_chat_action(message.from_user.id,'typing')
        usuario = get_user(message)
        if usuario.tg_id in admins:
            markup = get_botonera_admin()
        else:
            markup = get_botonera_inicial() 
        bot.send_message(message.from_user.id,"Mostrando categorias",reply_markup = markup)
        return
    if "Nombre ✍️" in message.text:
        question = bot.send_message(message.from_user.id,"Introduzca el nuevo nombre del producto",reply_markup = markup)
        bot.register_next_step_handler(question,procesar_edicion_nombre_producto,producto)
    if "Detalles 📋" in message.text:
        question = bot.send_message(message.from_user.id,"Introduzca los nuevos detalles del producto",reply_markup = markup)
        bot.register_next_step_handler(question,procesar_edicion_detalles_producto,producto)
    if "Precio 💰" in message.text:
        question = bot.send_message(message.from_user.id,"Introduzca el nuevo precio del producto",reply_markup = markup)
        bot.register_next_step_handler(question,procesar_edicion_precio_producto,producto)
    # if "Limite 📦" in message.text:
    #     question = bot.send_message(message.from_user.id,"Introduzca el nuevo limite del producto",reply_markup = markup)
    #     bot.register_next_step_handler(question,procesar_edicion_limite_producto,producto)
    if "Foto 🖼" in message.text:
        question = bot.send_message(message.from_user.id,"Introduzca la nueva foto del producto",reply_markup = markup)
        bot.register_next_step_handler(question,procesar_edicion_imagen_producto,producto)
    
def procesar_edicion_nombre_producto(message,producto):
    if "Cancelar ↩️" in message.text:
        cancelar_edicion(message,producto)
        return
    bot.send_chat_action(message.from_user.id,'typing')
    markup = get_botonera_edicion_producto()
    if message.text == None or message.text == "" or message.text in detalles_de_producto:
        markup = get_botonera_edicion_producto()
        question = bot.send_message(message.from_user.id,"Porfavor introduzca los detalles del producto",reply_markup= markup)
        bot.register_next_step_handler(question,procesar_detalles_producto,producto)

    else:

        nombre = message.text
        producto.nombre= nombre

        session.commit()

        question = bot.send_message(message.from_user.id,"Seleccione la sección a editar:",reply_markup = markup)
        bot.register_next_step_handler(question,procesar_edicion_producto,producto)

def procesar_edicion_detalles_producto(message,producto):
    if "Cancelar ↩️" in message.text:
        cancelar_procesamiento(message,producto)
        return
    bot.send_chat_action(message.from_user.id,'typing')
    markup = get_botonera_edicion_producto()
    if message.text == None or message.text == "" or message.text in detalles_de_producto:
        
        markup = get_botonera_edicion_producto()
        question = bot.send_message(message.from_user.id,"Seleccione la sección a editar:",reply_markup= markup)
        bot.register_next_step_handler(question,procesar_detalles_producto,producto)

    else:

        detalles = message.text
        producto.detalles = detalles

        session.commit()

        question = bot.send_message(message.from_user.id,"Seleccione la sección a editar:",reply_markup = markup)
        bot.register_next_step_handler(question,procesar_edicion_producto,producto)

def procesar_edicion_precio_producto(message,producto):
    if "Cancelar ↩️" in message.text:
        cancelar_procesamiento(message,producto)
        return
    bot.send_chat_action(message.from_user.id,'typing')
    markup = get_botonera_edicion_producto()

    if message.text == None or message.text == "" or message.text in detalles_de_producto:

        markup = get_botonera_edicion_producto()
        question = bot.send_message(message.from_user.id,"Porfavor introduzca el precio del producto",reply_markup = markup)
        bot.register_next_step_handler(question,procesar_edicion_precio_producto,producto)

    else:

        try:

            precio = int(message.text)

        except ValueError as e:

            print(e)

            question = bot.send_message(message.from_user.id,"Porfavor introduzca el precio del producto",reply_markup = markup)
            bot.register_next_step_handler(question,procesar_edicion_precio_producto,producto)
            return

        except Exception as e:
            print(f'Error: [{e}]')
            question = bot.send_message(message.from_user.id,"Porfavor introduzca el precio del producto. Secciorese de introducir un número.",reply_markup = markup)
            bot.register_next_step_handler(question,procesar_edicion_precio_producto,producto)
            return

        producto.precio = precio

        session.commit()

        question = bot.send_message(message.from_user.id,"Seleccione la sección a editar:",reply_markup = markup)
        bot.register_next_step_handler(question,procesar_edicion_producto,producto)

def procesar_edicion_categoria_producto(message,producto):
    if "Cancelar ↩️" in message.text:
        cancelar_procesamiento(message,producto)
        return
    bot.send_chat_action(message.from_user.id,'typing')
    markup = get_botonera_edicion_producto()
    if message.text not in categorias:
        if_error_markup = get_botonera_cancelar(True)
        question = bot.send_message(message.from_user.id,"Porfavor seleccione la categoria del producto",reply_markup = if_error_markup)
        bot.register_next_step_handler(question,procesar_categoria_producto,producto)
    else:
        categoria = message.text
        producto.categoria = categoria

        session.commit()

        question = bot.send_message(message.from_user.id,"Seleccione la sección a editar:",reply_markup = markup)
        bot.register_next_step_handler(question,procesar_edicion_producto,producto)

# def procesar_edicion_limite_producto(message,producto):
#     if "Cancelar ↩️" in message.text:
#         cancelar_procesamiento(message,producto)
#         return
#     bot.send_chat_action(message.from_user.id,'typing')
#     markup = get_botonera_cancelar(False)
#     if message.text in detalles_de_producto:
#         question = bot.send_message(message.from_user.id,"Porfavor introduzca el limite del producto",reply_markup = markup)
#         bot.register_next_step_handler(question,procesar_limite_producto,producto)
#         return
#     try:

#         limite = int(message.text)

#     except ValueError as e:

#         print(e)
#         question = bot.send_message(message.from_user.id,"Porfavor introduzca el limite del producto",reply_markup = markup)
#         bot.register_next_step_handler(question,procesar_limite_producto,producto)
#         return

#     markup = get_botonera_edicion_producto()

#     producto.limite = limite
#     session.commit()

#     question = bot.send_message(message.from_user.id,"Seleccione la sección a editar:",reply_markup = markup)
#     bot.register_next_step_handler(question,procesar_edicion_producto,producto)

def procesar_edicion_imagen_producto(message,producto):
    if message.text:
        if "Cancelar ↩️" in message.text:
            cancelar_procesamiento(message,producto)
            return
    bot.send_chat_action(message.from_user.id,'typing')
    print("Entered image processing")
    if not message.photo:
        markup = get_botonera_edicion_producto()
        question = bot.send_message(message.from_user.id,"Porfavor envie la foto del producto",reply_markup = markup)
        bot.register_next_step_handler(question,procesar_edicion_producto,producto)
    else:
        print("Photo array:")
        print(message.photo[0])
        photo = message.photo[0]
        
        producto.imagen = photo.file_id

        markup = get_botonera_edicion_producto()
        session.commit()

        question = bot.send_message(message.from_user.id,"Seleccione la sección a editar:",reply_markup = markup)
        bot.register_next_step_handler(question,procesar_edicion_producto,producto)

def cancelar_edicion(message,producto):
    bot.send_chat_action(message.from_user.id,'typing')
    markup = get_botonera_edicion_producto()
    question = bot.send_message(message.from_user.id,"Operación cancelada. Seleccione la sección a editar:",reply_markup = markup)
    bot.register_next_step_handler(question, procesar_edicion_producto, producto)

# ___________________________________________________#
################## ############### ###################


######## Para mostrar señales y conocer en caso de apagarse #######

def inform():
    bot.send_message(dev,"I'm still working.")

def keep_informing():
    print("Thread on!")
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule.every().day.at("18:00").do(inform)

schedule.every().day.at("10:00").do(inform)

informer = threading.Thread(target=keep_informing)
informer.start()

######################################################


bot.infinity_polling(non_stop= True,allowed_updates=util.update_types)

schedule.run_pending()

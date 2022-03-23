
def procesar_imagen_producto(message,producto):
    bot.send_chat_action(message.from_user.id,'typing')
    print("Entered image processing")
    if not message.photo:
        question = bot.send_message(message.from_user.id,"Porfavor envie la foto del producto")
        bot.register_next_step_handler(question,procesar_detalles_producto)
    else:
        print("Photo array:")
        print(message.photo)

        photo = message.photo[0]
        print("Imagen on 0:")
        print(photo)


        imagen_producto = bot.get_file(photo.file_id)

        # file_producto = requests.get(f'https://api.telegram.org/file/bot{bot_token}/{imagen_producto.file_path}')
        downloaded = bot.download_file(imagen_producto.file_path)
        try:
            with store_context(store):
                f = open("temporal image","wb")
                f.write(downloaded)
                producto.imagen.from_file(f)
                f.close()
        except Exception:
            session.rollback()
            raise        
        session.commit()
        bot.send_message(message.from_user.id,f'Producto agregado: \n {producto}',reply_markup = markup)



Paso cuando melissa intento usar el bot estando apagado y lo encendi luego de recibir el sms

 #raise sa_exc.InvalidRequestError(
        #sqlalchemy.exc.InvalidRequestError: This session is in 'prepared' state; no further SQL can be emitted within this transaction.        
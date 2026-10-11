CABECERA = 'codigo;descripcion;cantidad;precio'


# Cada producto es una lista: código, descripción, cantidad y precio
# raise ValueError avisa que un dato es incorrecto  except muestra ese aviso
def validar(codigo, descripcion, cantidad, precio):
    codigo = str(codigo).strip().upper()
    descripcion = str(descripcion).strip()
    cantidad = str(cantidad).strip()
    precio = str(precio).strip().replace(',', '.')
    letras = codigo.replace('-', '').replace('_', '')
    if not codigo or len(codigo) > 30 or not codigo.isascii():
        raise ValueError('Código inválido.')
    if letras and not letras.isalnum():
        raise ValueError('Use letras, números, guion o guion bajo en el código.')
    if not descripcion or len(descripcion) > 120 or not descripcion.isprintable() or ';' in descripcion:
        raise ValueError('Descripción: 1 a 120 caracteres, sin punto y coma ni saltos de línea.')
    if not cantidad.isascii() or not cantidad.isdigit():
        raise ValueError('Cantidad: entero mayor o igual a cero.')
    partes = precio.split('.')
    if not precio.isascii() or not precio.replace('.', '', 1).isdigit():
        raise ValueError('Precio inválido.')
    if len(partes) == 2 and (not partes[0] or not partes[1] or len(partes[1]) > 2):
        raise ValueError('Precio: hasta dos decimales.')
    if float(precio) <= 0 or float(precio) == float('inf'):
        raise ValueError('El precio debe ser positivo y válido.')
    # int convierte la cantidad a entero; float convierte el precio a decimal.
    return [codigo, descripcion, int(cantidad), float(precio)]


def buscar(productos, codigo):
    codigo = str(codigo).strip().upper()
    for i in range(len(productos)):
        if productos[i][0] == codigo:
            return i
    return -1  


def cargar(ruta, permitir_ausente=True):
    productos = []
    try:
        archivo = open(ruta, 'r', encoding='utf-8-sig')
    except FileNotFoundError:
        if permitir_ausente:
            return []
        raise
    with archivo:
        if archivo.readline().strip() != CABECERA:
            raise ValueError('Cabecera incorrecta en el archivo.')
        for linea in archivo:
            fila = linea.strip().split(';')  # Separar los cuatro datos.
            if len(fila) != 4:
                raise ValueError('Cada fila debe tener cuatro campos')
            producto = validar(fila[0], fila[1], fila[2], fila[3])
            if buscar(productos, producto[0]) != -1:
                raise ValueError('Código duplicado en el archivo')
            productos.append(producto)
    return productos


def guardar(productos, ruta, modo='w'):
    # w escribe el archivo; with lo cierra al terminar.
    with open(ruta, modo, encoding='utf-8') as archivo:
        archivo.write(CABECERA + '\n')
        for p in productos:
            archivo.write(f'{p[0]};{p[1]};{p[2]};{p[3]:.2f}\n')


def registrar(productos, ruta, codigo, descripcion, cantidad, precio):
    nuevo = validar(codigo, descripcion, cantidad, precio)
    if buscar(productos, nuevo[0]) != -1:
        raise ValueError('Ya existe un producto con ese código')
    guardar(productos + [nuevo], ruta)
    productos.append(nuevo)


def actualizar(productos, ruta, codigo, descripcion, cantidad, precio):
    i = buscar(productos, codigo)
    if i == -1:
        raise ValueError('Producto no encontrado')
    nuevo = validar(codigo, descripcion, cantidad, precio)
    copia = productos.copy()
    copia[i] = nuevo
    guardar(copia, ruta)
    productos[i] = nuevo


def eliminar(productos, ruta, codigo):
    i = buscar(productos, codigo)
    if i == -1:
        raise ValueError('Producto no encontrado')
    copia = productos.copy()
    copia.pop(i)
    guardar(copia, ruta)
    productos.pop(i)


def importar(productos, ruta, origen):
    # Aceptar un nombre o una ruta pegada entre comillas.
    origen = str(origen).strip().strip('"').strip("'")
    lote = cargar(origen, permitir_ausente=False)
    for p in lote:
        if buscar(productos, p[0]) != -1:
            raise ValueError('El lote contiene códigos ya registrados')
    guardar(productos + lote, ruta)
    productos.extend(lote)
    return len(lote)


def exportar(productos, destino):
    destino = str(destino).strip() or 'catalogo_exportado.txt'
    if not destino.lower().endswith('.txt'):
        destino += '.txt'
    # x crea un archivo nuevo para no reemplazar uno que ya existe.
    guardar(productos, destino, modo='x')
    return destino


def resumen(productos):
    unidades = 0
    valor = 0.0
    sin_stock = 0
    for p in productos:
        unidades += p[2]
        valor += p[2] * p[3]
        if p[2] == 0:
            sin_stock += 1
    return len(productos), unidades, round(valor, 2), sin_stock


def mostrar(productos):
    if not productos:
        print('Catálogo vacío.')
    for p in productos:
        print(f'{p[0]} | {p[1]} | stock={p[2]} | S/ {p[3]:.2f}')


def limpiar_pantalla():
   
    print('\033[2J\033[H', end='', flush=True)


def main(ruta='catalogo.txt'):
    try:
        productos = cargar(ruta)
    except (ValueError, OSError, UnicodeError) as error:
        print('No se puede abrir el catálogo:', error)
        return
    while True:
        limpiar_pantalla()
        print(f'Catálogo cargado: {len(productos)} productos.')
        print('\n===== CATÁLOGO =====')
        print('1. Registrar producto')
        print('2. Buscar producto')
        print('3. Actualizar producto')
        print('4. Eliminar producto')
        print('5. Listar productos')
        print('6. Ver resumen')
        print('7. Importar lote desde TXT')
        print('8. Exportar productos a TXT')
        print('0. Salir')
        print('====================\n')
        try:
            opcion = input('Opción: ').strip()
            if opcion == '0':
                print('Sesión finalizada. Los cambios confirmados están guardados')
                break
            if opcion == '1' or opcion == '3':
                codigo = input('Código: ')
                descripcion = input('Descripción: ')
                cantidad = input('Cantidad: ')
                precio = input('Precio: ')
                if opcion == '1':
                    registrar(productos, ruta, codigo, descripcion, cantidad, precio)
                    print('Producto registrado y guardado.')
                else:
                    actualizar(productos, ruta, codigo, descripcion, cantidad, precio)
                    print('Producto actualizado y guardado.')
            elif opcion == '2':
                i = buscar(productos, input('Código: '))
                if i == -1:
                    print('Producto no encontrado.')
                else:
                    mostrar([productos[i]])
            elif opcion == '4':
                print('\nProductos disponibles para eliminar:')
                mostrar(productos)
                if productos:
                    codigo = input('\nCódigo a eliminar: ').strip()
                    if buscar(productos, codigo) == -1:
                        print('Producto no encontrado.')
                    elif input('Escriba SI para confirmar: ').strip().upper() == 'SI':
                        eliminar(productos, ruta, codigo)
                        print('Producto eliminado y guardado.')
                    else:
                        print('Eliminación cancelada.')
            elif opcion == '5':
                mostrar(productos)
            elif opcion == '6':
                n, unidades, valor, agotados = resumen(productos)
                print(f'Productos: {n} | Unidades: {unidades}')
                print(f'Valor a precio de venta: S/ {valor:.2f} | Sin stock: {agotados}')
            elif opcion == '7':
                origen = input('Nombre o ruta completa del archivo TXT: ').strip()
                n = importar(productos, ruta, origen)
                print(f'Lote importado y guardado: {n} productos')
            elif opcion == '8':
                destino = input('Nombre del TXT [catalogo_exportado.txt]: ')
                nombre = exportar(productos, destino)
                print(f'{len(productos)} productos exportados a {nombre}')
            else:
                print('Opción inválida; seleccione de 0 a 8.')
        # Si un dato o archivo tiene un error, avisar y volver al menú.
        except FileNotFoundError:
            print('Archivo no encontrado.')
        except (ValueError, OSError, UnicodeError) as error:
            print('Operación rechazada:', error)
        except (EOFError, KeyboardInterrupt):
            print('\nSesión interrumpida; los cambios confirmados están guardados')
            break
        try:
            input('\nPresiona Enter para volver al menú...')
        except (EOFError, KeyboardInterrupt):
            print('\nSesión finalizada. Los cambios confirmados están guardados')
            break


if __name__ == '__main__':
    main()

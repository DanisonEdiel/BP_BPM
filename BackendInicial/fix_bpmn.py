import xml.etree.ElementTree as ET
import os

# Ruta al archivo BPMN (usando ruta absoluta para evitar problemas)
bpmn_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Resources', 'GestionReembo.bpmn')
print(f"Buscando archivo BPMN en: {bpmn_file}")

# Registrar los namespaces
ET.register_namespace('', "http://www.omg.org/spec/BPMN/20100524/MODEL")
ET.register_namespace('bpmndi', "http://www.omg.org/spec/BPMN/20100524/DI")
ET.register_namespace('dc', "http://www.omg.org/spec/DD/20100524/DC")
ET.register_namespace('di', "http://www.omg.org/spec/DD/20100524/DI")
ET.register_namespace('zeebe', "http://camunda.org/schema/zeebe/1.0")
ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
ET.register_namespace('modeler', "http://camunda.org/schema/modeler/1.0")

# Verificar que el archivo existe
if not os.path.exists(bpmn_file):
    print(f"ERROR: El archivo BPMN no existe en la ruta: {bpmn_file}")
    # Buscar el archivo en el directorio actual y sus subdirectorios
    for root, dirs, files in os.walk(os.path.dirname(os.path.dirname(__file__))):
        for file in files:
            if file == 'GestionReembo.bpmn':
                print(f"Archivo BPMN encontrado en: {os.path.join(root, file)}")
                bpmn_file = os.path.join(root, file)
                break
    if not os.path.exists(bpmn_file):
        print("No se pudo encontrar el archivo BPMN. Saliendo.")
        exit(1)

# Cargar el archivo BPMN
print(f"Cargando archivo BPMN desde: {bpmn_file}")
tree = ET.parse(bpmn_file)
root = tree.getroot()

# Definir el namespace para zeebe
ns = {'zeebe': 'http://camunda.org/schema/zeebe/1.0'}

# Contador para llevar un registro de las correcciones
fixed_count = 0

# Buscar todas las tareas de servicio que usan el conector de correo electrónico
for task in root.findall('.//*[@zeebe:modelerTemplate="io.camunda.connectors.email.v1"]', ns):
    task_name = task.get('name', '')
    print(f"Procesando tarea: {task_name}")
    
    # Encontrar el elemento ioMapping
    io_mapping = task.find('.//zeebe:ioMapping', ns)
    if io_mapping is None:
        print(f"No se encontró ioMapping en {task_name}")
        continue
    
    # Buscar el input para htmlBody
    html_body_input = None
    for input_elem in io_mapping.findall('.//zeebe:input[@target="data.smtpAction.htmlBody"]', ns):
        html_body_input = input_elem
        break
    
    # Si no tiene source, agregar un HTML estático simple
    if html_body_input is not None and 'source' not in html_body_input.attrib:
        html_body_input.set('source', '"<h1>Notificación del Sistema</h1><p>Este es un mensaje automático del sistema de reembolsos.</p>"')
        fixed_count += 1
        print(f"  Corregido htmlBody en {task_name}")

# Guardar el archivo modificado
output_dir = os.path.dirname(bpmn_file)
output_file = os.path.join(output_dir, 'GestionReembo_fixed.bpmn')
print(f"Guardando archivo corregido en: {output_file}")
tree.write(output_file, encoding='UTF-8', xml_declaration=True)

# Corregir manualmente el problema de prefijos XML no declarados
with open(output_file, 'r', encoding='UTF-8') as file:
    content = file.read()

# Asegurarse de que el prefijo bpmn esté declarado en el elemento raíz
if 'xmlns:bpmn=' not in content:
    content = content.replace('<definitions ', '<definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" ')

# Guardar el archivo con los prefijos corregidos
with open(output_file, 'w', encoding='UTF-8') as file:
    file.write(content)

print(f"\nProceso completado. Se corrigieron {fixed_count} elementos.")
print(f"Archivo guardado como {output_file} con prefijos XML corregidos.")

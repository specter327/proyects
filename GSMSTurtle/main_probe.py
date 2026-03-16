# Library import
from src.controllers.transport_layers.ATEngine import ATEngine
from src.controllers.transport_layers.serial import TransportLayer
from src.contracts.properties.signal_level import SignalLevel
from src.contracts.operations.send_sms import SendSMS, SendSMSOperationParameters
from src.contracts.operations.receive_sms import ReceiveSMS, ReceiveSMSOperationParameters
from src.contracts.operations.delete_sms import DeleteSMS, DeleteSMSOperationParameters
from src.contracts.properties.query_imei import QueryIMEI
from src.contracts.properties.signal_level import SignalLevel
from src.controllers import PlatformLayer
from src.controllers.SIM800C.controller import Controller
from src.system.application_system.application_system import ApplicationSystem
import time
import threading
import os
from src.system.core.core import Core, utils
import json

def run_application_test():
    application = ApplicationSystem()
    application.start()

    print("System ports:")
    print(application.system_ports)

    time.sleep(5)

    print("Compatible devices:")
    print(application.compatible_devices)

    # Connect to device
    for device in application.compatible_devices:
        print("Compatible device:", device) # IDENTIFICATION

        controller_module = application.compatible_devices.get(device)
        controller = controller_module.controller()

        all_settings = controller.configurations.query_settings()
        for setting in all_settings:
            setting_properties = controller.configurations.query_setting(setting)
            print("Setting:")
            print(json.dumps(setting_properties.to_dict(), indent=4))
        
        controller.configurations.query_setting("COMMUNICATION_PORT").value.content = device.name
        controller.configurations.query_setting("BAUDRATE").value.content = 115200

        # Connect with the device
        device_identifier = application.connect(
            controller.configurations, 
            device, 
            controller_module
        )


    print("Controlled devices:")
    print(application.controlled_devices)

    # Send a SMS message
    print("Sending SMS message...")
    application.send_sms(
        device_identifier=device_identifier,
        destinatary="+525624545382",
        message=f"¡Hola! ¿Como te encuentras? [{int(round(time.time()))}]"
    )

    application.core.controlled_devices.get(device_identifier).get("DEVICE_CONTROLLER").ATEngine.send_at_command("AT+CMGD=1,4")

    #parameters = SendSMSOperationParameters("+525636600548", f"¡Hola! Prueba: {int(time.time())}")
    #print(application.core.request_operation(device_identifier, SendSMS, parameters).to_dict())

    #print("Update device information:")
    #application.update_device_information(device_identifier)
    #print("New controlled devices:")
    #print(application.controlled_devices)
    
    while True: time.sleep(10)
    
    time.sleep(30)
    application.stop()

def run_core_test():
    core = Core()
    core.start()

    print(utils.identify_controllers())
    # Identify all the available compatible devices
    print("Loaded controllers:")
    time.sleep(5)
    print(core.loaded_controllers)

    all_compatible_devices = core.auto_recognize_compatible_devices()
    time.sleep(10)

    # Connect to device
    for device in all_compatible_devices:
        print("Compatible device:", device.name)

        controller_module = all_compatible_devices.get(device)
        controller = controller_module.controller()

        all_settings = controller.configurations.query_settings()
        for setting in all_settings:
            setting_properties = controller.configurations.query_setting(setting)
            print("Setting:")
            print(json.dumps(setting_properties.to_dict(), indent=4))
        
        controller.configurations.query_setting("COMMUNICATION_PORT").value.content = device.name
        controller.configurations.query_setting("BAUDRATE").value.content = 115200

        # Connect with the device
        device_identifier = core.connect_device(controller.configurations, device, controller_module)
        print("Device identifier:", device_identifier)

        print("Connected devices:")
        print(core.controlled_devices)

        # Request a device property
        property = core.request_property(device_identifier, SignalLevel)


def run_operations_test():
    available_dev = Controller().recognize()[0]
    device = Controller()
    print("Using device:", available_dev.name)

    device.configurations.query_setting("COMMUNICATION_PORT").value.content = available_dev.name
    device.configurations.query_setting("BAUDRATE").value.content = 115200

    device.connect()
    print(device.request_property(SignalLevel).to_dict())
    
    #parameters = SendSMSOperationParameters("+525623707153", f"¡Hola! Prueba: {int(time.time())}")
    #print(device.request_operation(SendSMS, parameters).to_dict())

    parameters = ReceiveSMSOperationParameters()

    # Get the IMEI code
    imei = device.request_property(QueryIMEI)
    print(imei.to_dict())
    return None
    new_messages = device.request_operation(ReceiveSMS, parameters).messages
    current_readed_messages = []
    for message in new_messages:
        print("New message:")
        print("    Type:", message.type.content)
        print("    Timestamp:", message.timestamp.content)
        print("    Content:", message.content.content)
        print("    Sender:", message.sender.content)
        print("    Metadata:")
        print("        SIM_INDEX:", message.metadata.sim_index)
        print("        SIM_STATUS:", message.metadata.sim_status)
        print("        NETWORK_TIMESTAMP:", message.metadata.network_timestamp)
        print("        RAW_HEADER:", message.metadata.raw_header)
        current_readed_messages.append(message)
    
    print("Deleting readed messages...")
    for message in current_readed_messages:
        print("Deleting:")
        print("    SIM_INDEX:", message.metadata.sim_index)
        print("    Content:", message.content.content)

        parameters = DeleteSMSOperationParameters(
            sim_index=message.metadata.sim_index
        )

        operation_results = device.request_operation(DeleteSMS, parameters)

        print("Results:", operation_results.to_dict())


    device.disconnect()

def run_stress_test():
    # 1. Inicialización de componentes
    available_dev = Controller().recognize()[0]
    print("Probed device:")
    print(available_dev)

    transport = TransportLayer(
        device_port=available_dev.name,
        baudrate=115200,
        timeout=10
    )
    transport.connect()
    engine = ATEngine(transport)
    engine.start()

    print("[TEST] Iniciando secuencia de comandos síncronos con ruido asíncrono...\n")

    # 2. Simulación de ráfagas URC en hilos paralelos (Inyectores de Ruido)
    # 3. Secuencia de Comandos Síncronos (Lógica bloqueante del usuario)
    commands = [
        "AT",
        "AT+CSQ",
        "AT+CMGF=1",
        'AT+CPMS="SM","SM","SM"',
        "AT+CBC"
    ]

    for cmd in commands:
        print("Command:", cmd)
        engine.send_at_command(cmd)
        print("Response:")
        print(engine.read_at_response().compact())
        # Mark all the responses as read
        engine.mark_all_responses()

        # En una implementación real, aquí llamarías a engine.read_at_response() bloqueante
        time.sleep(1.2) # Tiempo de espera para que las rutinas procesen

    # 4. Verificación de Resultados
    print("\n" + "="*30)
    print("REPORTE FINAL DE DISECCIÓN")
    print("="*30)

    # Procesar Respuestas (Flujo Síncrono)
    time.sleep(30)
    print(f"\nRespuestas Capturadas ({engine.responses_counter}):")
    for i in range(engine.responses_counter):
        res = engine.responses.get(i)
        print(f"  [{i}] TS: {res.timestamp} | Data: {res.content}")

    # Procesar Eventos (Flujo Asíncrono / URC)
    print(f"\nEventos URC Capturados ({engine.events_counter}):")
    for i in range(engine.events_counter):
        event = engine.events.get(i)
        print(f"  [{i}] TS: {event.timestamp} | Evento: {event.content}")

    # 5. Auditoría de Salud del Motor
    print("\n" + "="*30)
    if not engine._read_lines_buffer and not engine._read_bytes_buffer:
        print("ESTADO: OK - Buffers limpios, datos procesados al 100%.")
    else:
        print(f"ESTADO: ALERTA - Residuos en buffer: {engine._read_lines_buffer}")

    #print("Sending ATI...", engine.send_at_command("ATI"))
    #engine.mark_all_responses()
    #print("Response:", engine.read_at_response().content)
    
    engine.stop()
    print("Test finalizado.")

if __name__ == "__main__":
    
    run_application_test()
    #run_core_test()

    #available_devices = PlatformLayer().identify_system_ports()
    #print("System ports:")
    #print(available_devices)
    #compatible_devices = Controller().recognize()
    #print("Compatible devices:")
    #print(compatible_devices)
    
    #run_operations_test()
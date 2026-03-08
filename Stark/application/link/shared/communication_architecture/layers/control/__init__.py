# Labels
__RESOURCE_TYPE__ = "STRUCTURAL"

# Library import
from .. import LayerInterface, LayerContainer, ModuleInterface, ModuleContainer, LAYER_TYPE_STRUCTURAL
from ....utils.logger import logger
from ....utils.debug import smart_debug
from configurations import Configurations, Setting
from . import modules
from typing import Optional, List, Dict
from abc import ABC, abstractmethod

# Classes definition
class ControlLayer(LayerInterface):
	# Class properties definition
	LAYER_NAME: str = "CONTROL"
	LAYER_TYPE = LAYER_TYPE_STRUCTURAL

	def __init__(self, layers_container: object) -> None:
		# Constructor hereditance
		super().__init__(layers_container)

		# Instance properties definition
		self._module_container = ModuleContainer()
		self.loaded_modules: Dict[str, ModuleInterface] = {}
		self.configurations: Optional[object] = None
		self.logger = logger("CONTROL_LAYER")
		print("Control layer instantiated")

	@property
	def NAME(self) -> str:
		return self.LAYER_NAME

	# Public methods
	@smart_debug(element_name="CONTROL_LAYER", include_args=True, include_result=True)
	def query_modules(self) -> List[str]:
		return self._module_container.query_modules()

	@smart_debug(element_name="CONTROL_LAYER", include_args=True, include_result=True)
	def query_module(self, module_name: str) -> ModuleInterface | None:
		return self._module_container.query_module(module_name)

	@smart_debug(element_name="CONTROL_LAYER", include_args=True, include_result=True)
	def configure(self, configurations: object) -> bool:
		self.configurations = configurations
		self.logger.info("Control layer configurated")
		return True

	@smart_debug(element_name="CONTROL_LAYER", include_args=True, include_result=True)
	def load_module(self, module_name: str, configurations: object = None) -> bool:
		self.logger.info(f"Loading communication module: {module_name}")
		module_class = self.query_module(module_name)
		if not module_class:
			self.logger.error(f"Module {module_name} not found in container")
			print(f"Module: {module_name} not found in container")
			return False
            
		try:
			module_instance = module_class(self)
			print(f"Module instance created: {module_name}")
			if configurations:
				module_instance.configure(configurations)
				print(f"Module configurated: {module_name}")
			start_result = module_instance.start()
			if start_result:
				print(f"Module started: {module_name}")
			else:
				print(f"Module not started: {module_name}")
			
			self.loaded_modules[module_name] = module_instance
			self.logger.info(f"Module {module_name} loaded and started successfully")
			return True
		except Exception as e:
			print(f"Exception:")
			print(e)
			self.logger.error(f"Error loading module {module_name}: {str(e)}")
			return False

	@smart_debug(element_name="CONTROL_LAYER", include_args=True, include_result=True)
	def load_modules(self) -> bool:
		#self.logger.info(f"Modules discovered: {self.query_modules()}")
		#print(f"Modules discovered: {self.query_modules()}")
		self.logger.info("Loading available modules")
		self._module_container.load_modules(package=modules.__package__)
		print(f"Modules discovered: {self.query_modules()}")

		for module_name in self.query_modules():
			self.logger.info(f"Instanciating module: {module_name}")
			print(f"Instanciating module: {module_name}")
			module_instance = self.query_module(module_name)
			module_configurations = module_instance.CONFIGURATIONS.copy()
			print(f"Configurating module: {module_name}")

			print(f"Loading module: {module_name}")
			self.load_module(module_name, module_configurations)
			self.logger.info(f"Module: {module_name}, loaded successfully")

		self.logger.info("Modules loaded successfully")

		return True

	@smart_debug(element_name="CONTROL_LAYER", include_args=True, include_result=True)
	def start(self) -> bool:
		self.logger.info("Starting Control layer")
		#self._module_container.load_modules(package=modules.__package__)
		#self.logger.info(f"Loaded modules: {self._module_container.query_layers()}")
		self.logger.info("Loading control modules")
		self.load_modules()
		self.logger.info("Control modules loaded")

		self.logger.info("Control layer initializated successfully")
		print("Control layer started successfully")

		return True

	@smart_debug(element_name="CONTROL_LAYER", include_args=True, include_result=True)
	def stop(self) -> bool:
		self.logger.info("Stopping Control layer")
		pass
		self.logger.info("Control layer successfully stopped")
		return True

class ControlModule(ModuleInterface, ABC):
	# Class properties definition
	CONFIGURATIONS: Optional[Configurations] = Configurations()

	def __init__(self, layer: object) -> None:
		# Constructor hereditance
		super().__init__(layer)